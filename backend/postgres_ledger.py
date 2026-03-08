
import logging
import json
import hashlib
from datetime import datetime, date
from uuid import uuid4
from sqlalchemy import Column, String, DateTime, text, Index
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.sql import select, desc
import os
from dotenv import load_dotenv

load_dotenv()

# Setup logging
logger = logging.getLogger(__name__)

# Base for SQLAlchemy models
Base = declarative_base()

class LedgerTransaction(Base):
    __tablename__ = 'ledger_transactions'

    id = Column(String, primary_key=True, default=lambda: str(uuid4()))
    table_name = Column(String, nullable=False, index=True)
    document_id = Column(String, nullable=False, index=True) # ID of the document itself
    data = Column(JSONB, nullable=False)
    tx_metadata = Column(JSONB, nullable=True) # Renamed from metadata
    hash = Column(String, nullable=False)
    previous_hash = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    __table_args__ = (
        Index('idx_table_document', 'table_name', 'document_id'),
    )

def json_serial(obj):
    """JSON serializer for objects not serializable by default json code"""
    if isinstance(obj, (datetime, date)):
        return obj.isoformat()
    raise TypeError(f"Type {type(obj)} not serializable")

def prepare_for_json(data):
    """Recursively convert datetime objects to strings for JSONB storage"""
    if isinstance(data, dict):
        return {k: prepare_for_json(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [prepare_for_json(v) for v in data]
    elif isinstance(data, (datetime, date)):
        return data.isoformat()
    return data

class PostgresLedgerDriver:
    def __init__(self, connection_string=None):
        self.connection_string = connection_string or os.getenv("POSTGRES_URL")
        self.engine = None
        self.async_session = None
        if not self.connection_string:
            logger.warning("POSTGRES_URL not set for PostgresLedgerDriver — all ledger operations will be no-ops")
            return

        self.engine = create_async_engine(self.connection_string, echo=False)
        self.async_session = sessionmaker(
            self.engine, class_=AsyncSession, expire_on_commit=False
        )

    async def initialize_table(self):
        """Creates the ledger table if it doesn't exist"""
        if not self.engine:
            logger.warning("PostgresLedgerDriver: no engine configured, skipping table init")
            return
        try:
            async with self.engine.begin() as conn:
                await conn.run_sync(Base.metadata.create_all)
            logger.info("PostgreSQL Ledger table initialized")
        except Exception as e:
            logger.error(f"Failed to initialize table: {repr(e)}")
            # Don't raise here to allow app to start even if DB is flaky, 
            # but for this specific "fix network" flow, we want to know.
            # raise e 

    def _calculate_hash(self, data, previous_hash, metadata):
        """Calculates SHA-256 hash of the record to ensure immutability"""
        # Ensure data is JSON serializable first
        clean_data = prepare_for_json(data)
        clean_metadata = prepare_for_json(metadata) if metadata else None
        
        payload = {
            "data": clean_data,
            "previous_hash": previous_hash,
            "metadata": clean_metadata
        }
        # Sort keys for consistent hashing
        payload_str = json.dumps(payload, sort_keys=True, default=json_serial)
        return hashlib.sha256(payload_str.encode()).hexdigest()

    async def insert_document(self, table_name: str, document: dict, metadata: dict = None):
        """
        Inserts a document into the ledger.
        """
        if not self.async_session:
            logger.warning("PostgresLedgerDriver: no session, skipping insert_document")
            return None
        if 'id' not in document:
            document['id'] = str(uuid4())
        
        doc_id = document['id']
        
        # Clean data for JSONB storage
        clean_doc = prepare_for_json(document)
        clean_metadata = prepare_for_json(metadata) if metadata else None

        async with self.async_session() as session:
            async with session.begin():
                # 1. Get the last hash for this table (to chain it)
                stmt = select(LedgerTransaction.hash).where(
                    LedgerTransaction.table_name == table_name
                ).order_by(desc(LedgerTransaction.created_at)).limit(1)
                
                result = await session.execute(stmt)
                last_hash_row = result.first()
                previous_hash = last_hash_row[0] if last_hash_row else None

                # 2. Calculate new hash
                new_hash = self._calculate_hash(clean_doc, previous_hash, clean_metadata)

                # 3. Create record
                new_record = LedgerTransaction(
                    table_name=table_name,
                    document_id=doc_id,
                    data=clean_doc,
                    tx_metadata=clean_metadata,
                    hash=new_hash,
                    previous_hash=previous_hash
                )
                
                session.add(new_record)
                await session.flush()
                
                logger.info(f"Ledger Insert: {table_name} - {doc_id} - Hash: {new_hash[:8]}...")
                return {"documentId": doc_id, "transactionId": new_record.id}

    async def get_document(self, table_name: str, document_id: str):
        """Retrieves the latest version of a document"""
        if not self.async_session:
            return None
        async with self.async_session() as session:
            stmt = select(LedgerTransaction).where(
                LedgerTransaction.table_name == table_name,
                LedgerTransaction.document_id == document_id
            ).order_by(desc(LedgerTransaction.created_at)).limit(1)
            
            result = await session.execute(stmt)
            record = result.scalars().first()
            
            if record:
                return record.data
            return None

    async def get_history(self, table_name: str, document_id: str):
        """Retrieves history of a document"""
        if not self.async_session:
            return []
        async with self.async_session() as session:
            stmt = select(LedgerTransaction).where(
                LedgerTransaction.table_name == table_name,
                LedgerTransaction.document_id == document_id
            ).order_by(desc(LedgerTransaction.created_at))
            
            result = await session.execute(stmt)
            records = result.scalars().all()
            
            return [{
                "data": r.data,
                "metadata": r.tx_metadata,
                "hash": r.hash,
                "created_at": r.created_at,
                "tx_id": r.id
            } for r in records]

    async def execute_query(self, query: str):
        """
        Simulates PartiQL execution by mapping to simple SQL queries if possible.
        """
        if not self.async_session:
            return []
        query_upper = query.strip().upper()
        
        async with self.async_session() as session:
             if query_upper.startswith("SELECT"):
                 parts = query.split()
                 if "FROM" in parts:
                     from_index = parts.index("FROM")
                     if from_index + 1 < len(parts):
                         table_name = parts[from_index + 1]
                         
                         # Basic Select: fetch all for table
                         stmt = select(LedgerTransaction).where(LedgerTransaction.table_name == table_name)
                         result = await session.execute(stmt)
                         rows = result.scalars().all()
                         
                         # Improve: Deduplicate in python for now
                         latest_docs = {}
                         for row in rows:
                             if row.document_id not in latest_docs:
                                 latest_docs[row.document_id] = row
                             else:
                                 if row.created_at > latest_docs[row.document_id].created_at:
                                     latest_docs[row.document_id] = row
                                     
                         return [r.data for r in latest_docs.values()]
                         
             return []

postgres_ledger = PostgresLedgerDriver()

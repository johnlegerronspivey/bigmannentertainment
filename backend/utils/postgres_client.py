
import logging
import json
import os
from datetime import datetime, date
from uuid import uuid4
from sqlalchemy import Column, String, DateTime, Integer, text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.sql import select, desc
from dotenv import load_dotenv

load_dotenv()

# Setup logging
logger = logging.getLogger(__name__)

# Base for SQLAlchemy models
Base = declarative_base()

class DisputeTable(Base):
    __tablename__ = 'disputes'

    id = Column(String, primary_key=True)
    dispute_number = Column(String, index=True)
    status = Column(String, index=True)
    priority = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow)
    # Store the full complex object as JSONB for flexibility
    document = Column(JSONB, nullable=False)

class AuditTable(Base):
    __tablename__ = 'audit_trail'

    id = Column(String, primary_key=True)
    entity_id = Column(String, index=True)
    event_type = Column(String, index=True)
    actor_id = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    document = Column(JSONB, nullable=False)

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

class PostgresClient:
    def __init__(self, connection_string=None):
        self.connection_string = connection_string or os.getenv("POSTGRES_URL")
        self.engine = None
        self.async_session = None
        if not self.connection_string:
            logger.warning("POSTGRES_URL not set for PostgresClient — all PG operations will be no-ops")
            return

        self.engine = create_async_engine(self.connection_string, echo=False)
        self.async_session = sessionmaker(
            self.engine, class_=AsyncSession, expire_on_commit=False
        )

    async def initialize_tables(self):
        """Creates standard tables if they don't exist"""
        if not self.engine:
            logger.warning("PostgresClient: no engine configured, skipping table init")
            return
        try:
            async with self.engine.begin() as conn:
                await conn.run_sync(Base.metadata.create_all)
            logger.info("PostgreSQL Standard Tables initialized")
        except Exception as e:
            logger.error(f"Failed to initialize tables: {repr(e)}")

    # --- Dispute Operations ---

    async def create_dispute(self, dispute_data: dict):
        if not self.async_session:
            logger.warning("PostgresClient: no session, skipping create_dispute")
            return None
        clean_doc = prepare_for_json(dispute_data)
        doc_id = clean_doc.get('id') or str(uuid4())
        
        async with self.async_session() as session:
            async with session.begin():
                new_dispute = DisputeTable(
                    id=doc_id,
                    dispute_number=clean_doc.get('dispute_number'),
                    status=clean_doc.get('status'),
                    priority=clean_doc.get('priority'),
                    created_at=datetime.fromisoformat(clean_doc.get('created_at')) if clean_doc.get('created_at') else datetime.utcnow(),
                    document=clean_doc
                )
                session.add(new_dispute)
            
            logger.info(f"Dispute Created: {doc_id}")
            return new_dispute

    async def get_dispute(self, dispute_id: str):
        if not self.async_session:
            return None
        async with self.async_session() as session:
            # Try by ID
            stmt = select(DisputeTable).where(DisputeTable.id == dispute_id)
            result = await session.execute(stmt)
            record = result.scalars().first()
            
            if not record:
                # Try by dispute number
                stmt = select(DisputeTable).where(DisputeTable.dispute_number == dispute_id)
                result = await session.execute(stmt)
                record = result.scalars().first()
                
            return record.document if record else None

    async def get_all_disputes(self, limit=50, offset=0):
        if not self.async_session:
            return []
        async with self.async_session() as session:
            stmt = select(DisputeTable).order_by(desc(DisputeTable.created_at)).limit(limit).offset(offset)
            result = await session.execute(stmt)
            records = result.scalars().all()
            return [r.document for r in records]

    async def update_dispute(self, dispute_id: str, update_data: dict):
        if not self.async_session:
            return None
        clean_update = prepare_for_json(update_data)
        
        async with self.async_session() as session:
            async with session.begin():
                stmt = select(DisputeTable).where(DisputeTable.id == dispute_id)
                result = await session.execute(stmt)
                record = result.scalars().first()
                
                if not record:
                    return None
                
                # Merge updates into document
                current_doc = dict(record.document)
                current_doc.update(clean_update)
                
                # Update columns
                record.document = current_doc
                if 'status' in clean_update:
                    record.status = clean_update['status']
                if 'priority' in clean_update:
                    record.priority = clean_update['priority']
                record.updated_at = datetime.utcnow()
                
                return current_doc

    # --- Audit Operations ---

    async def create_audit_entry(self, entry_data: dict):
        if not self.async_session:
            return None
        clean_doc = prepare_for_json(entry_data)
        entry_id = clean_doc.get('id') or str(uuid4())
        
        async with self.async_session() as session:
            async with session.begin():
                new_entry = AuditTable(
                    id=entry_id,
                    entity_id=clean_doc.get('entity_id'),
                    event_type=clean_doc.get('event_type'),
                    actor_id=clean_doc.get('actor_id'),
                    created_at=datetime.utcnow(),
                    document=clean_doc
                )
                session.add(new_entry)
                
        return new_entry

    async def get_audit_trail(self, limit=50, offset=0):
        if not self.async_session:
            return []
        async with self.async_session() as session:
            stmt = select(AuditTable).order_by(desc(AuditTable.created_at)).limit(limit).offset(offset)
            result = await session.execute(stmt)
            records = result.scalars().all()
            return [r.document for r in records]

# Singleton instance
postgres_client = PostgresClient()

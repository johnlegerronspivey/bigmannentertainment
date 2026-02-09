import logging
import json
import hashlib
from datetime import datetime
from uuid import uuid4
import os
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)

class EmergentLedgerDriver:
    def __init__(self, mongo_url=None, db_name=None):
        self.mongo_url = mongo_url or os.getenv("MONGO_URL", "mongodb://localhost:27017")
        self.db_name = db_name or os.getenv("DB_NAME", "bigmann_entertainment_production")
        
        try:
            self.client = AsyncIOMotorClient(self.mongo_url)
            self.db = self.client[self.db_name]
            self.collection = self.db['ledger_transactions']
            logger.info(f"Emergent Ledger connected to MongoDB: {self.db_name}")
        except Exception as e:
            logger.error(f"Failed to connect to MongoDB: {e}")

    async def initialize_table(self):
        """Creates indexes for the ledger"""
        try:
            await self.collection.create_index([("table_name", 1), ("document_id", 1)])
            await self.collection.create_index([("created_at", -1)])
            logger.info("Emergent Ledger indexes initialized")
        except Exception as e:
            logger.error(f"Failed to initialize indexes: {e}")

    def _calculate_hash(self, data, previous_hash, metadata):
        """Calculates SHA-256 hash of the record to ensure immutability"""
        payload = {
            "data": data,
            "previous_hash": previous_hash,
            "metadata": metadata
        }
        # Sort keys for consistent hashing
        payload_str = json.dumps(payload, sort_keys=True, default=str)
        return hashlib.sha256(payload_str.encode()).hexdigest()

    async def insert_document(self, table_name: str, document: dict, metadata: dict = None):
        """
        Inserts a document into the ledger.
        """
        if 'id' not in document:
            document['id'] = str(uuid4())
        
        doc_id = document['id']

        # 1. Get the last hash for this table (to chain it)
        last_record = await self.collection.find_one(
            {"table_name": table_name},
            sort=[("created_at", -1)]
        )
        previous_hash = last_record['hash'] if last_record else "GENESIS"

        # 2. Calculate new hash
        new_hash = self._calculate_hash(document, previous_hash, metadata)

        # 3. Create record
        new_record = {
            "id": str(uuid4()),
            "table_name": table_name,
            "document_id": doc_id,
            "data": document,
            "tx_metadata": metadata,
            "hash": new_hash,
            "previous_hash": previous_hash,
            "created_at": datetime.utcnow()
        }
        
        await self.collection.insert_one(new_record)
        
        logger.info(f"Ledger Insert: {table_name} - {doc_id} - Hash: {new_hash[:8]}...")
        return {"documentId": doc_id, "transactionId": new_record['id']}

    async def get_document(self, table_name: str, document_id: str):
        """Retrieves the latest version of a document"""
        record = await self.collection.find_one(
            {"table_name": table_name, "document_id": document_id},
            sort=[("created_at", -1)]
        )
        return record['data'] if record else None

    async def get_history(self, table_name: str, document_id: str):
        """Retrieves history of a document"""
        cursor = self.collection.find(
            {"table_name": table_name, "document_id": document_id}
        ).sort("created_at", -1)
        
        records = await cursor.to_list(length=1000)
        
        return [{
            "data": r['data'],
            "metadata": r.get('tx_metadata'),
            "hash": r['hash'],
            "created_at": r['created_at'],
            "tx_id": r['id']
        } for r in records]

    async def execute_query(self, query: str):
        """
        Simulates PartiQL execution by mapping to simple SQL-like queries.
        Supports: "SELECT * FROM TableName"
        """
        query_upper = query.strip().upper()
        
        if query_upper.startswith("SELECT"):
            parts = query.split()
            if "FROM" in parts:
                from_index = parts.index("FROM")
                if from_index + 1 < len(parts):
                    table_name = parts[from_index + 1]
                    
                    # Fetch all records for table
                    cursor = self.collection.find({"table_name": table_name})
                    records = await cursor.to_list(length=1000)
                    
                    # Deduplicate to get latest version per document_id
                    latest_docs = {}
                    for row in records:
                        doc_id = row['document_id']
                        if doc_id not in latest_docs:
                            latest_docs[doc_id] = row
                        else:
                            # If we found a newer one (shouldn't happen with raw find unless we sort)
                            # Actually, we didn't sort the main query.
                            if row['created_at'] > latest_docs[doc_id]['created_at']:
                                latest_docs[doc_id] = row
                                
                    return [r['data'] for r in latest_docs.values()]
                        
        return []

emergent_ledger = EmergentLedgerDriver()

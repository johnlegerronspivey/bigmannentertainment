"""
ULN Blockchain Ledger Service
==============================
Real cryptographic blockchain ledger for the Unified Label Network.
Implements SHA-256 hash chains, block mining, smart contract state management,
and chain integrity verification stored in MongoDB.
"""

import os
import hashlib
import json
import time
import logging
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
from motor.motor_asyncio import AsyncIOMotorClient
import uuid

MONGO_URL = os.environ.get('MONGO_URL')
DB_NAME = os.environ.get('DB_NAME')
client = AsyncIOMotorClient(MONGO_URL)
db = client[DB_NAME]

logger = logging.getLogger(__name__)

DIFFICULTY = 2  # Number of leading zeros required in block hash


class ULNBlockchainService:
    """Real cryptographic blockchain ledger backed by MongoDB."""

    def __init__(self):
        self.blocks = db.uln_blockchain_blocks
        self.transactions = db.uln_blockchain_transactions
        self.contracts = db.uln_smart_contracts_live
        self.chain_meta = db.uln_blockchain_meta

    # ───────────── Block operations ─────────────

    @staticmethod
    def _compute_hash(data: str) -> str:
        return hashlib.sha256(data.encode("utf-8")).hexdigest()

    def _mine_block(self, block_data: Dict[str, Any]) -> tuple:
        """Proof-of-work: find nonce so hash starts with DIFFICULTY zeros."""
        nonce = 0
        prefix = "0" * DIFFICULTY
        while True:
            block_data["nonce"] = nonce
            candidate = json.dumps(block_data, sort_keys=True, default=str)
            h = self._compute_hash(candidate)
            if h.startswith(prefix):
                return h, nonce
            nonce += 1

    async def _get_latest_block(self) -> Optional[Dict[str, Any]]:
        block = await self.blocks.find_one(
            {}, sort=[("index", -1)], projection={"_id": 0}
        )
        return block

    async def _ensure_genesis(self):
        """Create genesis block if chain is empty."""
        count = await self.blocks.count_documents({})
        if count > 0:
            return
        genesis_data = {
            "index": 0,
            "previous_hash": "0" * 64,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "transactions": [],
            "merkle_root": self._compute_hash("genesis"),
        }
        block_hash, nonce = self._mine_block(genesis_data)
        genesis_data["nonce"] = nonce
        genesis_data["hash"] = block_hash
        await self.blocks.insert_one(genesis_data)
        await self.chain_meta.update_one(
            {"key": "chain_info"},
            {"$set": {"total_blocks": 1, "total_transactions": 0, "created_at": datetime.now(timezone.utc).isoformat()}},
            upsert=True,
        )
        logger.info("Genesis block created")

    async def add_transaction(self, tx_type: str, payload: Dict[str, Any], actor_id: str) -> Dict[str, Any]:
        """Add a pending transaction to the mempool."""
        tx = {
            "tx_id": str(uuid.uuid4()),
            "tx_type": tx_type,
            "payload": payload,
            "actor_id": actor_id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "status": "pending",
            "tx_hash": self._compute_hash(json.dumps(payload, sort_keys=True, default=str) + actor_id + tx_type),
        }
        await self.transactions.insert_one({k: v for k, v in tx.items()})
        return {k: v for k, v in tx.items() if k != "_id"}

    async def mine_pending_block(self) -> Dict[str, Any]:
        """Mine all pending transactions into a new block."""
        await self._ensure_genesis()
        pending = await self.transactions.find({"status": "pending"}).to_list(length=100)
        if not pending:
            return {"success": False, "message": "No pending transactions to mine"}

        latest = await self._get_latest_block()
        tx_hashes = [t["tx_hash"] for t in pending]
        merkle = self._build_merkle_root(tx_hashes)

        block_data = {
            "index": latest["index"] + 1,
            "previous_hash": latest["hash"],
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "transactions": [t["tx_id"] for t in pending],
            "tx_count": len(pending),
            "merkle_root": merkle,
        }
        start = time.time()
        block_hash, nonce = self._mine_block(block_data)
        mining_time = round(time.time() - start, 4)
        block_data["nonce"] = nonce
        block_data["hash"] = block_hash
        block_data["mining_time_seconds"] = mining_time

        await self.blocks.insert_one(block_data)

        # Mark transactions as confirmed
        tx_ids = [t["tx_id"] for t in pending]
        await self.transactions.update_many(
            {"tx_id": {"$in": tx_ids}},
            {"$set": {"status": "confirmed", "block_index": block_data["index"], "block_hash": block_hash}},
        )
        await self.chain_meta.update_one(
            {"key": "chain_info"},
            {"$inc": {"total_blocks": 1, "total_transactions": len(tx_ids)}},
            upsert=True,
        )

        return {
            "success": True,
            "block_index": block_data["index"],
            "block_hash": block_hash,
            "transactions_mined": len(tx_ids),
            "mining_time_seconds": mining_time,
            "nonce": nonce,
            "merkle_root": merkle,
        }

    def _build_merkle_root(self, hashes: List[str]) -> str:
        if not hashes:
            return self._compute_hash("empty")
        while len(hashes) > 1:
            if len(hashes) % 2 == 1:
                hashes.append(hashes[-1])
            hashes = [self._compute_hash(hashes[i] + hashes[i + 1]) for i in range(0, len(hashes), 2)]
        return hashes[0]

    # ───────────── Chain verification ─────────────

    async def verify_chain(self) -> Dict[str, Any]:
        """Walk the entire chain and verify hash integrity."""
        await self._ensure_genesis()
        blocks = await self.blocks.find({}, projection={"_id": 0}).sort("index", 1).to_list(length=None)
        if not blocks:
            return {"valid": True, "blocks_checked": 0}

        invalid = []
        for i in range(1, len(blocks)):
            if blocks[i]["previous_hash"] != blocks[i - 1]["hash"]:
                invalid.append({"block_index": blocks[i]["index"], "error": "previous_hash mismatch"})

            # Re-verify proof-of-work
            verify_data = {
                "index": blocks[i]["index"],
                "previous_hash": blocks[i]["previous_hash"],
                "timestamp": blocks[i]["timestamp"],
                "transactions": blocks[i]["transactions"],
                "tx_count": blocks[i].get("tx_count", len(blocks[i]["transactions"])),
                "merkle_root": blocks[i]["merkle_root"],
                "nonce": blocks[i]["nonce"],
            }
            expected = self._compute_hash(json.dumps(verify_data, sort_keys=True, default=str))
            if expected != blocks[i]["hash"]:
                invalid.append({"block_index": blocks[i]["index"], "error": "hash recomputation mismatch"})

        return {
            "valid": len(invalid) == 0,
            "blocks_checked": len(blocks),
            "invalid_blocks": invalid,
        }

    # ───────────── Smart contracts ─────────────

    async def deploy_contract(self, contract_type: str, label_id: str, params: Dict[str, Any], deployer_id: str) -> Dict[str, Any]:
        """Deploy a smart contract and record it on-chain."""
        contract_id = f"SC-{uuid.uuid4().hex[:12].upper()}"
        address = f"0x{uuid.uuid4().hex[:40]}"
        contract = {
            "contract_id": contract_id,
            "contract_address": address,
            "contract_type": contract_type,
            "label_id": label_id,
            "parameters": params,
            "state": params.get("initial_state", {}),
            "deployer_id": deployer_id,
            "status": "active",
            "deployed_at": datetime.now(timezone.utc).isoformat(),
            "executions": 0,
        }
        await self.contracts.insert_one(contract)
        # Record deployment tx
        await self.add_transaction("contract_deploy", {
            "contract_id": contract_id,
            "contract_address": address,
            "contract_type": contract_type,
            "label_id": label_id,
        }, deployer_id)
        contract.pop("_id", None)
        return {"success": True, "contract": contract}

    async def execute_contract(self, contract_id: str, action: str, params: Dict[str, Any], executor_id: str) -> Dict[str, Any]:
        """Execute an action on a deployed smart contract."""
        contract = await self.contracts.find_one({"contract_id": contract_id}, projection={"_id": 0})
        if not contract:
            return {"success": False, "error": "Contract not found"}
        if contract["status"] != "active":
            return {"success": False, "error": f"Contract is {contract['status']}"}

        # Apply state transition
        state = contract.get("state", {})
        if action == "update_splits":
            state["rights_splits"] = params.get("splits", state.get("rights_splits", {}))
        elif action == "distribute_royalty":
            dist = state.get("distributions", [])
            dist.append({"amount": params.get("amount", 0), "timestamp": datetime.now(timezone.utc).isoformat(), "recipients": params.get("recipients", [])})
            state["distributions"] = dist
        elif action == "toggle_dao":
            state["dao_enabled"] = params.get("enabled", True)
        else:
            state[action] = params

        await self.contracts.update_one(
            {"contract_id": contract_id},
            {"$set": {"state": state}, "$inc": {"executions": 1}},
        )
        await self.add_transaction("contract_execute", {
            "contract_id": contract_id,
            "action": action,
            "params": params,
        }, executor_id)

        return {"success": True, "contract_id": contract_id, "action": action, "new_state": state}

    async def get_contracts(self, label_id: Optional[str] = None) -> List[Dict[str, Any]]:
        query = {"label_id": label_id} if label_id else {}
        contracts = await self.contracts.find(query, projection={"_id": 0}).to_list(length=100)
        return contracts

    # ───────────── Chain explorer ─────────────

    async def get_blocks(self, limit: int = 20, offset: int = 0) -> Dict[str, Any]:
        await self._ensure_genesis()
        total = await self.blocks.count_documents({})
        blocks = await self.blocks.find({}, projection={"_id": 0}).sort("index", -1).skip(offset).limit(limit).to_list(length=limit)
        return {"blocks": blocks, "total": total}

    async def get_block(self, index: int) -> Optional[Dict[str, Any]]:
        return await self.blocks.find_one({"index": index}, projection={"_id": 0})

    async def get_transactions(self, status: Optional[str] = None, limit: int = 50) -> List[Dict[str, Any]]:
        query = {"status": status} if status else {}
        return await self.transactions.find(query, projection={"_id": 0}).sort("timestamp", -1).limit(limit).to_list(length=limit)

    async def get_chain_stats(self) -> Dict[str, Any]:
        await self._ensure_genesis()
        meta = await self.chain_meta.find_one({"key": "chain_info"}, projection={"_id": 0})
        pending = await self.transactions.count_documents({"status": "pending"})
        active_contracts = await self.contracts.count_documents({"status": "active"})
        latest = await self._get_latest_block()
        return {
            "total_blocks": meta.get("total_blocks", 1) if meta else 1,
            "total_transactions": meta.get("total_transactions", 0) if meta else 0,
            "pending_transactions": pending,
            "active_contracts": active_contracts,
            "latest_block_hash": latest["hash"] if latest else None,
            "latest_block_index": latest["index"] if latest else 0,
            "difficulty": DIFFICULTY,
            "chain_created": meta.get("created_at") if meta else None,
        }

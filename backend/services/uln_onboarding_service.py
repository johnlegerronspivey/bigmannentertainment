"""
ULN Label Onboarding Service
==============================
Multi-step guided onboarding workflow for new labels joining the ULN.
Tracks progress through 5 steps: Basic Info, Business Details, Key Personnel,
Smart Contract Setup, and Review & Submit.
"""

import os
import logging
from datetime import datetime, timezone
from typing import Dict, Any, Optional
from motor.motor_asyncio import AsyncIOMotorClient
import uuid

MONGO_URL = os.environ.get('MONGO_URL')
DB_NAME = os.environ.get('DB_NAME')
client = AsyncIOMotorClient(MONGO_URL)
db = client[DB_NAME]
logger = logging.getLogger(__name__)

ONBOARDING_STEPS = [
    {"step": 1, "name": "basic_info", "title": "Basic Information", "fields": ["name", "label_type", "jurisdiction", "headquarters"]},
    {"step": 2, "name": "business_details", "title": "Business Details", "fields": ["legal_name", "tax_status", "business_registration_number", "tax_id", "founded_date"]},
    {"step": 3, "name": "key_personnel", "title": "Key Personnel", "fields": ["entities"]},
    {"step": 4, "name": "smart_contracts", "title": "Smart Contract Setup", "fields": ["contract_type", "rights_splits", "dao_integration"]},
    {"step": 5, "name": "review_submit", "title": "Review & Submit", "fields": []},
]


class ULNOnboardingService:
    def __init__(self):
        self.onboarding = db.uln_onboarding

    async def start_onboarding(self, user_id: str) -> Dict[str, Any]:
        """Start a new onboarding session."""
        session_id = str(uuid.uuid4())
        session = {
            "session_id": session_id,
            "user_id": user_id,
            "current_step": 1,
            "steps_completed": [],
            "data": {},
            "status": "in_progress",
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat(),
        }
        await self.onboarding.insert_one(session)
        return {
            "success": True,
            "session_id": session_id,
            "current_step": 1,
            "steps": ONBOARDING_STEPS,
        }

    async def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get current onboarding session."""
        session = await self.onboarding.find_one({"session_id": session_id}, projection={"_id": 0})
        if not session:
            return None
        session["steps"] = ONBOARDING_STEPS
        return session

    async def save_step(self, session_id: str, step: int, data: Dict[str, Any]) -> Dict[str, Any]:
        """Save data for a specific step and advance."""
        session = await self.onboarding.find_one({"session_id": session_id})
        if not session:
            return {"success": False, "error": "Session not found"}
        if session["status"] != "in_progress":
            return {"success": False, "error": "Onboarding already completed"}

        # Merge step data
        existing_data = session.get("data", {})
        step_key = f"step_{step}"
        existing_data[step_key] = data
        completed = session.get("steps_completed", [])
        if step not in completed:
            completed.append(step)

        next_step = min(step + 1, 5)
        await self.onboarding.update_one(
            {"session_id": session_id},
            {"$set": {
                "data": existing_data,
                "steps_completed": completed,
                "current_step": next_step,
                "updated_at": datetime.now(timezone.utc).isoformat(),
            }},
        )
        return {
            "success": True,
            "step_saved": step,
            "next_step": next_step,
            "steps_completed": completed,
        }

    async def complete_onboarding(self, session_id: str) -> Dict[str, Any]:
        """Mark onboarding as complete and return consolidated data for label registration."""
        session = await self.onboarding.find_one({"session_id": session_id}, projection={"_id": 0})
        if not session:
            return {"success": False, "error": "Session not found"}

        # Check all steps completed
        completed = set(session.get("steps_completed", []))
        required = {1, 2, 3, 4}
        if not required.issubset(completed):
            missing = required - completed
            return {"success": False, "error": f"Steps not completed: {list(missing)}"}

        data = session.get("data", {})
        # Build registration payload
        basic = data.get("step_1", {})
        business = data.get("step_2", {})
        personnel = data.get("step_3", {})
        contracts = data.get("step_4", {})

        registration = {
            "label_type": basic.get("label_type", "independent"),
            "integration_type": basic.get("integration_type", "api_partner"),
            "metadata_profile": {
                "name": basic.get("name", ""),
                "legal_name": business.get("legal_name", basic.get("name", "")),
                "jurisdiction": basic.get("jurisdiction", "US"),
                "tax_status": business.get("tax_status", "llc"),
                "headquarters": basic.get("headquarters", ""),
                "business_registration_number": business.get("business_registration_number", ""),
                "tax_id": business.get("tax_id", ""),
                "genre_specialization": basic.get("genres", []),
                "territories_of_operation": basic.get("territories", []),
            },
            "entities": personnel.get("entities", []),
            "smart_contract_config": contracts,
        }

        await self.onboarding.update_one(
            {"session_id": session_id},
            {"$set": {"status": "completed", "updated_at": datetime.now(timezone.utc).isoformat()}},
        )

        return {
            "success": True,
            "session_id": session_id,
            "status": "completed",
            "registration_payload": registration,
        }

    async def get_user_sessions(self, user_id: str) -> list:
        """Get all onboarding sessions for a user."""
        sessions = await self.onboarding.find(
            {"user_id": user_id}, projection={"_id": 0}
        ).sort("created_at", -1).to_list(length=20)
        return sessions

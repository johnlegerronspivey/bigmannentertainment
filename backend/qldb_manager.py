import os
import logging
from postgres_client import postgres_client

logger = logging.getLogger(__name__)

class QldbManager:
    """
    Adapter class to maintain compatibility with existing service structure
    but routed to standard PostgreSQL.
    """
    def __init__(self):
        self.client = postgres_client

    async def initialize(self):
        """Initialize the standard SQL tables"""
        await self.client.initialize_tables()

    # Expose the client as 'ledger' for minimal refactoring in service,
    # though conceptually it's just a DB client now.
    @property
    def ledger(self):
        return self.client

# Global instance
qldb_manager = QldbManager()

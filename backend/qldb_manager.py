import os
import logging
from postgres_ledger import postgres_ledger

logger = logging.getLogger(__name__)

class QldbManager:
    def __init__(self):
        self.ledger = postgres_ledger

    async def initialize(self):
        """Initialize the ledger tables"""
        await self.ledger.initialize_table()

    # We are deprecating execute_transaction in favor of direct async usage of self.ledger
    # But for backward compatibility if needed, we can keep a stub, 
    # though we plan to refactor the service to use self.ledger directly.
    
    def get_ledger(self):
        return self.ledger

# Global instance
qldb_manager = QldbManager()

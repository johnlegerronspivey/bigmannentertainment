import os
import logging
from emergent_ledger import emergent_ledger

logger = logging.getLogger(__name__)

class QldbManager:
    def __init__(self):
        self.ledger = emergent_ledger

    async def initialize(self):
        """Initialize the ledger tables"""
        await self.ledger.initialize_table()

    def get_ledger(self):
        return self.ledger

# Global instance
qldb_manager = QldbManager()

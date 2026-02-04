import os
import logging
from botocore.config import Config

logger = logging.getLogger(__name__)

class QldbManager:
    def __init__(self):
        self.driver = None
        self.ledger_name = os.getenv("QLDB_LEDGER_NAME", "dispute-ledger")
        self.region_name = os.getenv("AWS_REGION", "us-east-1")
        self.use_mock = True # Force mock due to environment constraints

    def initialize(self):
        """Initialize the QLDB driver"""
        if not self.driver:
            if self.use_mock:
                try:
                    from qldb_mock import MockQldbDriver
                    self.driver = MockQldbDriver(ledger_name=self.ledger_name)
                    logger.info(f"Initialized MOCK QLDB driver for ledger: {self.ledger_name}")
                except Exception as e:
                    logger.error(f"Failed to initialize Mock QLDB driver: {e}")
            else:
                try:
                    from pyqldb.driver.qldb_driver import QldbDriver
                    config = Config(
                        retries={'max_attempts': 3, 'mode': 'standard'},
                        connect_timeout=10,
                        read_timeout=10
                    )
                    self.driver = QldbDriver(
                        ledger_name=self.ledger_name,
                        region_name=self.region_name,
                        config=config
                    )
                    logger.info(f"Initialized QLDB driver for ledger: {self.ledger_name}")
                except Exception as e:
                    logger.error(f"Failed to initialize QLDB driver: {e}")

    def get_driver(self):
        if not self.driver:
            self.initialize()
        return self.driver

    def execute_transaction(self, transaction_lambda):
        """Execute a lambda function within a QLDB session"""
        driver = self.get_driver()
        if not driver:
            raise Exception("QLDB Driver not available")
        
        return driver.execute_lambda(transaction_lambda)

# Global instance
qldb_manager = QldbManager()

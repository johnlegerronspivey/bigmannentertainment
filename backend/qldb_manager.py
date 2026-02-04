import os
import logging
from pyqldb.driver.qldb_driver import QldbDriver
from botocore.config import Config

logger = logging.getLogger(__name__)

class QldbManager:
    def __init__(self):
        self.driver = None
        self.ledger_name = os.getenv("QLDB_LEDGER_NAME", "dispute-ledger")
        self.region_name = os.getenv("AWS_REGION", "us-east-1")

    def initialize(self):
        """Initialize the QLDB driver"""
        if not self.driver:
            try:
                # Retry config for better stability
                config = Config(
                    retries={'max_attempts': 3, 'mode': 'standard'},
                    connect_timeout=10,
                    read_timeout=10
                )
                self.driver = QldbDriver(
                    ledger_name=self.ledger_name,
                    region_name=self.region_name,
                    boto_config=config
                )
                logger.info(f"Initialized QLDB driver for ledger: {self.ledger_name}")
            except Exception as e:
                logger.error(f"Failed to initialize QLDB driver: {e}")
                # We don't raise here to allow the app to start, but QLDB ops will fail.

    def get_driver(self):
        if not self.driver:
            self.initialize()
        return self.driver

    def execute_transaction(self, transaction_lambda):
        """Execute a lambda function within a QLDB session"""
        driver = self.get_driver()
        if not driver:
            raise Exception("QLDB Driver not available")
        
        session = driver.get_session()
        try:
            return session.execute_lambda(transaction_lambda)
        finally:
            session.close()

# Global instance
qldb_manager = QldbManager()

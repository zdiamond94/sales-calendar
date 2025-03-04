import sys
import logging
from app import app

# Configure logging
logging.basicConfig(stream=sys.stdout, level=logging.INFO)
logger = logging.getLogger(__name__)

if __name__ == "__main__":
    try:
        logger.info("Starting application...")
        app.run()
    except Exception as e:
        logger.error(f"Failed to start application: {str(e)}")
        raise

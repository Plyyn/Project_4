import logging
from datetime import datetime
import os


def setup_logger():
    if not os.path.exists('logs'):
        os.makedirs('logs')

    current_time = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    log_file = f'logs/bot_{current_time}.log'

    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler()
        ]
    )

    logger = logging.getLogger(__name__)
    logger.info("Logger initialized")
    return logger
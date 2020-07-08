import logging
import sys
from logging.handlers import RotatingFileHandler

# Log to stdout
def get_logger(log_level):
    logger = logging.getLogger(__name__)
    logger.setLevel(log_level)
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s %(message)s'))
    logger.addHandler(handler) 
    return logger

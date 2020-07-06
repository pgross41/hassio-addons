import logging
import sys
from logging.handlers import RotatingFileHandler

# Rotating log flie with max size 1MB
def get_logger(log_level, filename):
    logger = logging.getLogger(__name__)
    handler = RotatingFileHandler(filename, mode='a', maxBytes=1024*1024, backupCount=1)
    handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s %(message)s'))
    logger.addHandler(handler) 
    logger.setLevel(log_level)
    return logger

# Logger exception handling
def init_exception_handler(logger):
    def handle_exception(exc_type, exc_value, exc_traceback):
        if issubclass(exc_type, KeyboardInterrupt):
            sys.__excepthook__(exc_type, exc_value, exc_traceback)
            return
        logger.critical("Uncaught exception", exc_info=(exc_type, exc_value, exc_traceback))
        raise exc_type, exc_value, exc_traceback
    sys.excepthook = handle_exception
import logging
# import logging.handlers
from logging.handlers import RotatingFileHandler
import os

logger = logging.getLogger("DOGFINDER-Logger")
logLevel = logging.getLevelName(os.getenv("LogLevel", "INFO"))
logger.setLevel(logLevel)
logger.propagate = 0

# set time zone to utc
# logging.Formatter.converter = time.gmtime
# create formatter to with miliseconds
fmt = logging.Formatter('[%(asctime)s.%(msecs)03d] [%(levelname)s] [%(module)s]: %(message)s', '%d/%m/%Y %H:%M:%S')

console = logging.StreamHandler()
console.setFormatter(fmt)
logger.addHandler(console)

if (os.path.exists(os.getenv("LOGGER_ROOT_PATH"))):
    # create folder if it doesn't exist
    logger_app_path = f"{os.getenv('LOGGER_ROOT_PATH')}/dogfinder"
    if not os.path.exists(logger_app_path):
        os.makedirs(logger_app_path)
    fileHandler = RotatingFileHandler(f"{logger_app_path}/dogfinder.log", maxBytes=10000000, backupCount=5)
    fileHandler.setFormatter(fmt)
    logger.addHandler(fileHandler)
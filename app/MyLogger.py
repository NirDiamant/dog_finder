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

if (os.path.exists("/var/log/")):
    # create folder if it doesn't exist
    if not os.path.exists("/var/log/dogfinder"):
        os.makedirs("/var/log/dogfinder")
    fileHandler = RotatingFileHandler('/var/log/dogfinder/dogfinder.log', maxBytes=10000000, backupCount=5)
    fileHandler.setFormatter(fmt)
    logger.addHandler(fileHandler)
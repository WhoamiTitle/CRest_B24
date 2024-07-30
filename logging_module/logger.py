import logging
from logging.handlers import RotatingFileHandler
from bitrix24_crest import settings

def setup_logger_json(name, filename, level=logging.DEBUG):
    formatter = logging.Formatter('%(message)s')
    handler = RotatingFileHandler(filename, maxBytes=10*1024*1024, backupCount=5, encoding='utf-8')
    handler.setFormatter(formatter)
    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.addHandler(handler)
    return logger

json_logger = setup_logger_json("json", settings.LOG_PATH)

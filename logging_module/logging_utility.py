import logging
from logging_module.logger import json_logger
from logging_module.schemes import LogMessage, log_en
import datetime

cmd_logger = logging.getLogger(__name__)

def log_info(message: LogMessage):
    cmd_logger.info(f"INFO: {message.heder}")
    cmd_logger.info(message.json())
    json_logger.info(message.json())

def log_error(message: LogMessage):
    cmd_logger.error(f"ERROR: {message.heder}")
    cmd_logger.error(message.json())
    json_logger.error(message.json())

def log_debug(message: LogMessage):
    cmd_logger.debug(f"DEBUG: {message.heder}")
    cmd_logger.debug(message.json())
    json_logger.debug(message.json())

log_switch = {
    log_en.INFO: log_info,
    log_en.ERROR: log_error,
    log_en.DEBUG: log_debug,
}

def log(message: LogMessage):
    message.time = datetime.datetime.now().isoformat()
    log_switch[message.level](message)

def filter_array_to_str(arr: list) -> list:
    return [item for item in arr if isinstance(item, str)]

def filter_dict_to_str(d: dict) -> dict:
    return {key: item for key, item in d.items() if isinstance(item, str)}
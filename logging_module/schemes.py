from pydantic import BaseModel
from enum import Enum
from typing import Any, Optional

class log_en(Enum):
    INFO = "info"
    ERROR = "error"
    DEBUG = "debug"

class LogMessage(BaseModel):
    time: Optional[str]
    level: log_en
    heder: str 
    heder_dict: Optional[Any]
    body: Optional[Any]

from datetime import datetime
from typing import Optional, Dict, Any
from pydantic import BaseModel
from enum import Enum

class LogLevel(str, Enum):
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    DEBUG = "DEBUG"

class LogType(str, Enum):
    HTTP_REQUEST = "HTTP_REQUEST"
    AUTHENTICATION = "AUTHENTICATION"
    BUSINESS_LOGIC = "BUSINESS_LOGIC"
    SYSTEM = "SYSTEM"

class LogDocument(BaseModel):

    timestamp: datetime
    level: LogLevel
    type: LogType
    source: str  
    
    user_id: Optional[int] = None
    user_role: Optional[str] = None
    correo: Optional[str] = None  
    
    action: Optional[str] = None  
    endpoint: Optional[str] = None
    method: Optional[str] = None
    
    status: Optional[str] = None 
    response_status: Optional[int] = None
    
    ip_address: Optional[str] = None
    duration_ms: Optional[float] = None
    
    message: Optional[str] = None
    error_message: Optional[str] = None
    
    metadata: Optional[Dict[str, Any]] = None
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
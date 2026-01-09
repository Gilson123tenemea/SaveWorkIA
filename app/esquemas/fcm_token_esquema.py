from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class FCMTokenRegistro(BaseModel):
    """Schema para registrar un nuevo token FCM"""
    token_fcm: str

class FCMTokenResponse(BaseModel):
    """Schema para la respuesta del servidor"""
    id_fcm_token: int
    id_inspector: int
    token_fcm: str
    fecha_registro: datetime

    class Config:
        orm_mode = True

class FCMTokenDelete(BaseModel):
    """Schema para eliminar un token"""
    token_fcm: str
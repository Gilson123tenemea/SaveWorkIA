from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean
from datetime import datetime
from app.config import Base

class FCMToken(Base):
    __tablename__ = "fcm_tokens"

    id_fcm_token = Column(Integer, primary_key=True, index=True)
    id_inspector = Column(Integer, ForeignKey("inspector.id_inspector"), nullable=False, index=True)
    token_fcm = Column(String(500), nullable=False, index=True)
    fecha_registro = Column(DateTime, default=datetime.utcnow, nullable=False)
    borrado = Column(Boolean, default=True)

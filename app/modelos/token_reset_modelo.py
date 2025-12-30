from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey
from datetime import datetime, timedelta
from app.config import Base

class TokenReset(Base):
    __tablename__ = "tokens_reset"

    id_token = Column(Integer, primary_key=True, index=True)
    id_persona = Column(Integer, ForeignKey("personas.id_persona"), nullable=False)
    token = Column(String(255), unique=True, index=True, nullable=False)
    correo = Column(String(150), nullable=False)
    fecha_creacion = Column(DateTime, default=datetime.utcnow, nullable=False)
    fecha_expiracion = Column(DateTime, nullable=False)
    usado = Column(Boolean, default=False)
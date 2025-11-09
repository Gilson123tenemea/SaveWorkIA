# app/modelos/camara_modelo.py
from sqlalchemy import Column, Integer, String, Boolean, Date, ForeignKey
from sqlalchemy.orm import relationship
from app.config import Base

class Camara(Base):
    __tablename__ = "camaras"

    id_camara = Column(Integer, primary_key=True, index=True)
    codigo = Column(String(10), unique=True, nullable=False, index=True)
    tipo = Column(String(100), nullable=False)
    estado = Column(String(100), nullable=False)
    ipAddress = Column(String(100), nullable=False)
    ultimaTransmision = Column(Date, nullable=True)
    ultima_revision = Column(Date, nullable=True)

    id_zona = Column(Integer, ForeignKey("zonas.id_Zona"), nullable=False)
    id_administrador = Column(Integer, ForeignKey("administrador.id_administrador"), nullable=False)
    borrado = Column(Boolean, default=True)

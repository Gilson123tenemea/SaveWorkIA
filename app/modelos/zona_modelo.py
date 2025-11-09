# app/modelos/zona_modelo.py
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from app.config import Base

class Zona(Base):
    __tablename__ = "zonas"

    id_Zona = Column(Integer, primary_key=True, index=True)
    nombreZona = Column(String(100), nullable=False)
    latitud = Column(String(100), nullable=False)
    longitud = Column(String(100), nullable=False)

    id_empresa_zona = Column(Integer, ForeignKey("empresas.id_Empresa"), nullable=False)
    id_administrador_zona = Column(Integer, ForeignKey("administrador.id_administrador"), nullable=False)
    borrado = Column(Boolean, default=True)

    
    
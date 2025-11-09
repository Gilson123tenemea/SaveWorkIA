# app/modelos/reporte.py
from sqlalchemy import Column, Integer, String, Date, ForeignKey, Boolean
from app.config import Base

class Reporte(Base):
    __tablename__ = "reportes"

    id_reporte = Column(Integer, primary_key=True, index=True)
    fecha = Column(Date, nullable=False)
    descripcion = Column(String(250), nullable=False)
    nivel_alerta = Column(String(100), nullable=False)
    estado = Column(String(50), nullable=False)
    brroado = Column(Boolean, default=True)

    id_empresa = Column(Integer, ForeignKey("empresas.id_Empresa"), nullable=False)
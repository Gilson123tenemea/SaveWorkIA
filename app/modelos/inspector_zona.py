# app/modelos/inspector_zona.py
from sqlalchemy import Column, Integer, Boolean, ForeignKey, DateTime, func
from app.config import Base

class InspectorZona(Base):
    __tablename__ = "inspector_zona"

    id_inspector_zona = Column(Integer, primary_key=True, index=True)
    fecha_asignacion = Column(DateTime, nullable=False, server_default=func.now())
    borrado = Column(Boolean, default=True)

    id_inspector_inspectorzona = Column(Integer, ForeignKey("inspector.id_inspector"), nullable=False)
    id_zona_inspectorzona = Column(Integer, ForeignKey("zonas.id_Zona"), nullable=False)
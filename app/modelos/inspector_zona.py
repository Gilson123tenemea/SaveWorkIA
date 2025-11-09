# app/modelos/inspector_zona.py
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, Date
from app.config import Base

class InspectorZona(Base):
    __tablename__ = "inspector_zona"

    id_inspector_zona = Column(Integer, primary_key=True, index=True)
    fecha_asignacion = Column(Date, nullable=False)
    borrado = Column(Boolean, default=True)

    id_inspector_inspectorzona = Column(Integer, ForeignKey("inspector.id_inspector"), nullable=False)
    id_zona_inspectorzona = Column(Integer, ForeignKey("zonas.id_Zona"), nullable=False)
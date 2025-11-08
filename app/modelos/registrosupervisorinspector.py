# app/model/registrosupervisorinspector.py
from sqlalchemy import Column, Integer, Boolean, Date, ForeignKey
from app.config import Base

class RegistroSupervisorInspector(Base):
    __tablename__ = "registro_supervisor_inspector"

    id_registrosupervisorins = Column(Integer, primary_key=True, index=True)
    fecha_asignacion = Column(Date, nullable=False)
    borrado = Column(Boolean, default=True)

    # Relaciones
    id_supervisor_registro = Column(Integer, nullable=False)
    id_supervisor_registro = Column(Integer, ForeignKey("supervisor.id_supervisor"),nullable=False)
    id_inspector_registro = Column(Integer, nullable=False)
    id_inspector_registro = Column(Integer, ForeignKey("inspector.id_inspector"), nullable=False)
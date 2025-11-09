# app/modelos/revision_reporte_modelo.py
from sqlalchemy import Column, Integer, String, Boolean, Date, ForeignKey
from sqlalchemy.orm import relationship
from app.config import Base

class RevisionReporte(Base):
    __tablename__ = "revision_reportes"

    id_revisionreporte = Column(Integer, primary_key=True, index=True)
    id_Supervisor = Column(Integer, ForeignKey("supervisor.id_supervisor"), nullable=False)
    id_reporte = Column(Integer, ForeignKey("reportes.id_reporte"), nullable=False)
    fecha_revision = Column(Date, nullable=False)
    observacion = Column(String(500), nullable=False)
    borrado = Column(Boolean, default=True)

   
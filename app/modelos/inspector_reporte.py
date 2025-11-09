from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, Date
from app.config import Base

class Inspectorreporte(Base):
    __tablename__ = "inspector_reportes"

    id_inspector_reporte = Column(Integer, primary_key=True, index=True)
    fecha_asignacion = Column(Date, nullable=False)
    observacion = Column(String(350), nullable=False)
    borrado = Column(Boolean, default=True)

    id_inspector = Column(Integer, ForeignKey("inspector.id_inspector"), nullable=False)
    id_reporte = Column(Integer, ForeignKey("reportes.id_reporte"), nullable=False)

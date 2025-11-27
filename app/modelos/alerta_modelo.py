from sqlalchemy import Column, Integer, String, Boolean, LargeBinary, ForeignKey, DateTime
from app.config import Base

class Alerta(Base):
    __tablename__ = "alertas"

    id_alerta = Column(Integer, primary_key=True, index=True)
    fecha_hora = Column(DateTime, nullable=False)
    tipo_alerta = Column(String(50), nullable=False)
    descripcion = Column(String(250), nullable=False)
    nivel_riesgo = Column(String(20), nullable=False)
    imagen_evidencia = Column(LargeBinary, nullable=True)
    estado = Column(String(20), nullable=False)

    id_evento = Column(Integer, ForeignKey("eventos_deteccion.id_evento"), nullable=False)
    borrado = Column(Boolean, default=False)

    # Relación opcional si quieres descargar reportes después
    id_reporte = Column(Integer, ForeignKey("reportes.id_reporte"), nullable=True)

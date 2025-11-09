# app/modelos/evento_deteccion_modelo.py
from sqlalchemy import Column, Integer, String, Boolean, Date, ForeignKey
from sqlalchemy.orm import relationship
from app.config import Base

class EventoDeteccion(Base):
    __tablename__ = "eventos_deteccion"

    id_evento = Column(Integer, primary_key=True, index=True)
    fecha = Column(Date, nullable=False)
    tipo_evento = Column(String(100), nullable=False)
    confianza = Column(String(100), nullable=False)
    id_zona = Column(Integer, ForeignKey("zonas.id_Zona"), nullable=False)
    id_camara = Column(Integer, ForeignKey("camaras.id_camara"), nullable=False)
    id_Trabajador = Column(Integer, ForeignKey("trabajadores.id_trabajador"), nullable=False)
    id_reporte = Column(Integer, ForeignKey("reportes.id_reporte"), nullable=False)
    borrado = Column(Boolean, default=True)

   
# app/modelos/alerta_modelo.py
from sqlalchemy import Column, Integer, String, Boolean, Date, LargeBinary, ForeignKey
from sqlalchemy.orm import relationship
from app.config import Base

class Alerta(Base):
    __tablename__ = "alertas"

    id_Alerta = Column(Integer, primary_key=True, index=True)
    fechaHora = Column(Date, nullable=False)
    tipoAlerta = Column(String(50), nullable=False)
    descripcion = Column(String(250), nullable=False)
    nivelRiesgo = Column(String(20), nullable=False)
    imagenEvidencia = Column(LargeBinary, nullable=True)
    estado = Column(String(20), nullable=False)
    id_evento = Column(Integer, ForeignKey("eventos.id_Evento"), nullable=False)
    id_reporte = Column(Integer, ForeignKey("reportes.id_Reporte"), nullable=False)
    id_supervisor = Column(Integer, ForeignKey("supervisores.id_Supervisor"), nullable=False)
    borrado = Column(Boolean, default=True)

    evento = relationship("Evento", back_populates="alertas")
    reporte = relationship("Reporte", back_populates="alertas")
    supervisor = relationship("Supervisor", back_populates="alertas")
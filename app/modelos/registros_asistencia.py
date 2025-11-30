from sqlalchemy import Column, Integer, DateTime, Boolean, String, ForeignKey, text
from sqlalchemy.orm import relationship
from app.config import Base

class RegistroAsistencia(Base):
    __tablename__ = "registros_asistencia"

    id_registro = Column(Integer, primary_key=True, index=True)
    fecha_hora = Column(DateTime, nullable=False, server_default=text("CURRENT_TIMESTAMP"))
    cumple_epp = Column(Boolean, default=True, nullable=False)

    # Guardar el código que ingresó el worker (histórico)
    codigo_ingresado = Column(String(50), nullable=False)

    # Relaciones FK
    id_trabajador = Column(Integer, ForeignKey("trabajadores.id_trabajador"), nullable=False)
    id_empresa = Column(Integer, ForeignKey("empresas.id_Empresa"), nullable=False)
    id_zona = Column(Integer, ForeignKey("zonas.id_Zona"), nullable=False)
    id_supervisor = Column(Integer, ForeignKey("supervisor.id_supervisor"), nullable=False)
    id_inspector = Column(Integer, ForeignKey("inspector.id_inspector"), nullable=True)
    id_camara = Column(Integer, ForeignKey("camaras.id_camara"), nullable=False)

    # Relaciones ORM
    trabajador = relationship("Trabajador", lazy="joined")
    empresa = relationship("Empresa", lazy="joined")
    zona = relationship("Zona", lazy="joined")
    supervisor = relationship("Supervisor", lazy="joined")
    inspector = relationship("Inspector", lazy="joined")
    camara = relationship("Camara", lazy="joined")

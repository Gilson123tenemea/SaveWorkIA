from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from app.config import Base

class Empresa(Base):
    __tablename__ = "empresas"

    id_Empresa = Column(Integer, primary_key=True, index=True)
    nombreEmpresa = Column(String(100), nullable=False)
    ruc = Column(String(13), unique=True, nullable=False)
    direccion = Column(String(100), nullable=False)
    telefono = Column(String(15), nullable=False)
    correo = Column(String(100), nullable=False)
    sector = Column(String(50), nullable=False)
    id_Administrador = Column(Integer, ForeignKey("administradores.id_Administrador"), nullable=False)
    id_Supervisor = Column(Integer, ForeignKey("supervisores.id_Supervisor"), nullable=False)
    borrado = Column(Boolean, default=True)

    administrador = relationship("Administrador", back_populates="empresas")
    supervisor = relationship("Supervisor", back_populates="empresas")
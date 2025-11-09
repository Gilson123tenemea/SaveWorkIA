# app/modelos/trabajador.py
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, Date
from app.config import Base

class Trabajador(Base):
    __tablename__ = "trabajadores"

    id_trabajador = Column(Integer, primary_key=True, index=True)
    cargo = Column(String(100), nullable=False)
    area_trabajo = Column(String(100), nullable=False)
    implementos_requeridos = Column(String(550), nullable=False)
    estado = Column(Boolean, default=True)
    fecharegistro = Column(Date, nullable=False)
    borrado = Column(Boolean, default=False)
    
    #relaciones
    id_persona_trabajador = Column(Integer, ForeignKey("personas.id_persona"), nullable=False)
   # id_empresa = Column(Integer, ForeignKey("empresas.id_empresa"), nullable=False)
    id_supervisor_trabajador = Column(Integer, ForeignKey("supervisor.id_supervisor"), nullable=False)
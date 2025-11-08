# app/modelos/supervisor.py
from sqlalchemy import Column, Integer, String, Boolean, Date, ForeignKey
from app.config import Base

class Supervisor(Base):
    __tablename__ = "supervisor"

    id_supervisor = Column(Integer, primary_key=True, index=True)
    especialidad_seguridad = Column(String(350), nullable=False)
    experiencia = Column(Integer, nullable=False)
    borrado = Column(Boolean, default=True)

    # Relacion con persona
    id_persona_supervisor = Column(Integer, nullable=False)
    id_persona_supervisor = Column(Integer, ForeignKey("personas.id_persona"), nullable=False)

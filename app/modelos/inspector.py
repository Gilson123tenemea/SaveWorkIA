# app/modelos/inspector.py
from sqlalchemy import Column, Integer, String, Boolean, Date, ForeignKey
from app.config import Base

class Inspector(Base):
    __tablename__ = "inspector"

    id_inspector = Column(Integer, primary_key=True, index=True)
    zona_asignada = Column(String(550), nullable=False)
    frecuenciaVisita = Column(String(500), nullable=True)
    borrado = Column(Boolean, default=True)

    # Relacion con persona
    id_persona_inspector = Column(Integer, nullable=False)
    id_persona_inspector = Column(Integer, ForeignKey("personas.id_persona"), nullable=False)
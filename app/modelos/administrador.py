# app/modelos/administrador.py
from sqlalchemy import Column, Integer, String, Boolean, Date, LargeBinary, ForeignKey
from app.config import Base

class Administrador(Base):
    __tablename__ = "administrador"

    id_administrador = Column(Integer, primary_key=True, index=True)
    ultima_conexion = Column(Date, nullable=True)
    fechaRegistroSistema = Column(Date, nullable=False)
    borrado = Column(Boolean, default=True)

    # Relacion con persona
    id_persona_administrador = Column(Integer, nullable=False)
    id_persona_administrador = Column(Integer, ForeignKey("personas.id_persona"), nullable=False)

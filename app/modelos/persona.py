# app/modelos/persona_modelo.py
from sqlalchemy import Column, Integer, String, Boolean, Date, LargeBinary
from app.config import Base

class Persona(Base):
    __tablename__ = "personas"

    id_persona = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(100), nullable=False)
    apellido = Column(String(100), nullable=False)
    telefono = Column(String(15), nullable=True)
    correo = Column(String(150), unique=True, index=True, nullable=False)
    direccion = Column(String(350), nullable=False)
    genero = Column(String(20), nullable=False)
    fecha_nacimiento = Column(Date, nullable=False)
    foto = Column(LargeBinary, nullable=True) 
    contrasena = Column(String(50), nullable=False)
    borrado = Column(Boolean, default=True)

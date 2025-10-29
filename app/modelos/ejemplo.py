# app/modelos/ejemplo.py
from sqlalchemy import Column, Integer, String
from app.config import Base

class Ejemplo(Base):
    __tablename__ = "ejemplos"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(100), nullable=False)
    descripcion = Column(String(250), nullable=True)

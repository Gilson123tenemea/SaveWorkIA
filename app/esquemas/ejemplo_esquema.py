# app/esquemas/ejemplo_esquema.py
from pydantic import BaseModel

class EjemploBase(BaseModel):
    nombre: str
    descripcion: str | None = None

class EjemploCrear(EjemploBase):
    pass

class Ejemplo(EjemploBase):
    id: int

    class Config:
        orm_mode = True

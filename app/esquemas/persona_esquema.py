# app/esquemas/persona_esquema.py
from pydantic import BaseModel, EmailStr
from datetime import date
from typing import Optional

class PersonaBase(BaseModel):
    nombre: str
    apellido: str
    telefono: Optional[str] = None
    correo: EmailStr
    direccion: str
    genero: str
    fecha_nacimiento: date
    borrado: Optional[bool] = True

class PersonaCreate(PersonaBase):
    contrasena: str
    foto: Optional[bytes] = None  

class PersonaResponse(PersonaBase):
    id_persona: int
    foto: Optional[bytes] = None 
    contrasena: str  

    class Config:
        orm_mode = True

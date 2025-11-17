from pydantic import BaseModel, EmailStr
from datetime import date
from typing import Optional


# ---------------------------
# ESQUEMA PERSONA (anidado)
# ---------------------------
class PersonaBase(BaseModel):
    cedula: str
    nombre: str
    apellido: str
    telefono: Optional[str] = None
    correo: EmailStr
    direccion: str
    genero: str
    fecha_nacimiento: date
    contrasena: str  # se encriptará luego
    # rol se genera automáticamente → no se envía
    # borrado se genera automáticamente → no se envía


# ---------------------------
# ESQUEMA TRABAJADOR
# ---------------------------
class TrabajadorBase(BaseModel):
    cargo: str
    area_trabajo: str
    implementos_requeridos: str
    estado: Optional[bool] = True
    # fecharegistro se genera automáticamente → no se envía
    codigo_trabajador: str
    id_empresa: int
    id_supervisor_trabajador: int
    # borrado se genera automáticamente → no se envía


# ---------------------------
# CREAR PERSONA + TRABAJADOR
# ---------------------------
class TrabajadorPersonaCreate(BaseModel):
    persona: PersonaBase
    trabajador: TrabajadorBase


# ---------------------------
# RESPUESTA COMPLETA
# ---------------------------
class PersonaResponse(PersonaBase):
    id_persona: int

    class Config:
        orm_mode = True


class TrabajadorResponse(TrabajadorBase):
    id_trabajador: int
    fecharegistro: date     # aquí sí aparece, porque viene del modelo
    persona: PersonaResponse

    class Config:
        orm_mode = True

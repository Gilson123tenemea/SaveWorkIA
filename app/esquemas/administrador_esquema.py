from pydantic import BaseModel, EmailStr
from datetime import date
from typing import Optional

# --- Datos de Persona ---
class PersonaBase(BaseModel):
    cedula: str
    nombre: str
    apellido: str
    telefono: Optional[str]
    correo: EmailStr
    direccion: str
    genero: str
    fecha_nacimiento: date
    contrasena: str

# --- Crear administrador (datos recibidos) ---
class AdministradorCreate(BaseModel):
    persona: PersonaBase
    ultima_conexion: Optional[date] = None

# --- Respuesta del registro ---
class AdministradorResponse(BaseModel):
    id_administrador: int
    id_persona: int
    nombre: str
    apellido: str
    correo: str
    fechaRegistroSistema: date
    borrado: bool

    class Config:
        orm_mode = True

# --- Login ---
class LoginAdministrador(BaseModel):
    correo: EmailStr
    contrasena: str

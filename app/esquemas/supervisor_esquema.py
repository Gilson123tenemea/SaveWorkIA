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

# --- Crear supervisor (datos recibidos) ---
class SupervisorCreate(BaseModel):
    persona: PersonaBase
    especialidad_seguridad: str
    experiencia: int
    id_empresa_supervisor: int

# --- Respuesta del registro ---
class SupervisorResponse(BaseModel):
    id_supervisor: int
    id_persona: int
    nombre: str
    apellido: str
    correo: str
    especialidad_seguridad: str
    experiencia: int
    borrado: bool

    class Config:
        orm_mode = True


# --- Login ---
class LoginSupervisor(BaseModel):
    correo: EmailStr
    contrasena: str
# --- Actualizar supervisor (datos recibidos) ---
class SupervisorUpdate(BaseModel):
    persona: PersonaBase
    especialidad_seguridad: str
    experiencia: int

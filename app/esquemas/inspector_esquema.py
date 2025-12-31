# app/esquemas/inspector_esquema.py
from pydantic import BaseModel, EmailStr
from datetime import date
from typing import Optional, List

# --- Datos de Persona para Inspector (registro/edición) ---
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

# --- Crear Inspector (recibe persona y datos del inspector) ---
class InspectorCreate(BaseModel):
    persona: PersonaBase
    frecuenciaVisita: Optional[str] = None
    id_supervisor_registro: int  # quién lo registró

# --- Respuesta del registro ---
class InspectorResponse(BaseModel):
    id_inspector: int
    id_persona: int
    nombre: str
    apellido: str
    correo: str
    frecuenciaVisita: Optional[str]
    fecha_asignacion: date
    borrado: bool

    class Config:
        orm_mode = True

# --- Login ---
class LoginInspector(BaseModel):
    correo: EmailStr
    contrasena: str

# --- Zonas asignadas al inspector ---
class ZonaAsignadaInspector(BaseModel):
    id_Zona: int
    nombreZona: str
    latitud: str
    longitud: str
    fecha_asignacion: str
    total_trabajadores: int
    total_camaras: int

    class Config:
        orm_mode = True
class ZonaAsignadaPerfil(BaseModel):
    id_Zona: int
    nombreZona: str
    fecha_asignacion: Optional[date]

    class Config:
        orm_mode = True

class InspectorPerfil(BaseModel):
    id_inspector: int
    id_persona: int
    cedula: str
    nombre: str
    apellido: str
    telefono: Optional[str] = None
    correo: EmailStr
    direccion: str
    genero: str
    fecha_nacimiento: date
    frecuenciaVisita: Optional[str] = None

    zonas_asignadas: List[ZonaAsignadaPerfil]  
    fotoBase64: Optional[str] = None

    class Config:
        orm_mode = True

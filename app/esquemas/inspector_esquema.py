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
    fotoBase64: Optional[str] = None

    class Config:
        orm_mode = True

# 🆕 --- Schema para actualizar perfil del inspector ---
class InspectorPerfilUpdate(BaseModel):
    """
    Schema para actualizar el perfil del inspector desde la interfaz de usuario.
    Solo permite actualizar: nombre, apellido, correo
    Teléfono es opcional pero no se edita desde el perfil (solo lectura en frontend)
    """
    nombre: str
    apellido: str
    correo: EmailStr
    telefono: Optional[str] = None

    class Config:
        orm_mode = True
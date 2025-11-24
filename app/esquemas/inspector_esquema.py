# app/esquemas/inspector_esquema.py
from pydantic import BaseModel, EmailStr
from datetime import date
from typing import Optional

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
    zona_asignada: str
    frecuenciaVisita: Optional[str] = None
    id_supervisor_registro: int  # quién lo registró

# --- Respuesta del registro ---
class InspectorResponse(BaseModel):
    id_inspector: int
    id_persona: int
    nombre: str
    apellido: str
    correo: str
    zona_asignada: str
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

# --- PERFIL DEL INSPECTOR (para el modal de perfil) ---
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
    zona_asignada: str
    frecuenciaVisita: Optional[str] = None
    fecha_asignacion: Optional[date] = None
    fotoBase64: Optional[str] = None

    class Config:
        orm_mode = True

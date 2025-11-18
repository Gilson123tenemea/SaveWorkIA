from pydantic import BaseModel
from typing import Optional
from pydantic import BaseModel


# Datos del inspector (provienen de Persona)
class InspectorPersona(BaseModel):
    nombre: str
    apellido: str
    cedula: str

# Datos de la zona
class ZonaInfo(BaseModel):
    id: int
    nombre: str
    latitud: str
    longitud: str

# Respuesta completa
class ZonaDetallesResponse(BaseModel):
    zona: ZonaInfo
    inspector: Optional[InspectorPersona] = None
    total_camaras: int
    total_trabajadores: int

    class Config:
        orm_mode = True

class TrabajadorZonaBase(BaseModel):
    id_trabajador_trabajadorzona: int
    id_zona_trabajadorzona: int

class TrabajadorZonaCreate(TrabajadorZonaBase):
    pass

class TrabajadorZonaResponse(TrabajadorZonaBase):
    id_trabajador_zona: int
    borrado: bool

    class Config:
        orm_mode = True

class TrabajadorZonaDetalle(BaseModel):
    id_asignacion: int
    trabajador_id: int
    trabajador_nombre: str
    trabajador_apellido: str
    trabajador_cedula: str
    trabajador_cargo: str

    zona_id: int
    zona_nombre: str

    class Config:
        orm_mode = True
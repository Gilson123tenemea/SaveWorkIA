# app/esquemas/zona_esquema.py
from pydantic import BaseModel
from typing import Optional

class ZonaBase(BaseModel):
    nombreZona: str
    latitud: str
    longitud: str

class ZonaCreate(ZonaBase):
    id_empresa_zona: int
    id_administrador_zona: int

class ZonaUpdate(BaseModel):
    nombreZona: Optional[str] = None
    latitud: Optional[str] = None
    longitud: Optional[str] = None
    id_empresa_zona: Optional[int] = None
    id_administrador_zona: Optional[int] = None

class ZonaResponse(ZonaBase):
    id_Zona: int
    id_empresa_zona: int
    id_administrador_zona: int
    borrado: bool

    class Config:
        orm_mode = True

class ZonaConDetalles(BaseModel):
    id_Zona: int
    nombreZona: str
    latitud: str
    longitud: str
    id_empresa_zona: int
    total_camaras: int
    total_trabajadores: int

    class Config:
        orm_mode = True

# app/esquemas/zona_esquema.py
from pydantic import BaseModel
from typing import Optional

class ZonaBase(BaseModel):
    nombreZona: str
    latitud: str
    longitud: str
    borrado: Optional[bool] = True

class ZonaCreate(ZonaBase):
    id_Empresa: int
    id_Administrador: int

class ZonaUpdate(BaseModel):
    nombreZona: Optional[str] = None
    latitud: Optional[str] = None
    longitud: Optional[str] = None
    id_Empresa: Optional[int] = None
    id_Administrador: Optional[int] = None
    borrado: Optional[bool] = None

class ZonaResponse(ZonaBase):
    id_Zona: int
    id_Empresa: int
    id_Administrador: int

    class Config:
        orm_mode = True
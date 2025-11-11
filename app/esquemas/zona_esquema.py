# app/esquemas/zona_esquema.py
from pydantic import BaseModel
from typing import Optional

class ZonaBase(BaseModel):
    nombreZona: str
    latitud: str
    longitud: str
    borrado: Optional[bool] = True


class ZonaCreate(ZonaBase):
    id_empresa_zona: int
    id_administrador_zona: int


class ZonaUpdate(BaseModel):
    nombreZona: Optional[str] = None
    latitud: Optional[str] = None
    longitud: Optional[str] = None
    id_empresa_zona: Optional[int] = None
    id_administrador_zona: Optional[int] = None
    borrado: Optional[bool] = None


class ZonaResponse(ZonaBase):
    id_Zona: int
    id_empresa_zona: int
    id_administrador_zona: int

    class Config:
        orm_mode = True

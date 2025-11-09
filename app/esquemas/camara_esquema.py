from pydantic import BaseModel
from datetime import date
from typing import Optional

class CamaraBase(BaseModel):
    codigo: str
    tipo: str
    estado: str
    ipAddress: str
    ultimaTransmision: Optional[date] = None
    ultima_revision: Optional[date] = None
    borrado: Optional[bool] = True

class CamaraCreate(CamaraBase):
    id_zona: int
    id_administrador: int

class CamaraUpdate(BaseModel):
    codigo: Optional[str] = None
    tipo: Optional[str] = None
    estado: Optional[str] = None
    ipAddress: Optional[str] = None
    ultimaTransmision: Optional[date] = None
    ultima_revision: Optional[date] = None
    id_zona: Optional[int] = None
    id_administrador: Optional[int] = None
    borrado: Optional[bool] = None

class CamaraResponse(CamaraBase):
    id_camara: int
    id_zona: int
    id_administrador: int

    class Config:
        orm_mode = True
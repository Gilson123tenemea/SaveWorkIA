from pydantic import BaseModel
from typing import Optional
from typing import List

class ZonaEppBase(BaseModel):
    tipo_epp: str
    obligatorio: bool = True

class ZonaEppCreate(ZonaEppBase):
    id_zona: int

class ZonaEppUpdateRequest(BaseModel):
    epps: List[str]

class ZonaEppUpdate(BaseModel):
    obligatorio: Optional[bool] = None
    activo: Optional[bool] = None

class ZonaEppResponse(ZonaEppBase):
    id: int
    id_zona: int
    activo: bool

    class Config:
        orm_mode = True

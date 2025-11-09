from pydantic import BaseModel
from datetime import date
from typing import Optional

class TrabajadorBase(BaseModel):
    cargo: str
    area_trabajo: str
    implementos_requeridos: str
    estado: Optional[bool] = True
    fecharegistro: date
    borrado: Optional[bool] = False
    id_persona: int
    id_supervisor: int

class TrabajadorCreate(TrabajadorBase):
    pass

class TrabajadorResponse(TrabajadorBase):
    id_trabajador: int

    class Config:
        orm_mode = True

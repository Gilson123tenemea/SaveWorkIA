from pydantic import BaseModel
from datetime import date
from typing import Optional

class AdministradorBase(BaseModel):
    ultima_conexion: Optional[date] = None
    fechaRegistroSistema: date
    borrado: Optional[bool] = True
    id_persona_administrador: int

class AdministradorCreate(AdministradorBase):
    pass

class AdministradorResponse(AdministradorBase):
    id_administrador: int

    class Config:
        orm_mode = True

from pydantic import BaseModel
from typing import Optional

class SupervisorBase(BaseModel):
    especialidad_seguridad: str
    experiencia: int
    borrado: Optional[bool] = True
    id_persona_supervisor: int

class SupervisorCreate(SupervisorBase):
    pass

class SupervisorResponse(SupervisorBase):
    id_supervisor: int

    class Config:
        orm_mode = True

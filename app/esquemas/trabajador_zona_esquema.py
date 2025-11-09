from pydantic import BaseModel
from typing import Optional

class TrabajadorZonaBase(BaseModel):
    borrado: Optional[bool] = True
    id_trabajador_trabajadorzona: int
    id_zona_trabajadorzona: int

class TrabajadorZonaCreate(TrabajadorZonaBase):
    pass

class TrabajadorZonaResponse(TrabajadorZonaBase):
    id_trabajador_zona: int

    class Config:
        orm_mode = True

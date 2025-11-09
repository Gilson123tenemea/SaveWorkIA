from pydantic import BaseModel
from datetime import date
from typing import Optional

class ReporteBase(BaseModel):
    fecha: date
    descripcion: str
    nivel_alerta: str
    estado: str
    borrado: Optional[bool] = True
    id_empresa: int

class ReporteCreate(ReporteBase):
    pass

class ReporteResponse(ReporteBase):
    id_reporte: int

    class Config:
        orm_mode = True

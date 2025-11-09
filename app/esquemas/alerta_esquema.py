from pydantic import BaseModel
from datetime import date
from typing import Optional

class AlertaBase(BaseModel):
    fechaHora: date
    tipoAlerta: str
    descripcion: str
    nivelRiesgo: str
    imagenEvidencia: Optional[bytes] = None
    estado: str
    borrado: Optional[bool] = True

class AlertaCreate(AlertaBase):
    id_evento: int
    id_reporte: int
    id_supervisor: int

class AlertaUpdate(BaseModel):
    fechaHora: Optional[date] = None
    tipoAlerta: Optional[str] = None
    descripcion: Optional[str] = None
    nivelRiesgo: Optional[str] = None
    imagenEvidencia: Optional[bytes] = None
    estado: Optional[str] = None
    id_evento: Optional[int] = None
    id_reporte: Optional[int] = None
    id_supervisor: Optional[int] = None
    borrado: Optional[bool] = None

class AlertaResponse(AlertaBase):
    id_Alerta: int
    id_evento: int
    id_reporte: int
    id_supervisor: int

    class Config:
        orm_mode = True
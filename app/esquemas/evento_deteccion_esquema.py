# app/esquemas/evento_deteccion_esquema.py
from pydantic import BaseModel
from datetime import date
from typing import Optional

class EventoDeteccionBase(BaseModel):
    fecha: date
    tipo_evento: str
    confianza: str
    borrado: Optional[bool] = True

class EventoDeteccionCreate(EventoDeteccionBase):
    id_zona: int
    id_camara: int
    id_Trabajador: int
    id_reporte: int

class EventoDeteccionUpdate(BaseModel):
    fecha: Optional[date] = None
    tipo_evento: Optional[str] = None
    confianza: Optional[str] = None
    id_zona: Optional[int] = None
    id_camara: Optional[int] = None
    id_Trabajador: Optional[int] = None
    id_reporte: Optional[int] = None
    borrado: Optional[bool] = None

class EventoDeteccionResponse(EventoDeteccionBase):
    id_evento: int
    id_zona: int
    id_camara: int
    id_Trabajador: int
    id_reporte: int

    class Config:
        orm_mode = True
# app/esquemas/reporte_incumplimientos_esquema.py
from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class TrabajadorInfo(BaseModel):
    nombre: str
    apellido: str
    cedula: str

    class Config:
        from_attributes = True


class InspectorInfo(BaseModel):
    nombre: Optional[str] = None
    apellido: Optional[str] = None


class CamaraInfo(BaseModel):
    codigo: str
    zona: str


class EvidenciaInfo(BaseModel):
    detalle: str
    foto_base64: str | None = None
    fecha: datetime


class IncumplimientoResponse(BaseModel):
    trabajador: TrabajadorInfo
    inspector: InspectorInfo
    camara: CamaraInfo
    evidencia: EvidenciaInfo
    fecha_registro: datetime

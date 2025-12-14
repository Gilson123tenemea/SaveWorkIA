# app/esquemas/reporte_inspector_incumplimiento_esquema.py
from pydantic import BaseModel
from datetime import datetime
from typing import Optional
from typing import List


class TrabajadorInfo(BaseModel):
    nombre: str
    apellido: str
    cedula: str

    class Config:
        from_attributes = True


class CamaraInfo(BaseModel):
    codigo: str
    zona: str


class EvidenciaInfo(BaseModel):
    id_evidencia: int
    detalle: str
    foto_base64: str | None = None
    fecha: datetime
    estado: bool | None = None
    observaciones: str | None = None  


class IncumplimientoInspectorResponse(BaseModel):
    trabajador: TrabajadorInfo
    camara: CamaraInfo
    evidencia: EvidenciaInfo
    fecha_registro: datetime


class EstadisticasIncumplimiento(BaseModel):
    total: int
    cumple: int
    incumple: int
    tasa: float


class HistorialIncumplimientoInspectorResponse(BaseModel):
    estadisticas: EstadisticasIncumplimiento
    historial: List[IncumplimientoInspectorResponse]
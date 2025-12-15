# app/esquemas/reporte_esquema.py
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class ReporteCreate(BaseModel):
    tipo_reporte: str
    formato: str
    filtros: Optional[str] = None
    generado_por: str
    id_empresa: int
    id_inspector: Optional[int] = None


class ReporteResponse(BaseModel):
    id_reporte: int
    tipo_reporte: str
    formato: str
    filtros: Optional[str]
    generado_por: str
    fecha_generacion: datetime
    id_empresa: int
    id_inspector: Optional[int]

    class Config:
        from_attributes = True


class BarItem(BaseModel):
    label: str
    value: int


class BarsResponse(BaseModel):
    total: int
    items: List[BarItem]


class PieItem(BaseModel):
    label: str
    value: int


class PieResponse(BaseModel):
    total: int
    items: List[PieItem]

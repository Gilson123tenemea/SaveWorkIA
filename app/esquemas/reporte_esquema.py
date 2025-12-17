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

class EmpresaInspectorResponse(BaseModel):
    """Respuesta con datos de empresa por inspector"""
    id_Empresa: int
    nombreEmpresa: str

    class Config:
        from_attributes = True

class ZonaItem(BaseModel):
    """Schema para una zona individual"""
    id: int
    nombre: str

    class Config:
        from_attributes = True


class ZonasInspectorResponse(BaseModel):
    """Respuesta con lista de zonas asignadas a un inspector"""
    id_inspector: int
    total_zonas: int
    zonas: List[ZonaItem]

    class Config:
        from_attributes = True

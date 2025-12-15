from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List


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
    detalle: Optional[str] = None
    foto_base64: Optional[str] = None
    fecha: Optional[datetime] = None


class IncumplimientoResponse(BaseModel):
    trabajador: TrabajadorInfo

    # 🔥 CLAVE: ahora puede ser None
    inspector: Optional[InspectorInfo] = None

    camara: CamaraInfo
    fecha_registro: datetime

    # 🔥 NUEVOS CAMPOS QUE TU BACK YA ENVÍA
    detecciones: List[str]
    epps_zona: List[str]

    evidencia: EvidenciaInfo


class EstadisticasEPP(BaseModel):
    total: int
    cumple: int
    incumple: int
    tasa: float


class ReporteTrabajadorResponse(BaseModel):
    estadisticas: EstadisticasEPP
    historial: List[IncumplimientoResponse]

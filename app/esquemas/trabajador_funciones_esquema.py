from pydantic import BaseModel
from typing import Optional, List
from datetime import date, datetime

class TrabajadorLoginRequest(BaseModel):
    correo: str
    contrasena: str


class TrabajadorLoginResponse(BaseModel):
    id_trabajador: int
    nombre: str
    apellido: str
    correo: str
    rol: str
    id_empresa: int


class EmpresaPerfil(BaseModel):
    id_empresa: int
    nombreEmpresa: str
    ruc: str
    sector: str


class ZonaAsignadaPerfil(BaseModel):
    id_zona: int
    nombreZona: str
    latitud: str
    longitud: str
    fecha_asignacion: Optional[date] = None


class TrabajadorPerfilResponse(BaseModel):
    id_trabajador: int
    cedula: str
    nombre: str
    apellido: str
    correo: str
    telefono: Optional[str]

    cargo: str
    area_trabajo: str

    empresa: EmpresaPerfil
    zona_asignada: Optional[ZonaAsignadaPerfil] = None

    class Config:
        orm_mode = True

class EstadisticasAsistencia(BaseModel):
    total_registros: int
    cumple_epp: int
    no_cumple_epp: int
    tasa_cumplimiento: float


class EstadisticasIncumplimientos(BaseModel):
    total_fallos: int
    revisados: int
    pendientes: int


class TrabajadorEstadisticasResponse(BaseModel):
    id_trabajador: int
    asistencia: EstadisticasAsistencia
    incumplimientos: EstadisticasIncumplimientos


class TrabajadorInfo(BaseModel):
    nombre: str
    apellido: str
    cedula: str


class CamaraInfo(BaseModel):
    codigo: str
    zona: str


class EvidenciaInfo(BaseModel):
    id_evidencia: int
    detalle: str
    foto_base64: Optional[str]
    fecha: datetime
    estado: Optional[bool]
    observaciones: Optional[str]


class IncumplimientoTrabajadorItem(BaseModel):
    trabajador: TrabajadorInfo
    camara: CamaraInfo
    evidencia: EvidenciaInfo
    fecha_registro: datetime


class EstadisticasTrabajador(BaseModel):
    total: int
    cumple: int
    incumple: int
    tasa: float


class IncumplimientosTrabajadorResponse(BaseModel):
    estadisticas: EstadisticasTrabajador
    historial: List[IncumplimientoTrabajadorItem]
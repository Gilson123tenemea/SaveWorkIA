from pydantic import BaseModel
from typing import Optional, List, Dict
from datetime import date, datetime
from pydantic import BaseModel, Field
from typing import Optional, List, Dict
from datetime import date, datetime

class TrabajadorLoginRequest(BaseModel):
    correo: str
    contrasena: str


class TrabajadorLoginResponse(BaseModel):
    id_trabajador: int
    id_persona: int
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
    foto_base64: Optional[str] = None 
    empresa: EmpresaPerfil
    zona_asignada: Optional[ZonaAsignadaPerfil] = None

    class Config:
        from_attributes = True

class EstadisticasAsistencia(BaseModel):
    total_registros: int
    cumple_epp: int
    no_cumple_epp: int
    tasa_cumplimiento: float


class EstadisticasIncumplimientos(BaseModel):
    total_fallos: int
    revisados: int
    pendientes: int


class EppsPorZona(BaseModel):
    zona: str
    epps: List[str]


class TrabajadorEstadisticasResponse(BaseModel):
    id_trabajador: int
    asistencia: EstadisticasAsistencia
    incumplimientos: EstadisticasIncumplimientos
    detecciones: Dict[str, int]  
    epps_por_zona: Dict[int, EppsPorZona] 


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
    detecciones: List[str]  
    epps_zona: List[str]   
    fecha_registro: datetime


class EstadisticasTrabajador(BaseModel):
    total: int
    cumple: int
    incumple: int
    tasa: float


class IncumplimientosTrabajadorResponse(BaseModel):
    estadisticas: EstadisticasTrabajador
    historial: List[IncumplimientoTrabajadorItem]

    class Config:
        from_attributes = True

class InspectorInfo(BaseModel):
    nombre: str
    apellido: str
    cedula: str


class AsistenciaRegistroItem(BaseModel):
    id_registro: int
    fecha: date
    hora: str
    codigo_trabajador: str
    cedula: str
    nombre: str
    apellido: str
    nombre_zona: str
    nombre_inspector: str
    apellido_inspector: str
    codigo_camara: str
    cumple_epp: bool

    class Config:
        from_attributes = True


class HistorialAsistenciasResponse(BaseModel):
    total_registros: int
    total_cumple: int
    total_no_cumple: int
    mes: Optional[int]
    año: Optional[int]
    registros: List[AsistenciaRegistroItem]

    class Config:
        from_attributes = True

class ActualizarTrabajadorRequest(BaseModel):
    """
    Esquema para actualizar datos del trabajador.
    Todos los campos son opcionales y pueden venir del body directamente.
    """
    nombre: Optional[str] = Field(None, min_length=1, max_length=50)
    apellido: Optional[str] = Field(None, min_length=1, max_length=50)
    correo: Optional[str] = Field(None, max_length=150)
    telefono: Optional[str] = Field(None, max_length=10)
    cargo: Optional[str] = Field(None, min_length=1, max_length=50)

    class Config:
        json_schema_extra = {
            "example": {
                "nombre": "Juan",
                "apellido": "Pérez",
                "correo": "juan.perez@example.com",
                "telefono": "0987654321",
                "cargo": "Técnico de Seguridad"
            }
        }


class ActualizarTrabajadorResponse(BaseModel):
    """
    Respuesta al actualizar trabajador
    """
    id_trabajador: int
    cedula: str
    nombre: str
    apellido: str
    correo: str
    telefono: Optional[str]
    cargo: str
    mensaje: str

    class Config:
        from_attributes = True
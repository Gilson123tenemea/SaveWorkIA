from pydantic import BaseModel
from datetime import datetime

class RegistroAsistenciaCreate(BaseModel):
    fecha_hora: datetime | None = None
    cumple_epp: bool
    codigo_ingresado: str

    id_trabajador: int
    id_empresa: int
    id_zona: int
    id_supervisor: int
    id_camara: int 
    id_inspector: int | None = None


class RegistroAsistenciaResponse(BaseModel):
    id_registro: int
    fecha_hora: datetime
    cumple_epp: bool
    codigo_ingresado: str
    id_trabajador: int
    id_empresa: int
    id_zona: int
    id_supervisor: int
    id_camara: int 
    id_inspector: int | None = None

    class Config:
        from_attributes = True

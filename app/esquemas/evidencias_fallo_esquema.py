from pydantic import BaseModel
from datetime import datetime

class EvidenciaFalloCreate(BaseModel):
    foto_base64: str
    detalle_fallo: str
    id_registro: int


class EvidenciaFalloResponse(BaseModel):
    id_evidencia: int
    foto_base64: str
    detalle_fallo: str
    fecha_captura: datetime
    id_registro: int

    class Config:
        from_attributes = True

class EvidenciaFalloUpdate(BaseModel):
    estado: bool | None = None
    observaciones: str | None = None

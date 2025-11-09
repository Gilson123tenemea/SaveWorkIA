from pydantic import BaseModel
from datetime import date
from typing import Optional

class InspectorReporteBase(BaseModel):
    fecha_asignacion: date
    observacion: str
    borrado: Optional[bool] = True
    id_inspector: int
    id_reporte: int

class InspectorReporteCreate(InspectorReporteBase):
    pass

class InspectorReporteResponse(InspectorReporteBase):
    id_inspector_reporte: int

    class Config:
        orm_mode = True

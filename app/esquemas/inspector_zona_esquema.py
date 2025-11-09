from pydantic import BaseModel
from datetime import date
from typing import Optional

class InspectorZonaBase(BaseModel):
    fecha_asignacion: date
    borrado: Optional[bool] = True
    id_inspector_inspectorzona: int
    id_zona_inspectorzona: int

class InspectorZonaCreate(InspectorZonaBase):
    pass

class InspectorZonaResponse(InspectorZonaBase):
    id_inspector_zona: int

    class Config:
        orm_mode = True

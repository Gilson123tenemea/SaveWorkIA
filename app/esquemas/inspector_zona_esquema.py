from pydantic import BaseModel
from typing import Optional
from datetime import date

class InspectorZonaBase(BaseModel):
    id_inspector_inspectorzona: int
    id_zona_inspectorzona: int
    borrado: Optional[bool] = True

class InspectorZonaCreate(InspectorZonaBase):
    pass

class InspectorZonaResponse(InspectorZonaBase):
    id_inspector_zona: int
    # La fecha sí se devuelve
    fecha_asignacion: date   

    class Config:
        orm_mode = True

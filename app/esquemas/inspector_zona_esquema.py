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

class InspectorZonaFullResponse(BaseModel):
    id_inspector_zona: int
    fecha_asignacion: date
    borrado: bool

    inspector_cedula: str
    inspector_nombre: str
    inspector_apellido: str

    zona_nombre: str

    class Config:
        orm_mode = True

from pydantic import BaseModel
from typing import Optional

class InspectorBase(BaseModel):
    zona_asignada: str
    frecuenciaVisita: Optional[str] = None
    borrado: Optional[bool] = True
    id_persona_inspector: int

class InspectorCreate(InspectorBase):
    pass  # No hay campos adicionales por ahora

class InspectorResponse(InspectorBase):
    id_inspector: int

    class Config:
        orm_mode = True

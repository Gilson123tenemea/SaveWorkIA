from pydantic import BaseModel
from datetime import date
from typing import Optional

class RegistroSupervisorInspectorBase(BaseModel):
    fecha_asignacion: date
    borrado: Optional[bool] = True
    id_supervisor_registro: int
    id_inspector_registro: int

class RegistroSupervisorInspectorCreate(RegistroSupervisorInspectorBase):
    pass  # No hay campos adicionales por ahora

class RegistroSupervisorInspectorResponse(RegistroSupervisorInspectorBase):
    id_registrosupervisorins: int

    class Config:
        orm_mode = True

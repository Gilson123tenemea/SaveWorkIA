# app/esquemas/revision_reporte_esquema.py
from pydantic import BaseModel
from datetime import date
from typing import Optional

class RevisionReporteBase(BaseModel):
    fecha_revision: date
    observacion: str
    borrado: Optional[bool] = True

class RevisionReporteCreate(RevisionReporteBase):
    id_Supervisor: int
    id_reporte: int

class RevisionReporteUpdate(BaseModel):
    fecha_revision: Optional[date] = None
    observacion: Optional[str] = None
    id_Supervisor: Optional[int] = None
    id_reporte: Optional[int] = None
    borrado: Optional[bool] = None

class RevisionReporteResponse(RevisionReporteBase):
    id_revisionreporte: int
    id_Supervisor: int
    id_reporte: int

    class Config:
        orm_mode = True
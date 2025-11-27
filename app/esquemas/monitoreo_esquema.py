from pydantic import BaseModel, ConfigDict
from typing import List, Optional


# --- Cámara ---
class CamaraZonaResponse(BaseModel):
    id_camara: int
    codigo: str
    estado: str
    tipo: str
    ipAddress: str

    model_config = ConfigDict(from_attributes=True)


# --- Zona con cámaras ---
class ZonaConCamarasResponse(BaseModel):
    id_zona: int
    nombreZona: str
    camaras: List[CamaraZonaResponse]

    model_config = ConfigDict(from_attributes=True)


# --- Respuesta final ---
class EmpresaZonasCamarasResponse(BaseModel):
    empresa_id: int
    empresa_nombre: str
    total_zonas: int
    total_camaras: int
    zonas: List[ZonaConCamarasResponse]

    model_config = ConfigDict(from_attributes=True)

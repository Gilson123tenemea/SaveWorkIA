from pydantic import BaseModel, ConfigDict
from datetime import date
from typing import Optional

# ================================
# 📍 Niveles de anidación
# ================================

class EmpresaNested(BaseModel):
    id_Empresa: int
    nombreEmpresa: str

    model_config = ConfigDict(from_attributes=True)


class ZonaNested(BaseModel):
    id_Zona: int
    nombreZona: str
    empresa: Optional[EmpresaNested] = None  # ✅ zona incluye empresa

    model_config = ConfigDict(from_attributes=True)

# ================================
# 📸 Cámara
# ================================

class CamaraBase(BaseModel):
    codigo: str
    tipo: str
    estado: str
    ipAddress: str
    ultimaTransmision: Optional[date] = None
    ultima_revision: Optional[date] = None
    borrado: Optional[bool] = True


class CamaraCreate(CamaraBase):
    id_zona: int
    id_administrador: int


class CamaraUpdate(BaseModel):
    codigo: Optional[str] = None
    tipo: Optional[str] = None
    estado: Optional[str] = None
    ipAddress: Optional[str] = None
    ultimaTransmision: Optional[date] = None
    ultima_revision: Optional[date] = None
    id_zona: Optional[int] = None
    id_administrador: Optional[int] = None
    borrado: Optional[bool] = None


class CamaraResponse(CamaraBase):
    id_camara: int
    id_zona: int
    id_administrador: int
    zona: Optional[ZonaNested] = None  # ✅ incluye la zona con empresa

    model_config = ConfigDict(from_attributes=True)

from pydantic import BaseModel, EmailStr
from typing import Optional

class EmpresaBase(BaseModel):
    nombreEmpresa: str
    ruc: str
    direccion: str
    telefono: str
    correo: EmailStr
    sector: str
    borrado: Optional[bool] = True

class EmpresaCreate(EmpresaBase):
    id_Administrador: int
    id_Supervisor: int

class EmpresaUpdate(BaseModel):
    nombreEmpresa: Optional[str] = None
    ruc: Optional[str] = None
    direccion: Optional[str] = None
    telefono: Optional[str] = None
    correo: Optional[EmailStr] = None
    sector: Optional[str] = None
    id_Administrador: Optional[int] = None
    id_Supervisor: Optional[int] = None
    borrado: Optional[bool] = None

class EmpresaResponse(EmpresaBase):
    id_Empresa: int
    id_Administrador: int
    id_Supervisor: int

    class Config:
        orm_mode = True
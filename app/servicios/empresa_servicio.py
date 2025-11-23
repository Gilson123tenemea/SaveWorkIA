from sqlalchemy.orm import Session
from app.modelos.empresa_modelo import Empresa
from app.esquemas.empresa_esquema import EmpresaCreate, EmpresaUpdate
from fastapi import HTTPException, status

from app.Validaciones.empresa_validaciones import (
    validar_nombre_empresa,
    validar_telefono_empresa,
    validar_ruc_empresa,
    validar_correo_unico,
    validar_ruc_unico
)

def crear_empresa(db: Session, empresa: EmpresaCreate):

    # 🔎 VALIDACIONES
    validar_nombre_empresa(empresa.nombreEmpresa)
    validar_telefono_empresa(empresa.telefono)
    validar_ruc_empresa(empresa.ruc)
    validar_ruc_unico(db, empresa.ruc)
    validar_correo_unico(db, empresa.correo)

    nueva_empresa = Empresa(
        nombreEmpresa=empresa.nombreEmpresa,
        ruc=empresa.ruc,
        direccion=empresa.direccion,
        telefono=empresa.telefono,
        correo=empresa.correo,
        sector=empresa.sector,
        id_administrador_empresa=empresa.id_administrador_empresa,
        borrado=True
    )

    db.add(nueva_empresa)
    db.commit()
    db.refresh(nueva_empresa)
    return nueva_empresa

def obtener_empresas(db: Session, skip: int = 0, limit: int = 100):
    return db.query(Empresa).filter(Empresa.borrado == True).offset(skip).limit(limit).all()

def obtener_empresa_por_id(db: Session, empresa_id: int):
    empresa = db.query(Empresa).filter(Empresa.id_Empresa == empresa_id).first()
    if not empresa:
        raise HTTPException(status_code=404, detail="Empresa no encontrada")
    return empresa

def obtener_empresa_por_ruc(db: Session, ruc: str):
    empresa = db.query(Empresa).filter(Empresa.ruc == ruc).first()
    if not empresa:
        raise HTTPException(status_code=404, detail="Empresa no encontrada")
    return empresa

def actualizar_empresa(db: Session, empresa_id: int, empresa_update: EmpresaUpdate):
    empresa = obtener_empresa_por_id(db, empresa_id)

    # Si edita → validar nombre, teléfono y correo
    if empresa_update.nombreEmpresa:
        validar_nombre_empresa(empresa_update.nombreEmpresa)

    if empresa_update.telefono:
        validar_telefono_empresa(empresa_update.telefono)

    if empresa_update.correo:
        validar_correo_unico(db, empresa_update.correo)

    # ❌ RUC bloqueado (NO se debe actualizar)
    if empresa_update.ruc:
        raise HTTPException(
            status_code=400,
            detail="No se puede modificar el RUC de una empresa"
        )

    for campo, valor in empresa_update.dict(exclude_unset=True).items():
        setattr(empresa, campo, valor)

    db.commit()
    db.refresh(empresa)
    return empresa


def eliminar_empresa(db: Session, empresa_id: int):
    empresa = obtener_empresa_por_id(db, empresa_id)
    empresa.borrado = False
    db.commit()
    return {"message": "Empresa eliminada correctamente"}

def eliminar_empresa_permanente(db: Session, empresa_id: int):
    empresa = obtener_empresa_por_id(db, empresa_id)
    db.delete(empresa)
    db.commit()
    return {"message": "Empresa eliminada permanentemente"}

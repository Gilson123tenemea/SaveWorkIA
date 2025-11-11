from sqlalchemy.orm import Session
from app.modelos.empresa_modelo import Empresa
from app.esquemas.empresa_esquema import EmpresaCreate, EmpresaUpdate
from fastapi import HTTPException, status

def crear_empresa(db: Session, empresa: EmpresaCreate):
    """
    Crea una nueva empresa en la base de datos
    """
    empresa_existente = db.query(Empresa).filter(Empresa.ruc == empresa.ruc).first()
    if empresa_existente:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El RUC ya está registrado"
        )

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
    for campo, valor in empresa_update.dict(exclude_unset=True).items():
        if campo == "id_Administrador":
            setattr(empresa, "id_administrador_empresa", valor)
        else:
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

from sqlalchemy.orm import Session
from app.modelos.zona_modelo import Zona
from app.esquemas.zona_esquema import ZonaCreate, ZonaUpdate
from fastapi import HTTPException, status


def crear_zona(db: Session, zona: ZonaCreate):
    """
    Crea una nueva zona en la base de datos
    """
    # Verificar si ya existe una zona con el mismo nombre en la misma empresa
    zona_existente = db.query(Zona).filter(
        Zona.nombreZona == zona.nombreZona,
        Zona.id_empresa_zona == zona.id_empresa_zona
    ).first()

    if zona_existente:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ya existe una zona con ese nombre en esta empresa"
        )

    nueva_zona = Zona(**zona.dict())
    db.add(nueva_zona)
    db.commit()
    db.refresh(nueva_zona)
    return nueva_zona


def obtener_zonas(db: Session, skip: int = 0, limit: int = 100):
    """
    Obtiene todas las zonas (no borradas por defecto)
    """
    return (
        db.query(Zona)
        .filter(Zona.borrado == True)
        .offset(skip)
        .limit(limit)
        .all()
    )


def obtener_zonas_por_empresa(db: Session, empresa_id: int, skip: int = 0, limit: int = 100):
    """
    Obtiene todas las zonas de una empresa específica
    """
    return (
        db.query(Zona)
        .filter(Zona.id_empresa_zona == empresa_id, Zona.borrado == True)
        .offset(skip)
        .limit(limit)
        .all()
    )


def obtener_zonas_por_administrador(db: Session, administrador_id: int, skip: int = 0, limit: int = 100):
    """
    Obtiene todas las zonas asignadas a un administrador
    """
    return (
        db.query(Zona)
        .filter(Zona.id_administrador_zona == administrador_id, Zona.borrado == True)
        .offset(skip)
        .limit(limit)
        .all()
    )


def obtener_zona_por_id(db: Session, zona_id: int):
    """
    Obtiene una zona por su ID
    """
    zona = db.query(Zona).filter(Zona.id_Zona == zona_id).first()
    if not zona:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Zona no encontrada"
        )
    return zona


def actualizar_zona(db: Session, zona_id: int, zona_update: ZonaUpdate):
    """
    Actualiza los datos de una zona
    """
    zona = obtener_zona_por_id(db, zona_id)

    # Actualizar solo los campos que no son None
    for campo, valor in zona_update.dict(exclude_unset=True).items():
        setattr(zona, campo, valor)

    db.commit()
    db.refresh(zona)
    return zona


def eliminar_zona(db: Session, zona_id: int):
    """
    Eliminación lógica de una zona (marca borrado = False)
    """
    zona = obtener_zona_por_id(db, zona_id)
    zona.borrado = False
    db.commit()
    return {"message": "Zona eliminada correctamente"}


def eliminar_zona_permanente(db: Session, zona_id: int):
    """
    Eliminación física de una zona de la base de datos
    """
    zona = obtener_zona_por_id(db, zona_id)
    db.delete(zona)
    db.commit()
    return {"message": "Zona eliminada permanentemente"}

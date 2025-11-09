# app/servicios/revision_reporte_servicio.py
from sqlalchemy.orm import Session
from app.modelos.revision_reporte_modelo import RevisionReporte
from app.esquemas.revision_reporte_esquema import RevisionReporteCreate, RevisionReporteUpdate
from fastapi import HTTPException, status
from datetime import date

def crear_revision(db: Session, revision: RevisionReporteCreate):
    """
    Crea una nueva revisión de reporte en la base de datos
    """
    nueva_revision = RevisionReporte(**revision.dict())
    db.add(nueva_revision)
    db.commit()
    db.refresh(nueva_revision)
    return nueva_revision

def obtener_revisiones(db: Session, skip: int = 0, limit: int = 100):
    """
    Obtiene todas las revisiones (no borradas por defecto)
    """
    return db.query(RevisionReporte).filter(RevisionReporte.borrado == True).offset(skip).limit(limit).all()

def obtener_revisiones_por_supervisor(db: Session, supervisor_id: int, skip: int = 0, limit: int = 100):
    """
    Obtiene todas las revisiones realizadas por un supervisor específico
    """
    return db.query(RevisionReporte).filter(
        RevisionReporte.id_Supervisor == supervisor_id,
        RevisionReporte.borrado == True
    ).offset(skip).limit(limit).all()

def obtener_revisiones_por_reporte(db: Session, reporte_id: int, skip: int = 0, limit: int = 100):
    """
    Obtiene todas las revisiones de un reporte específico
    """
    return db.query(RevisionReporte).filter(
        RevisionReporte.id_reporte == reporte_id,
        RevisionReporte.borrado == True
    ).offset(skip).limit(limit).all()

def obtener_revisiones_por_fecha(db: Session, fecha_inicio: date, fecha_fin: date, skip: int = 0, limit: int = 100):
    """
    Obtiene todas las revisiones entre dos fechas
    """
    return db.query(RevisionReporte).filter(
        RevisionReporte.fecha_revision >= fecha_inicio,
        RevisionReporte.fecha_revision <= fecha_fin,
        RevisionReporte.borrado == True
    ).offset(skip).limit(limit).all()

def obtener_revision_por_id(db: Session, revision_id: int):
    """
    Obtiene una revisión por su ID
    """
    revision = db.query(RevisionReporte).filter(RevisionReporte.id_revisionreporte == revision_id).first()
    if not revision:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Revisión no encontrada"
        )
    return revision

def actualizar_revision(db: Session, revision_id: int, revision_update: RevisionReporteUpdate):
    """
    Actualiza los datos de una revisión
    """
    revision = obtener_revision_por_id(db, revision_id)
    
    # Actualizar solo los campos que no son None
    for campo, valor in revision_update.dict(exclude_unset=True).items():
        setattr(revision, campo, valor)
    
    db.commit()
    db.refresh(revision)
    return revision

def contar_revisiones_por_supervisor(db: Session, supervisor_id: int):
    """
    Cuenta el total de revisiones realizadas por un supervisor
    """
    total = db.query(RevisionReporte).filter(
        RevisionReporte.id_Supervisor == supervisor_id,
        RevisionReporte.borrado == True
    ).count()
    
    return {"supervisor_id": supervisor_id, "total_revisiones": total}

def contar_revisiones_por_reporte(db: Session, reporte_id: int):
    """
    Cuenta el total de revisiones de un reporte
    """
    total = db.query(RevisionReporte).filter(
        RevisionReporte.id_reporte == reporte_id,
        RevisionReporte.borrado == True
    ).count()
    
    return {"reporte_id": reporte_id, "total_revisiones": total}

def obtener_ultima_revision_reporte(db: Session, reporte_id: int):
    """
    Obtiene la última revisión realizada a un reporte
    """
    revision = db.query(RevisionReporte).filter(
        RevisionReporte.id_reporte == reporte_id,
        RevisionReporte.borrado == True
    ).order_by(RevisionReporte.fecha_revision.desc()).first()
    
    if not revision:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No se encontraron revisiones para este reporte"
        )
    return revision

def eliminar_revision(db: Session, revision_id: int):
    """
    Eliminación lógica de una revisión (marca borrado = False)
    """
    revision = obtener_revision_por_id(db, revision_id)
    revision.borrado = False
    db.commit()
    return {"message": "Revisión eliminada correctamente"}

def eliminar_revision_permanente(db: Session, revision_id: int):
    """
    Eliminación física de una revisión de la base de datos
    """
    revision = obtener_revision_por_id(db, revision_id)
    db.delete(revision)
    db.commit()
    return {"message": "Revisión eliminada permanentemente"}
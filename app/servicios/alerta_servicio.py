from sqlalchemy.orm import Session
from app.modelos.alerta_modelo import Alerta
from app.esquemas.alerta_esquema import AlertaCreate, AlertaUpdate
from fastapi import HTTPException, status
from datetime import date

def crear_alerta(db: Session, alerta: AlertaCreate):
    """
    Crea una nueva alerta en la base de datos
    """
    nueva_alerta = Alerta(**alerta.dict())
    db.add(nueva_alerta)
    db.commit()
    db.refresh(nueva_alerta)
    return nueva_alerta

def obtener_alertas(db: Session, skip: int = 0, limit: int = 100):
    """
    Obtiene todas las alertas (no borradas por defecto)
    """
    return db.query(Alerta).filter(Alerta.borrado == True).offset(skip).limit(limit).all()

def obtener_alertas_por_supervisor(db: Session, supervisor_id: int, skip: int = 0, limit: int = 100):
    """
    Obtiene todas las alertas asignadas a un supervisor
    """
    return db.query(Alerta).filter(
        Alerta.id_supervisor == supervisor_id,
        Alerta.borrado == True
    ).offset(skip).limit(limit).all()

def obtener_alertas_por_evento(db: Session, evento_id: int, skip: int = 0, limit: int = 100):
    """
    Obtiene todas las alertas relacionadas a un evento específico
    """
    return db.query(Alerta).filter(
        Alerta.id_evento == evento_id,
        Alerta.borrado == True
    ).offset(skip).limit(limit).all()

def obtener_alertas_por_reporte(db: Session, reporte_id: int, skip: int = 0, limit: int = 100):
    """
    Obtiene todas las alertas relacionadas a un reporte específico
    """
    return db.query(Alerta).filter(
        Alerta.id_reporte == reporte_id,
        Alerta.borrado == True
    ).offset(skip).limit(limit).all()

def obtener_alertas_por_estado(db: Session, estado: str, skip: int = 0, limit: int = 100):
    """
    Obtiene todas las alertas con un estado específico (pendiente, en proceso, resuelta, etc.)
    """
    return db.query(Alerta).filter(
        Alerta.estado == estado,
        Alerta.borrado == True
    ).offset(skip).limit(limit).all()

def obtener_alertas_por_nivel_riesgo(db: Session, nivel_riesgo: str, skip: int = 0, limit: int = 100):
    """
    Obtiene todas las alertas con un nivel de riesgo específico (bajo, medio, alto, crítico)
    """
    return db.query(Alerta).filter(
        Alerta.nivelRiesgo == nivel_riesgo,
        Alerta.borrado == True
    ).offset(skip).limit(limit).all()

def obtener_alertas_por_tipo(db: Session, tipo_alerta: str, skip: int = 0, limit: int = 100):
    """
    Obtiene todas las alertas de un tipo específico
    """
    return db.query(Alerta).filter(
        Alerta.tipoAlerta == tipo_alerta,
        Alerta.borrado == True
    ).offset(skip).limit(limit).all()

def obtener_alertas_por_fecha(db: Session, fecha_inicio: date, fecha_fin: date, skip: int = 0, limit: int = 100):
    """
    Obtiene todas las alertas entre dos fechas
    """
    return db.query(Alerta).filter(
        Alerta.fechaHora >= fecha_inicio,
        Alerta.fechaHora <= fecha_fin,
        Alerta.borrado == True
    ).offset(skip).limit(limit).all()

def obtener_alerta_por_id(db: Session, alerta_id: int):
    """
    Obtiene una alerta por su ID
    """
    alerta = db.query(Alerta).filter(Alerta.id_Alerta == alerta_id).first()
    if not alerta:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Alerta no encontrada"
        )
    return alerta

def actualizar_alerta(db: Session, alerta_id: int, alerta_update: AlertaUpdate):
    """
    Actualiza los datos de una alerta
    """
    alerta = obtener_alerta_por_id(db, alerta_id)
    
    # Actualizar solo los campos que no son None
    for campo, valor in alerta_update.dict(exclude_unset=True).items():
        setattr(alerta, campo, valor)
    
    db.commit()
    db.refresh(alerta)
    return alerta

def cambiar_estado_alerta(db: Session, alerta_id: int, nuevo_estado: str):
    """
    Cambia el estado de una alerta
    """
    alerta = obtener_alerta_por_id(db, alerta_id)
    alerta.estado = nuevo_estado
    db.commit()
    db.refresh(alerta)
    return alerta

def asignar_supervisor_alerta(db: Session, alerta_id: int, supervisor_id: int):
    """
    Asigna o reasigna un supervisor a una alerta
    """
    alerta = obtener_alerta_por_id(db, alerta_id)
    alerta.id_supervisor = supervisor_id
    db.commit()
    db.refresh(alerta)
    return alerta

def obtener_alertas_criticas(db: Session, skip: int = 0, limit: int = 100):
    """
    Obtiene todas las alertas críticas (nivel de riesgo crítico o alto) que están pendientes
    """
    return db.query(Alerta).filter(
        Alerta.nivelRiesgo.in_(["crítico", "alto"]),
        Alerta.estado == "pendiente",
        Alerta.borrado == True
    ).offset(skip).limit(limit).all()

def eliminar_alerta(db: Session, alerta_id: int):
    """
    Eliminación lógica de una alerta (marca borrado = False)
    """
    alerta = obtener_alerta_por_id(db, alerta_id)
    alerta.borrado = False
    db.commit()
    return {"message": "Alerta eliminada correctamente"}

def eliminar_alerta_permanente(db: Session, alerta_id: int):
    """
    Eliminación física de una alerta de la base de datos
    """
    alerta = obtener_alerta_por_id(db, alerta_id)
    db.delete(alerta)
    db.commit()
    return {"message": "Alerta eliminada permanentemente"}
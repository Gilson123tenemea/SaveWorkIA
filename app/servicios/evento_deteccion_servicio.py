# app/servicios/evento_deteccion_servicio.py
from sqlalchemy.orm import Session
from app.modelos.evento_deteccion_modelo import EventoDeteccion
from app.esquemas.evento_deteccion_esquema import EventoDeteccionCreate, EventoDeteccionUpdate
from fastapi import HTTPException, status
from datetime import date

def crear_evento(db: Session, evento: EventoDeteccionCreate):
    """
    Crea un nuevo evento de detección en la base de datos
    """
    nuevo_evento = EventoDeteccion(**evento.dict())
    db.add(nuevo_evento)
    db.commit()
    db.refresh(nuevo_evento)
    return nuevo_evento

def obtener_eventos(db: Session, skip: int = 0, limit: int = 100):
    """
    Obtiene todos los eventos (no borrados por defecto)
    """
    return db.query(EventoDeteccion).filter(EventoDeteccion.borrado == True).offset(skip).limit(limit).all()

def obtener_eventos_por_zona(db: Session, zona_id: int, skip: int = 0, limit: int = 100):
    """
    Obtiene todos los eventos de una zona específica
    """
    return db.query(EventoDeteccion).filter(
        EventoDeteccion.id_zona == zona_id,
        EventoDeteccion.borrado == True
    ).offset(skip).limit(limit).all()

def obtener_eventos_por_camara(db: Session, camara_id: int, skip: int = 0, limit: int = 100):
    """
    Obtiene todos los eventos capturados por una cámara específica
    """
    return db.query(EventoDeteccion).filter(
        EventoDeteccion.id_camara == camara_id,
        EventoDeteccion.borrado == True
    ).offset(skip).limit(limit).all()

def obtener_eventos_por_trabajador(db: Session, trabajador_id: int, skip: int = 0, limit: int = 100):
    """
    Obtiene todos los eventos relacionados a un trabajador específico
    """
    return db.query(EventoDeteccion).filter(
        EventoDeteccion.id_Trabajador == trabajador_id,
        EventoDeteccion.borrado == True
    ).offset(skip).limit(limit).all()

def obtener_eventos_por_reporte(db: Session, reporte_id: int, skip: int = 0, limit: int = 100):
    """
    Obtiene todos los eventos relacionados a un reporte específico
    """
    return db.query(EventoDeteccion).filter(
        EventoDeteccion.id_reporte == reporte_id,
        EventoDeteccion.borrado == True
    ).offset(skip).limit(limit).all()

def obtener_eventos_por_tipo(db: Session, tipo_evento: str, skip: int = 0, limit: int = 100):
    """
    Obtiene todos los eventos de un tipo específico
    """
    return db.query(EventoDeteccion).filter(
        EventoDeteccion.tipo_evento == tipo_evento,
        EventoDeteccion.borrado == True
    ).offset(skip).limit(limit).all()

def obtener_eventos_por_fecha(db: Session, fecha_inicio: date, fecha_fin: date, skip: int = 0, limit: int = 100):
    """
    Obtiene todos los eventos entre dos fechas
    """
    return db.query(EventoDeteccion).filter(
        EventoDeteccion.fecha >= fecha_inicio,
        EventoDeteccion.fecha <= fecha_fin,
        EventoDeteccion.borrado == True
    ).offset(skip).limit(limit).all()

def obtener_eventos_por_confianza(db: Session, confianza_minima: str, skip: int = 0, limit: int = 100):
    """
    Obtiene todos los eventos con un nivel de confianza específico o superior
    """
    return db.query(EventoDeteccion).filter(
        EventoDeteccion.confianza >= confianza_minima,
        EventoDeteccion.borrado == True
    ).offset(skip).limit(limit).all()

def obtener_evento_por_id(db: Session, evento_id: int):
    """
    Obtiene un evento por su ID
    """
    evento = db.query(EventoDeteccion).filter(EventoDeteccion.id_evento == evento_id).first()
    if not evento:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Evento no encontrado"
        )
    return evento

def actualizar_evento(db: Session, evento_id: int, evento_update: EventoDeteccionUpdate):
    """
    Actualiza los datos de un evento
    """
    evento = obtener_evento_por_id(db, evento_id)
    
    # Actualizar solo los campos que no son None
    for campo, valor in evento_update.dict(exclude_unset=True).items():
        setattr(evento, campo, valor)
    
    db.commit()
    db.refresh(evento)
    return evento

def obtener_estadisticas_eventos_por_zona(db: Session, zona_id: int):
    """
    Obtiene estadísticas de eventos por zona
    """
    total_eventos = db.query(EventoDeteccion).filter(
        EventoDeteccion.id_zona == zona_id,
        EventoDeteccion.borrado == True
    ).count()
    
    eventos_por_tipo = db.query(
        EventoDeteccion.tipo_evento,
        db.func.count(EventoDeteccion.id_evento)
    ).filter(
        EventoDeteccion.id_zona == zona_id,
        EventoDeteccion.borrado == True
    ).group_by(EventoDeteccion.tipo_evento).all()
    
    return {
        "zona_id": zona_id,
        "total_eventos": total_eventos,
        "eventos_por_tipo": [{"tipo": tipo, "cantidad": cantidad} for tipo, cantidad in eventos_por_tipo]
    }

def obtener_estadisticas_eventos_por_camara(db: Session, camara_id: int):
    """
    Obtiene estadísticas de eventos por cámara
    """
    total_eventos = db.query(EventoDeteccion).filter(
        EventoDeteccion.id_camara == camara_id,
        EventoDeteccion.borrado == True
    ).count()
    
    eventos_por_tipo = db.query(
        EventoDeteccion.tipo_evento,
        db.func.count(EventoDeteccion.id_evento)
    ).filter(
        EventoDeteccion.id_camara == camara_id,
        EventoDeteccion.borrado == True
    ).group_by(EventoDeteccion.tipo_evento).all()
    
    return {
        "camara_id": camara_id,
        "total_eventos": total_eventos,
        "eventos_por_tipo": [{"tipo": tipo, "cantidad": cantidad} for tipo, cantidad in eventos_por_tipo]
    }

def eliminar_evento(db: Session, evento_id: int):
    """
    Eliminación lógica de un evento (marca borrado = False)
    """
    evento = obtener_evento_por_id(db, evento_id)
    evento.borrado = False
    db.commit()
    return {"message": "Evento eliminado correctamente"}

def eliminar_evento_permanente(db: Session, evento_id: int):
    """
    Eliminación física de un evento de la base de datos
    """
    evento = obtener_evento_por_id(db, evento_id)
    db.delete(evento)
    db.commit()
    return {"message": "Evento eliminado permanentemente"}
# app/routers/evento_deteccion_router.py
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.config import SessionLocal
from app.esquemas.evento_deteccion_esquema import EventoDeteccionCreate, EventoDeteccionResponse, EventoDeteccionUpdate
from app.servicios import evento_deteccion_servicio
from datetime import date

router = APIRouter(prefix="/eventos", tags=["Eventos de Detección"])

# Dependencia para obtener la sesión de BD
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/", response_model=EventoDeteccionResponse, status_code=201)
def crear_evento(evento: EventoDeteccionCreate, db: Session = Depends(get_db)):
    """
    Crea un nuevo evento de detección en el sistema
    """
    return evento_deteccion_servicio.crear_evento(db, evento)

@router.get("/", response_model=list[EventoDeteccionResponse])
def listar_eventos(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """
    Lista todos los eventos activos (no eliminados)
    """
    return evento_deteccion_servicio.obtener_eventos(db, skip, limit)

@router.get("/zona/{zona_id}", response_model=list[EventoDeteccionResponse])
def listar_eventos_por_zona(
    zona_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """
    Lista todos los eventos de una zona específica
    """
    return evento_deteccion_servicio.obtener_eventos_por_zona(db, zona_id, skip, limit)

@router.get("/camara/{camara_id}", response_model=list[EventoDeteccionResponse])
def listar_eventos_por_camara(
    camara_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """
    Lista todos los eventos capturados por una cámara específica
    """
    return evento_deteccion_servicio.obtener_eventos_por_camara(db, camara_id, skip, limit)

@router.get("/trabajador/{trabajador_id}", response_model=list[EventoDeteccionResponse])
def listar_eventos_por_trabajador(
    trabajador_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """
    Lista todos los eventos relacionados a un trabajador específico
    """
    return evento_deteccion_servicio.obtener_eventos_por_trabajador(db, trabajador_id, skip, limit)

@router.get("/reporte/{reporte_id}", response_model=list[EventoDeteccionResponse])
def listar_eventos_por_reporte(
    reporte_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """
    Lista todos los eventos relacionados a un reporte específico
    """
    return evento_deteccion_servicio.obtener_eventos_por_reporte(db, reporte_id, skip, limit)

@router.get("/tipo/{tipo_evento}", response_model=list[EventoDeteccionResponse])
def listar_eventos_por_tipo(
    tipo_evento: str,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """
    Lista todos los eventos de un tipo específico
    Ejemplos: caida, intruso, zona_restringida, sin_epp, accidente
    """
    return evento_deteccion_servicio.obtener_eventos_por_tipo(db, tipo_evento, skip, limit)

@router.get("/fecha-rango", response_model=list[EventoDeteccionResponse])
def listar_eventos_por_fecha(
    fecha_inicio: date = Query(..., description="Fecha de inicio (YYYY-MM-DD)"),
    fecha_fin: date = Query(..., description="Fecha de fin (YYYY-MM-DD)"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """
    Lista todos los eventos entre dos fechas
    """
    return evento_deteccion_servicio.obtener_eventos_por_fecha(db, fecha_inicio, fecha_fin, skip, limit)

@router.get("/confianza/{confianza_minima}", response_model=list[EventoDeteccionResponse])
def listar_eventos_por_confianza(
    confianza_minima: str,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """
    Lista todos los eventos con un nivel de confianza específico o superior
    """
    return evento_deteccion_servicio.obtener_eventos_por_confianza(db, confianza_minima, skip, limit)

@router.get("/{evento_id}", response_model=EventoDeteccionResponse)
def obtener_evento(evento_id: int, db: Session = Depends(get_db)):
    """
    Obtiene un evento específico por su ID
    """
    return evento_deteccion_servicio.obtener_evento_por_id(db, evento_id)

@router.get("/estadisticas/zona/{zona_id}")
def obtener_estadisticas_zona(zona_id: int, db: Session = Depends(get_db)):
    """
    Obtiene estadísticas de eventos por zona
    """
    return evento_deteccion_servicio.obtener_estadisticas_eventos_por_zona(db, zona_id)

@router.get("/estadisticas/camara/{camara_id}")
def obtener_estadisticas_camara(camara_id: int, db: Session = Depends(get_db)):
    """
    Obtiene estadísticas de eventos por cámara
    """
    return evento_deteccion_servicio.obtener_estadisticas_eventos_por_camara(db, camara_id)

@router.put("/{evento_id}", response_model=EventoDeteccionResponse)
def actualizar_evento(
    evento_id: int,
    evento_update: EventoDeteccionUpdate,
    db: Session = Depends(get_db)
):
    """
    Actualiza los datos de un evento
    """
    return evento_deteccion_servicio.actualizar_evento(db, evento_id, evento_update)

@router.delete("/{evento_id}")
def eliminar_evento(evento_id: int, db: Session = Depends(get_db)):
    """
    Elimina lógicamente un evento (marca como borrado)
    """
    return evento_deteccion_servicio.eliminar_evento(db, evento_id)

@router.delete("/{evento_id}/permanente")
def eliminar_evento_permanente(evento_id: int, db: Session = Depends(get_db)):
    """
    Elimina físicamente un evento de la base de datos
    ⚠️ Esta acción es irreversible
    """
    return evento_deteccion_servicio.eliminar_evento_permanente(db, evento_id)
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.config import SessionLocal
from app.esquemas.alerta_esquema import AlertaCreate, AlertaResponse, AlertaUpdate
from app.servicios import alerta_servicio
from datetime import date

router = APIRouter(prefix="/alertas", tags=["Alertas"])

# Dependencia para obtener la sesión de BD
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/", response_model=AlertaResponse, status_code=201)
def crear_alerta(alerta: AlertaCreate, db: Session = Depends(get_db)):
    """
    Crea una nueva alerta en el sistema
    """
    return alerta_servicio.crear_alerta(db, alerta)

@router.get("/", response_model=list[AlertaResponse])
def listar_alertas(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """
    Lista todas las alertas activas (no eliminadas)
    """
    return alerta_servicio.obtener_alertas(db, skip, limit)

@router.get("/criticas", response_model=list[AlertaResponse])
def listar_alertas_criticas(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """
    Lista todas las alertas críticas pendientes (nivel de riesgo crítico o alto)
    """
    return alerta_servicio.obtener_alertas_criticas(db, skip, limit)

@router.get("/supervisor/{supervisor_id}", response_model=list[AlertaResponse])
def listar_alertas_por_supervisor(
    supervisor_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """
    Lista todas las alertas asignadas a un supervisor
    """
    return alerta_servicio.obtener_alertas_por_supervisor(db, supervisor_id, skip, limit)

@router.get("/evento/{evento_id}", response_model=list[AlertaResponse])
def listar_alertas_por_evento(
    evento_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """
    Lista todas las alertas relacionadas a un evento específico
    """
    return alerta_servicio.obtener_alertas_por_evento(db, evento_id, skip, limit)

@router.get("/reporte/{reporte_id}", response_model=list[AlertaResponse])
def listar_alertas_por_reporte(
    reporte_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """
    Lista todas las alertas relacionadas a un reporte específico
    """
    return alerta_servicio.obtener_alertas_por_reporte(db, reporte_id, skip, limit)

@router.get("/estado/{estado}", response_model=list[AlertaResponse])
def listar_alertas_por_estado(
    estado: str,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """
    Lista todas las alertas con un estado específico
    Ejemplos: pendiente, en_proceso, resuelta, cerrada
    """
    return alerta_servicio.obtener_alertas_por_estado(db, estado, skip, limit)

@router.get("/nivel-riesgo/{nivel_riesgo}", response_model=list[AlertaResponse])
def listar_alertas_por_nivel_riesgo(
    nivel_riesgo: str,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """
    Lista todas las alertas con un nivel de riesgo específico
    Ejemplos: bajo, medio, alto, crítico
    """
    return alerta_servicio.obtener_alertas_por_nivel_riesgo(db, nivel_riesgo, skip, limit)

@router.get("/tipo/{tipo_alerta}", response_model=list[AlertaResponse])
def listar_alertas_por_tipo(
    tipo_alerta: str,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """
    Lista todas las alertas de un tipo específico
    Ejemplos: intruso, accidente, emergencia, sospechoso
    """
    return alerta_servicio.obtener_alertas_por_tipo(db, tipo_alerta, skip, limit)

@router.get("/fecha-rango", response_model=list[AlertaResponse])
def listar_alertas_por_fecha(
    fecha_inicio: date = Query(..., description="Fecha de inicio (YYYY-MM-DD)"),
    fecha_fin: date = Query(..., description="Fecha de fin (YYYY-MM-DD)"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """
    Lista todas las alertas entre dos fechas
    """
    return alerta_servicio.obtener_alertas_por_fecha(db, fecha_inicio, fecha_fin, skip, limit)

@router.get("/{alerta_id}", response_model=AlertaResponse)
def obtener_alerta(alerta_id: int, db: Session = Depends(get_db)):
    """
    Obtiene una alerta específica por su ID
    """
    return alerta_servicio.obtener_alerta_por_id(db, alerta_id)

@router.put("/{alerta_id}", response_model=AlertaResponse)
def actualizar_alerta(
    alerta_id: int,
    alerta_update: AlertaUpdate,
    db: Session = Depends(get_db)
):
    """
    Actualiza los datos de una alerta
    """
    return alerta_servicio.actualizar_alerta(db, alerta_id, alerta_update)

@router.patch("/{alerta_id}/estado", response_model=AlertaResponse)
def cambiar_estado_alerta(
    alerta_id: int,
    nuevo_estado: str = Query(..., description="Nuevo estado de la alerta"),
    db: Session = Depends(get_db)
):
    """
    Cambia el estado de una alerta
    Ejemplos: pendiente, en_proceso, resuelta, cerrada
    """
    return alerta_servicio.cambiar_estado_alerta(db, alerta_id, nuevo_estado)

@router.patch("/{alerta_id}/asignar-supervisor", response_model=AlertaResponse)
def asignar_supervisor_alerta(
    alerta_id: int,
    supervisor_id: int = Query(..., description="ID del supervisor a asignar"),
    db: Session = Depends(get_db)
):
    """
    Asigna o reasigna un supervisor a una alerta
    """
    return alerta_servicio.asignar_supervisor_alerta(db, alerta_id, supervisor_id)

@router.delete("/{alerta_id}")
def eliminar_alerta(alerta_id: int, db: Session = Depends(get_db)):
    """
    Elimina lógicamente una alerta (marca como borrado)
    """
    return alerta_servicio.eliminar_alerta(db, alerta_id)

@router.delete("/{alerta_id}/permanente")
def eliminar_alerta_permanente(alerta_id: int, db: Session = Depends(get_db)):
    """
    Elimina físicamente una alerta de la base de datos
    ⚠️ Esta acción es irreversible
    """
    return alerta_servicio.eliminar_alerta_permanente(db, alerta_id)
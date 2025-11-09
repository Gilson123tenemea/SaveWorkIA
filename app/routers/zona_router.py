from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.config import SessionLocal
from app.esquemas.zona_esquema import ZonaCreate, ZonaResponse, ZonaUpdate
from app.servicios import zona_servicio

router = APIRouter(prefix="/zonas", tags=["Zonas"])

# Dependencia para obtener la sesión de BD
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/", response_model=ZonaResponse, status_code=201)
def crear_zona(zona: ZonaCreate, db: Session = Depends(get_db)):
    """
    Crea una nueva zona en el sistema
    """
    return zona_servicio.crear_zona(db, zona)

@router.get("/", response_model=list[ZonaResponse])
def listar_zonas(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """
    Lista todas las zonas activas (no eliminadas)
    """
    return zona_servicio.obtener_zonas(db, skip, limit)

@router.get("/empresa/{empresa_id}", response_model=list[ZonaResponse])
def listar_zonas_por_empresa(
    empresa_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """
    Lista todas las zonas de una empresa específica
    """
    return zona_servicio.obtener_zonas_por_empresa(db, empresa_id, skip, limit)

@router.get("/administrador/{administrador_id}", response_model=list[ZonaResponse])
def listar_zonas_por_administrador(
    administrador_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """
    Lista todas las zonas asignadas a un administrador
    """
    return zona_servicio.obtener_zonas_por_administrador(db, administrador_id, skip, limit)

@router.get("/{zona_id}", response_model=ZonaResponse)
def obtener_zona(zona_id: int, db: Session = Depends(get_db)):
    """
    Obtiene una zona específica por su ID
    """
    return zona_servicio.obtener_zona_por_id(db, zona_id)

@router.put("/{zona_id}", response_model=ZonaResponse)
def actualizar_zona(
    zona_id: int,
    zona_update: ZonaUpdate,
    db: Session = Depends(get_db)
):
    """
    Actualiza los datos de una zona
    """
    return zona_servicio.actualizar_zona(db, zona_id, zona_update)

@router.delete("/{zona_id}")
def eliminar_zona(zona_id: int, db: Session = Depends(get_db)):
    """
    Elimina lógicamente una zona (marca como borrado)
    """
    return zona_servicio.eliminar_zona(db, zona_id)

@router.delete("/{zona_id}/permanente")
def eliminar_zona_permanente(zona_id: int, db: Session = Depends(get_db)):
    """
    Elimina físicamente una zona de la base de datos
    ⚠️ Esta acción es irreversible
    """
    return zona_servicio.eliminar_zona_permanente(db, zona_id)
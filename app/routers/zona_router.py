from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.config import SessionLocal
from app.esquemas.zona_esquema import (
    ZonaCreate,
    ZonaResponse,
    ZonaUpdate,
    ZonaConDetalles,
)
from app.servicios import zona_servicio

router = APIRouter(prefix="/zonas", tags=["Zonas"])


# ---------------------------------------------------------
# DB
# ---------------------------------------------------------
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ---------------------------------------------------------
# PRE-FLIGHT
# ---------------------------------------------------------
@router.options("/{zona_id}")
async def options_zona(zona_id: int):
    return {"ok": True}

@router.options("/")
async def options_root():
    return {"ok": True}


# ---------------------------------------------------------
# CREATE
# ---------------------------------------------------------
@router.post("/", response_model=ZonaResponse, status_code=201)
def crear_zona(zona: ZonaCreate, db: Session = Depends(get_db)):
    return zona_servicio.crear_zona(db, zona)


# ---------------------------------------------------------
# LISTAR ZONAS
# ---------------------------------------------------------
@router.get("/", response_model=list[ZonaResponse])
def listar_zonas(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return zona_servicio.obtener_zonas(db, skip, limit)


# ---------------------------------------------------------
# LISTAR POR EMPRESA
# ---------------------------------------------------------
@router.get("/empresa/{empresa_id}", response_model=list[ZonaConDetalles])
def listar_zonas_por_empresa(empresa_id: int, db: Session = Depends(get_db)):
    return zona_servicio.obtener_zonas_por_empresa_con_detalles(db, empresa_id)


# ---------------------------------------------------------
# LISTAR POR ADMIN
# ---------------------------------------------------------
@router.get("/administrador/{admin_id}", response_model=list[ZonaResponse])
def listar_zonas_por_admin(admin_id: int, db: Session = Depends(get_db)):
    return zona_servicio.obtener_zonas_por_administrador(db, admin_id)


# ---------------------------------------------------------
# GET POR ID  (DEBE IR AL FINAL)
# ---------------------------------------------------------
@router.get("/{zona_id}", response_model=ZonaResponse)
def obtener_zona(zona_id: int, db: Session = Depends(get_db)):
    return zona_servicio.obtener_zona_por_id(db, zona_id)


# ---------------------------------------------------------
# PUT  (DEBE IR AL FINAL)
# ---------------------------------------------------------
@router.put("/{zona_id}", response_model=ZonaResponse)
def actualizar_zona(zona_id: int, zona_update: ZonaUpdate, db: Session = Depends(get_db)):
    return zona_servicio.actualizar_zona(db, zona_id, zona_update)


# ---------------------------------------------------------
# DELETE (DEBE IR AL FINAL)
# ---------------------------------------------------------
@router.delete("/{zona_id}")
def eliminar_zona(zona_id: int, db: Session = Depends(get_db)):
    return zona_servicio.eliminar_zona(db, zona_id)


@router.delete("/{zona_id}/permanente")
def eliminar_zona_permanente(zona_id: int, db: Session = Depends(get_db)):
    return zona_servicio.eliminar_zona_permanente(db, zona_id)

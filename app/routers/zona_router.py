from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.config import SessionLocal
from app.esquemas.zona_esquema import ZonaCreate, ZonaResponse, ZonaUpdate
from app.servicios import zona_servicio
from app.esquemas.zona_esquema import ZonaConDetalles

router = APIRouter(prefix="/zonas", tags=["Zonas"])


# ============================================================
# 🔹 DEPENDENCIA DE BD (NO SE TOCA)
# ============================================================
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ============================================================
# 🔹 CREAR ZONA
# ============================================================
@router.post("/", response_model=ZonaResponse, status_code=201)
def crear_zona(zona: ZonaCreate, db: Session = Depends(get_db)):
    """
    Crea una nueva zona en el sistema.
    """
    return zona_servicio.crear_zona(db, zona)


# ============================================================
# 🔹 LISTAR TODAS LAS ZONAS
# ============================================================
@router.get("/", response_model=list[ZonaResponse])
def listar_zonas(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """
    Lista todas las zonas activas (borrado=True).
    """
    return zona_servicio.obtener_zonas(db, skip, limit)


# ============================================================
# 🔹 LISTAR ZONAS POR EMPRESA + DETALLES (Cámaras y Trabajadores)
# ============================================================
@router.get("/empresa/{empresa_id}", response_model=list[ZonaConDetalles])
def listar_zonas_por_empresa(empresa_id: int, db: Session = Depends(get_db)):
    return zona_servicio.obtener_zonas_por_empresa_con_detalles(db, empresa_id)


# ============================================================
# 🔹 LISTAR ZONAS POR ADMINISTRADOR
# ============================================================
@router.get("/administrador/{administrador_id}", response_model=list[ZonaResponse])
def listar_zonas_por_administrador(
    administrador_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """
    Lista todas las zonas asignadas a un administrador.
    """
    return zona_servicio.obtener_zonas_por_administrador(db, administrador_id, skip, limit)


# ============================================================
# 🔹 OBTENER ZONA POR ID
# ============================================================
@router.get("/{zona_id}", response_model=ZonaResponse)
def obtener_zona(zona_id: int, db: Session = Depends(get_db)):
    """
    Obtiene una zona específica por ID.
    """
    return zona_servicio.obtener_zona_por_id(db, zona_id)


# ============================================================
# 🔹 ACTUALIZAR ZONA
# ============================================================
@router.put("/{zona_id}", response_model=ZonaResponse)
def actualizar_zona(
    zona_id: int,
    zona_update: ZonaUpdate,
    db: Session = Depends(get_db)
):
    """
    Actualiza los datos de una zona.
    """
    return zona_servicio.actualizar_zona(db, zona_id, zona_update)


# ============================================================
# 🔹 ELIMINAR ZONA (LÓGICO)
# ============================================================
@router.delete("/{zona_id}")
def eliminar_zona(zona_id: int, db: Session = Depends(get_db)):
    """
    Elimina lógicamente una zona (borrado=False).
    ✔ Ahora valida que NO tenga cámaras activas.
    """
    return zona_servicio.eliminar_zona(db, zona_id)


# ============================================================
# 🔹 ELIMINACIÓN FÍSICA
# ============================================================
@router.delete("/{zona_id}/permanente")
def eliminar_zona_permanente(zona_id: int, db: Session = Depends(get_db)):
    """
    Eliminación física definitiva.
    ⚠️ Esta acción es irreversible.
    """
    return zona_servicio.eliminar_zona_permanente(db, zona_id)

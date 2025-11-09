from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.config import SessionLocal
from app.esquemas.empresa_esquema import EmpresaCreate, EmpresaResponse, EmpresaUpdate
from app.servicios import empresa_servicio

router = APIRouter(prefix="/empresas", tags=["Empresas"])

# Dependencia para obtener la sesión de BD
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/", response_model=EmpresaResponse, status_code=201)
def crear_empresa(empresa: EmpresaCreate, db: Session = Depends(get_db)):
    """
    Crea una nueva empresa en el sistema
    """
    return empresa_servicio.crear_empresa(db, empresa)

@router.get("/", response_model=list[EmpresaResponse])
def listar_empresas(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """
    Lista todas las empresas activas (no eliminadas)
    """
    return empresa_servicio.obtener_empresas(db, skip, limit)

@router.get("/{empresa_id}", response_model=EmpresaResponse)
def obtener_empresa(empresa_id: int, db: Session = Depends(get_db)):
    """
    Obtiene una empresa específica por su ID
    """
    return empresa_servicio.obtener_empresa_por_id(db, empresa_id)

@router.get("/ruc/{ruc}", response_model=EmpresaResponse)
def obtener_empresa_por_ruc(ruc: str, db: Session = Depends(get_db)):
    """
    Obtiene una empresa específica por su RUC
    """
    return empresa_servicio.obtener_empresa_por_ruc(db, ruc)

@router.put("/{empresa_id}", response_model=EmpresaResponse)
def actualizar_empresa(
    empresa_id: int,
    empresa_update: EmpresaUpdate,
    db: Session = Depends(get_db)
):
    """
    Actualiza los datos de una empresa
    """
    return empresa_servicio.actualizar_empresa(db, empresa_id, empresa_update)

@router.delete("/{empresa_id}")
def eliminar_empresa(empresa_id: int, db: Session = Depends(get_db)):
    """
    Elimina lógicamente una empresa (marca como borrado)
    """
    return empresa_servicio.eliminar_empresa(db, empresa_id)

@router.delete("/{empresa_id}/permanente")
def eliminar_empresa_permanente(empresa_id: int, db: Session = Depends(get_db)):
    """
    Elimina físicamente una empresa de la base de datos
    ⚠️ Esta acción es irreversible
    """
    return empresa_servicio.eliminar_empresa_permanente(db, empresa_id)
from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy.orm import Session
from app.config import SessionLocal
from app.esquemas.empresa_esquema import EmpresaCreate, EmpresaResponse, EmpresaUpdate
from app.servicios import empresa_servicio

router = APIRouter(prefix="/empresas", tags=["Empresas"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_client_ip(request: Request) -> str:
    """Obtiene la IP del cliente desde la request"""
    if "x-forwarded-for" in request.headers:
        return request.headers["x-forwarded-for"].split(",")[0]
    return request.client.host if request.client else "unknown"

@router.post("/", response_model=EmpresaResponse, status_code=201)
async def crear_empresa(
    empresa: EmpresaCreate, 
    request: Request,
    db: Session = Depends(get_db)
):
    ip_address = get_client_ip(request)
    # TODO: Obtener user_id y user_role del token de autenticación
    user_id = None
    user_role = None  # Ejemplo: "ADMIN", "SUPERADMIN", etc.
    
    return await empresa_servicio.crear_empresa(
        db, 
        empresa, 
        user_id=user_id,
        user_role=user_role,
        ip_address=ip_address
    )

@router.get("/", response_model=list[EmpresaResponse])
def listar_empresas(
    skip: int = Query(0, ge=0), 
    limit: int = Query(100, ge=1, le=100), 
    db: Session = Depends(get_db)
):
    return empresa_servicio.obtener_empresas(db, skip, limit)

@router.get("/{empresa_id}", response_model=EmpresaResponse)
def obtener_empresa(empresa_id: int, db: Session = Depends(get_db)):
    return empresa_servicio.obtener_empresa_por_id(db, empresa_id)

@router.get("/ruc/{ruc}", response_model=EmpresaResponse)
def obtener_empresa_por_ruc(ruc: str, db: Session = Depends(get_db)):
    return empresa_servicio.obtener_empresa_por_ruc(db, ruc)

@router.put("/{empresa_id}", response_model=EmpresaResponse)
async def actualizar_empresa(
    empresa_id: int, 
    empresa_update: EmpresaUpdate,
    request: Request,
    db: Session = Depends(get_db)
):
    ip_address = get_client_ip(request)
    user_id = None  # TODO: Obtener del JWT
    user_role = None
    
    return await empresa_servicio.actualizar_empresa(
        db, 
        empresa_id, 
        empresa_update,
        user_id=user_id,
        user_role=user_role,
        ip_address=ip_address
    )

@router.delete("/{empresa_id}")
async def eliminar_empresa(
    empresa_id: int,
    request: Request,
    db: Session = Depends(get_db)
):
    ip_address = get_client_ip(request)
    user_id = None  # TODO: Obtener del JWT
    user_role = None
    
    return await empresa_servicio.eliminar_empresa(
        db, 
        empresa_id,
        user_id=user_id,
        user_role=user_role,
        ip_address=ip_address
    )

@router.delete("/{empresa_id}/permanente")
async def eliminar_empresa_permanente(
    empresa_id: int,
    request: Request,
    db: Session = Depends(get_db)
):
    ip_address = get_client_ip(request)
    user_id = None  # TODO: Obtener del JWT
    user_role = None
    
    return await empresa_servicio.eliminar_empresa_permanente(
        db, 
        empresa_id,
        user_id=user_id,
        user_role=user_role,
        ip_address=ip_address
    )
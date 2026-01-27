from fastapi import APIRouter, Depends, Request, BackgroundTasks
from sqlalchemy.orm import Session
from app.config import SessionLocal
from app.esquemas.administrador_esquema import AdministradorCreate, LoginAdministrador
from app.servicios.administrador_servicio import crear_administrador, login_administrador

router = APIRouter(prefix="/administradores", tags=["Administrador"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/registrar")
def registrar_admin(
    request: AdministradorCreate, 
    db: Session = Depends(get_db),
    background_tasks: BackgroundTasks = BackgroundTasks()
):
    return crear_administrador(db, request, background_tasks)

@router.post("/login")
async def login_admin(
    request: LoginAdministrador, 
    db: Session = Depends(get_db),
    http_request: Request = None
):
    # Obtener IP del cliente
    ip_address = http_request.client.host if http_request else None
    return await login_administrador(db, request, ip_address)
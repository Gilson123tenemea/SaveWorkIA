from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.config import SessionLocal
from app.esquemas.supervisor_esquema import SupervisorCreate, LoginSupervisor
from app.servicios.supervisor_servicio import crear_supervisor, login_supervisor, listar_supervisores_activos, eliminar_supervisor, editar_supervisor, SupervisorUpdate

router = APIRouter(prefix="/supervisores", tags=["Supervisores"])

# Dependencia para la sesión de BD
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/registrar")
def registrar_supervisor(request: SupervisorCreate, db: Session = Depends(get_db)):
    return crear_supervisor(db, request)

@router.post("/login")
def login_supervisor_endpoint(request: LoginSupervisor, db: Session = Depends(get_db)):
    return login_supervisor(db, request)

@router.get("/listar")
def listar_supervisores(db: Session = Depends(get_db)):
    return listar_supervisores_activos(db)

# --- Nuevo endpoint: eliminado lógico ---
@router.delete("/eliminar/{id_supervisor}")
def eliminar_supervisor_endpoint(id_supervisor: int, db: Session = Depends(get_db)):
    return eliminar_supervisor(db, id_supervisor)

@router.put("/editar/{id_supervisor}")
def actualizar_supervisor(id_supervisor: int, request: SupervisorUpdate, db: Session = Depends(get_db)):
    return editar_supervisor(db, id_supervisor, request)
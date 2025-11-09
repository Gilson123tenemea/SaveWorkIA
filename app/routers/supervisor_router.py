from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.config import SessionLocal
from app.esquemas.supervisor_esquema import SupervisorCreate, SupervisorResponse
from app.servicios import supervisor_servicio

router = APIRouter(prefix="/supervisores", tags=["Supervisores"])

# Dependencia de sesión de BD
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/", response_model=SupervisorResponse)
def crear_supervisor(supervisor: SupervisorCreate, db: Session = Depends(get_db)):
    return supervisor_servicio.crear_supervisor(db, supervisor)

@router.get("/", response_model=list[SupervisorResponse])
def listar_supervisores(db: Session = Depends(get_db)):
    return supervisor_servicio.obtener_supervisores(db)

@router.get("/{supervisor_id}", response_model=SupervisorResponse)
def obtener_supervisor(supervisor_id: int, db: Session = Depends(get_db)):
    return supervisor_servicio.obtener_supervisor_por_id(db, supervisor_id)

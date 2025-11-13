from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.config import SessionLocal
from app.esquemas.inspector_esquema import InspectorCreate, LoginInspector
from app.servicios import inspector_servicio

router = APIRouter(prefix="/inspectores", tags=["Inspectores"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# --- Registrar ---
@router.post("/registrar")
def registrar_inspector(request: InspectorCreate, db: Session = Depends(get_db)):
    return inspector_servicio.crear_inspector(db, request)

# --- Listar activos ---
@router.get("/")
def listar_inspectores(db: Session = Depends(get_db)):
    return inspector_servicio.listar_inspectores(db)

# --- Editar ---
@router.put("/{id_inspector}")
def editar_inspector(id_inspector: int, request: InspectorCreate, db: Session = Depends(get_db)):
    return inspector_servicio.editar_inspector(db, id_inspector, request)

# --- Borrado lógico ---
@router.delete("/{id_inspector}")
def eliminar_inspector(id_inspector: int, db: Session = Depends(get_db)):
    return inspector_servicio.eliminar_inspector(db, id_inspector)

# --- Login ---
@router.post("/login")
def login_inspector(request: LoginInspector, db: Session = Depends(get_db)):
    return inspector_servicio.login_inspector(db, request)

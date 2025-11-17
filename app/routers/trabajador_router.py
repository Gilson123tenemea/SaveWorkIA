from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.config import SessionLocal



from app.esquemas.trabajador_esquema import (
    TrabajadorPersonaCreate,
    TrabajadorResponse
)
from app.servicios import trabajador_servicio

router = APIRouter(prefix="/trabajadores", tags=["Trabajadores"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# --------------------------------------------------
# CREAR PERSONA + TRABAJADOR
# --------------------------------------------------
@router.post("/", response_model=TrabajadorResponse)
def crear_trabajador(data: TrabajadorPersonaCreate, db: Session = Depends(get_db)):
    return trabajador_servicio.crear_trabajador_completo(db, data)


# --------------------------------------------------
# LISTAR
# --------------------------------------------------
@router.get("/", response_model=list[TrabajadorResponse])
def listar_trabajadores(db: Session = Depends(get_db)):
    return trabajador_servicio.obtener_trabajadores_completos(db)


# --------------------------------------------------
# OBTENER POR ID
# --------------------------------------------------
@router.get("/{id_trabajador}", response_model=TrabajadorResponse)
def obtener_trabajador(id_trabajador: int, db: Session = Depends(get_db)):
    return trabajador_servicio.obtener_trabajador_completo(db, id_trabajador)


# --------------------------------------------------
# EDITAR PERSONA + TRABAJADOR
# --------------------------------------------------
@router.put("/{id_trabajador}", response_model=TrabajadorResponse)
def editar_trabajador(id_trabajador: int, data: TrabajadorPersonaCreate, db: Session = Depends(get_db)):
    return trabajador_servicio.editar_trabajador_completo(db, id_trabajador, data)


# --------------------------------------------------
# BORRADO LÓGICO
# --------------------------------------------------
@router.put("/borrar/{id_trabajador}")
def borrar_trabajador(id_trabajador: int, db: Session = Depends(get_db)):
    return trabajador_servicio.borrado_logico_trabajador(db, id_trabajador)

# --------------------------------------------------
# LISTAR TRABAJADORES DE UN SUPERVISOR
# --------------------------------------------------
@router.get("/supervisor/{id_supervisor}", response_model=list[TrabajadorResponse])
def listar_trabajadores_por_supervisor(id_supervisor: int, db: Session = Depends(get_db)):
    return trabajador_servicio.obtener_trabajadores_por_supervisor(db, id_supervisor)

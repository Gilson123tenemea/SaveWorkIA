from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.config import SessionLocal
from app.esquemas.zona_epp_esquema import (
    ZonaEppCreate,
    ZonaEppResponse
)
from app.servicios import zona_epp_servicio
from app.esquemas.zona_epp_esquema import ZonaEppUpdateRequest


router = APIRouter(
    prefix="/zonas-epp",
    tags=["Zonas - EPP"]
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/", response_model=ZonaEppResponse)
def crear_epp_zona(data: ZonaEppCreate, db: Session = Depends(get_db)):
    return zona_epp_servicio.crear_epp_zona(db, data)

@router.get("/{id_zona}", response_model=list[ZonaEppResponse])
def listar_epp_por_zona(id_zona: int, db: Session = Depends(get_db)):
    return zona_epp_servicio.obtener_epp_por_zona(db, id_zona)

@router.put("/zona/{id_zona}")
def actualizar_epp_zona(
    id_zona: int,
    data: ZonaEppUpdateRequest,
    db: Session = Depends(get_db)
):
    return zona_epp_servicio.actualizar_epp_de_zona(
        db=db,
        id_zona=id_zona,
        epps=data.epps
    )

# app/rutas/ejemplo.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.config import get_db
from app.servicios import ejemplo_servicio
from app.esquemas.ejemplo_esquema import Ejemplo, EjemploCrear

router = APIRouter(prefix="/ejemplos", tags=["Ejemplos"])

@router.post("/", response_model=Ejemplo)
def crear_ejemplo_endpoint(ejemplo: EjemploCrear, db: Session = Depends(get_db)):
    return ejemplo_servicio.crear_ejemplo(db, ejemplo)

@router.get("/", response_model=list[Ejemplo])
def leer_ejemplos(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    return ejemplo_servicio.obtener_ejemplos(db, skip=skip, limit=limit)

@router.get("/{ejemplo_id}", response_model=Ejemplo)
def leer_ejemplo(ejemplo_id: int, db: Session = Depends(get_db)):
    db_obj = ejemplo_servicio.obtener_ejemplo(db, ejemplo_id)
    if not db_obj:
        raise HTTPException(status_code=404, detail="Ejemplo no encontrado")
    return db_obj

@router.delete("/{ejemplo_id}", response_model=Ejemplo)
def eliminar_ejemplo_endpoint(ejemplo_id: int, db: Session = Depends(get_db)):
    db_obj = ejemplo_servicio.eliminar_ejemplo(db, ejemplo_id)
    if not db_obj:
        raise HTTPException(status_code=404, detail="Ejemplo no encontrado")
    return db_obj

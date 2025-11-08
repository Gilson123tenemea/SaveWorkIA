# app/routers/persona_router.py
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.config import SessionLocal
from app.esquemas.persona_esquema import PersonaCreate, PersonaResponse
from app.servicios import persona_servicio

router = APIRouter(prefix="/personas", tags=["Personas"])

# Dependencia para obtener la sesión de BD
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/", response_model=PersonaResponse)
def crear_persona(persona: PersonaCreate, db: Session = Depends(get_db)):
    return persona_servicio.crear_persona(db, persona)

@router.get("/", response_model=list[PersonaResponse])
def listar_personas(db: Session = Depends(get_db)):
    return persona_servicio.obtener_personas(db)

@router.get("/{persona_id}", response_model=PersonaResponse)
def obtener_persona(persona_id: int, db: Session = Depends(get_db)):
    return persona_servicio.obtener_persona_por_id(db, persona_id)

# app/servicios/persona_servicio.py
from sqlalchemy.orm import Session
from app.modelos.persona import Persona
from app.esquemas.persona_esquema import PersonaCreate

def crear_persona(db: Session, persona: PersonaCreate):
    nueva_persona = Persona(**persona.dict())
    db.add(nueva_persona)
    db.commit()
    db.refresh(nueva_persona)
    return nueva_persona

def obtener_personas(db: Session):
    return db.query(Persona).all()

def obtener_persona_por_id(db: Session, persona_id: int):
    return db.query(Persona).filter(Persona.id == persona_id).first()

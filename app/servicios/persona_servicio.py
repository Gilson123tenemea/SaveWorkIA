from sqlalchemy.orm import Session
from fastapi import HTTPException
import base64

from app.modelos.persona import Persona   # 👈 IMPORT CORRECTO
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
    return db.query(Persona).filter(Persona.id_persona == persona_id).first()


def actualizar_foto_persona(db: Session, id_persona: int, foto_base64: str):
    persona = db.query(Persona).filter(Persona.id_persona == id_persona).first()

    if not persona:
        raise HTTPException(status_code=404, detail="Persona no encontrada")

    if not foto_base64:
        raise HTTPException(status_code=400, detail="No se recibió la imagen")

    try:
        # Esperamos algo tipo: "data:image/jpeg;base64,AAAAAA..."
        header, encoded = foto_base64.split(",", 1)
        foto_bytes = base64.b64decode(encoded)
    except Exception:
        raise HTTPException(status_code=400, detail="Formato de imagen inválido")

    persona.foto = foto_bytes
    db.commit()

    return {"mensaje": "Foto actualizada correctamente"}

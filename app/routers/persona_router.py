from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.config import SessionLocal
from app.esquemas.persona_esquema import PersonaCreate, PersonaResponse, FotoUpdate
from app.servicios import persona_servicio

router = APIRouter(prefix="/personas", tags=["Personas"])


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


# ⚠️ ESTE DEBE IR ANTES DEL GET /{persona_id}
@router.get("/buscar-por-correo")
def buscar_por_correo(correo: str, db: Session = Depends(get_db)):
    """
    🔍 Busca una persona activa por correo
    Ejemplo: GET /personas/buscar-por-correo?correo=freddy@admin.com
    """
    persona = persona_servicio.obtener_persona_por_correo(db, correo)
    
    if not persona:
        raise HTTPException(
            status_code=404,
            detail="No se encontró una persona registrada con ese correo"
        )
    
    return {
        "id_persona": persona.id_persona,
        "correo": persona.correo,
        "nombre": persona.nombre
    }


@router.get("/{persona_id}", response_model=PersonaResponse)
def obtener_persona(persona_id: int, db: Session = Depends(get_db)):
    persona = persona_servicio.obtener_persona_por_id(db, persona_id)
    if not persona:
        raise HTTPException(status_code=404, detail="Persona no encontrada")
    return persona


@router.put("/foto/{id_persona}")
def actualizar_foto(id_persona: int, data: FotoUpdate, db: Session = Depends(get_db)):
    return persona_servicio.actualizar_foto_persona(db, id_persona, data.fotoBase64)
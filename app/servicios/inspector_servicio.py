from sqlalchemy.orm import Session
from app.modelos.inspector import Inspector
from app.esquemas.inspector_esquema import InspectorCreate

def crear_inspector(db: Session, inspector: InspectorCreate):
    nuevo_inspector = Inspector(**inspector.dict())
    db.add(nuevo_inspector)
    db.commit()
    db.refresh(nuevo_inspector)
    return nuevo_inspector

def obtener_inspectores(db: Session):
    return db.query(Inspector).all()

def obtener_inspector_por_id(db: Session, inspector_id: int):
    return db.query(Inspector).filter(Inspector.id_inspector == inspector_id).first()

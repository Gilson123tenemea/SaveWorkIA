from sqlalchemy.orm import Session
from app.modelos.inspector_zona import InspectorZona
from app.esquemas.inspector_zona_esquema import InspectorZonaCreate

def crear_inspector_zona(db: Session, inspector_zona: InspectorZonaCreate):
    nueva_asignacion = InspectorZona(**inspector_zona.dict())
    db.add(nueva_asignacion)
    db.commit()
    db.refresh(nueva_asignacion)
    return nueva_asignacion

def obtener_inspector_zonas(db: Session):
    return db.query(InspectorZona).all()

def obtener_inspector_zona_por_id(db: Session, asignacion_id: int):
    return db.query(InspectorZona).filter(InspectorZona.id_inspector_zona == asignacion_id).first()

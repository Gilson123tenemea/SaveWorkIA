from sqlalchemy.orm import Session
from app.modelos.trabajador_zona import TrabajadorZona
from app.esquemas.trabajador_zona_esquema import TrabajadorZonaCreate

def crear_trabajador_zona(db: Session, trabajador_zona: TrabajadorZonaCreate):
    nueva_asignacion = TrabajadorZona(**trabajador_zona.dict())
    db.add(nueva_asignacion)
    db.commit()
    db.refresh(nueva_asignacion)
    return nueva_asignacion

def obtener_trabajador_zonas(db: Session):
    return db.query(TrabajadorZona).all()

def obtener_trabajador_zona_por_id(db: Session, asignacion_id: int):
    return db.query(TrabajadorZona).filter(TrabajadorZona.id_trabajador_zona == asignacion_id).first()

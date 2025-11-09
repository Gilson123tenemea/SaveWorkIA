from sqlalchemy.orm import Session
from app.modelos.reporte import Reporte
from app.esquemas.reporte_esquema import ReporteCreate

def crear_reporte(db: Session, reporte: ReporteCreate):
    nuevo_reporte = Reporte(**reporte.dict())
    db.add(nuevo_reporte)
    db.commit()
    db.refresh(nuevo_reporte)
    return nuevo_reporte

def obtener_reportes(db: Session):
    return db.query(Reporte).all()

def obtener_reporte_por_id(db: Session, reporte_id: int):
    return db.query(Reporte).filter(Reporte.id_reporte == reporte_id).first()

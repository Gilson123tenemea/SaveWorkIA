from sqlalchemy.orm import Session
from app.modelos.inspector_reporte import Inspectorreporte as InspectorReporte
from app.esquemas.inspector_reporte_esquema import InspectorReporteCreate

def crear_inspector_reporte(db: Session, inspector_reporte: InspectorReporteCreate):
    nuevo_registro = InspectorReporte(**inspector_reporte.dict())
    db.add(nuevo_registro)
    db.commit()
    db.refresh(nuevo_registro)
    return nuevo_registro

def obtener_inspector_reportes(db: Session):
    return db.query(InspectorReporte).all()

def obtener_inspector_reporte_por_id(db: Session, registro_id: int):
    return db.query(InspectorReporte).filter(
        InspectorReporte.id_inspector_reporte == registro_id
    ).first()

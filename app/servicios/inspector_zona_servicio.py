from sqlalchemy.orm import Session
from datetime import date

from app.modelos.inspector_zona import InspectorZona
from app.esquemas.inspector_zona_esquema import InspectorZonaCreate, InspectorZonaBase


def crear_inspector_zona(db: Session, data: InspectorZonaBase):
    nueva_asignacion = InspectorZona(
        fecha_asignacion=date.today(),   # Fecha automática
        borrado=data.borrado,
        id_inspector_inspectorzona=data.id_inspector_inspectorzona,
        id_zona_inspectorzona=data.id_zona_inspectorzona,
    )

    db.add(nueva_asignacion)
    db.commit()
    db.refresh(nueva_asignacion)
    return nueva_asignacion


def obtener_inspector_zonas(db: Session):
    return db.query(InspectorZona).filter(InspectorZona.borrado == True).all()


def obtener_inspector_zona_por_id(db: Session, asignacion_id: int):
    return (
        db.query(InspectorZona)
        .filter(
            InspectorZona.id_inspector_zona == asignacion_id,
            InspectorZona.borrado == True
        )
        .first()
    )


def actualizar_inspector_zona(db: Session, asignacion_id: int, data: InspectorZonaCreate):
    asignacion = db.query(InspectorZona).filter(
        InspectorZona.id_inspector_zona == asignacion_id
    ).first()

    if not asignacion:
        return None

    for key, value in data.dict().items():
        setattr(asignacion, key, value)

    db.commit()
    db.refresh(asignacion)
    return asignacion


def eliminar_inspector_zona(db: Session, asignacion_id: int):
    asignacion = db.query(InspectorZona).filter(
        InspectorZona.id_inspector_zona == asignacion_id
    ).first()

    if not asignacion:
        return None

    asignacion.borrado = False  # Borrado lógico
    db.commit()
    db.refresh(asignacion)
    return asignacion

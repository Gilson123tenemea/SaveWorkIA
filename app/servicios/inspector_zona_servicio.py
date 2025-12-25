from sqlalchemy.orm import Session
from app.modelos.inspector_zona import InspectorZona
from app.modelos.supervisor import Supervisor
from app.modelos.zona_modelo import Zona
from app.modelos.inspector import Inspector
from app.modelos.persona import Persona
from fastapi import HTTPException
from app.modelos.inspector_zona import InspectorZona
from app.esquemas.inspector_zona_esquema import InspectorZonaCreate, InspectorZonaBase


def crear_inspector_zona(db: Session, data: InspectorZonaBase):


    zona_ocupada = db.query(InspectorZona).filter(
        InspectorZona.id_zona_inspectorzona == data.id_zona_inspectorzona,
        InspectorZona.borrado == True
    ).first()

    if zona_ocupada:
        raise HTTPException(
            status_code=400,
            detail="La zona ya tiene un inspector asignado"
        )

    # ❌ VALIDAR: inspector ya asignado a esa zona
    asignacion_existente = db.query(InspectorZona).filter(
        InspectorZona.id_inspector_inspectorzona == data.id_inspector_inspectorzona,
        InspectorZona.id_zona_inspectorzona == data.id_zona_inspectorzona,
        InspectorZona.borrado == True
    ).first()

    if asignacion_existente:
        raise HTTPException(
            status_code=400,
            detail="El inspector ya está asignado a esta zona"
        )

    nueva_asignacion = InspectorZona(
        borrado=True,
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

def obtener_asignaciones_completas(db: Session, empresa_id: int):
    registros = (
        db.query(InspectorZona, Inspector, Persona, Zona)
        .join(Inspector, InspectorZona.id_inspector_inspectorzona == Inspector.id_inspector)
        .join(Persona, Inspector.id_persona_inspector == Persona.id_persona)
        .join(Zona, InspectorZona.id_zona_inspectorzona == Zona.id_Zona)
        .filter(
            Zona.id_empresa_zona == empresa_id,
            InspectorZona.borrado == True
        )
        .all()
    )

    resultado = []

    for asignacion, inspector, persona, zona in registros:
        resultado.append({
            "id_inspector_zona": asignacion.id_inspector_zona,
            "fecha_asignacion": asignacion.fecha_asignacion.strftime("%Y-%m-%d %H:%M"),

            "inspector": {
                "id_inspector": inspector.id_inspector,
                "cedula": persona.cedula,
                "nombre": persona.nombre,
                "apellido": persona.apellido
            },

            "zona": {
                "id_zona": zona.id_Zona,
                "nombreZona": zona.nombreZona
            }
        })

    return resultado

def obtener_zonas_disponibles_por_inspector(
    db: Session,
    inspector_id: int,
    empresa_id: int
):
    # zonas de la empresa
    zonas_empresa = db.query(Zona).filter(
        Zona.id_empresa_zona == empresa_id,
        Zona.borrado == True
    ).subquery()

    # zonas ya asignadas (a cualquier inspector)
    zonas_ocupadas = db.query(
        InspectorZona.id_zona_inspectorzona
    ).filter(
        InspectorZona.borrado == True
    ).subquery()

    zonas_disponibles = db.query(Zona).filter(
        Zona.id_Zona.notin_(zonas_ocupadas),
        Zona.id_empresa_zona == empresa_id,
        Zona.borrado == True
    ).all()

    return zonas_disponibles

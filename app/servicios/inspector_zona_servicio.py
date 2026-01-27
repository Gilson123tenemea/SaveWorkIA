from sqlalchemy.orm import Session
from app.modelos.inspector_zona import InspectorZona
from app.modelos.supervisor import Supervisor
from app.modelos.zona_modelo import Zona
from app.modelos.inspector import Inspector
from app.modelos.persona import Persona
from fastapi import HTTPException
from app.esquemas.inspector_zona_esquema import InspectorZonaCreate, InspectorZonaBase

# Importar servicio de logs
from app.servicios.log_service import LogServicio


async def crear_inspector_zona(
    db: Session, 
    data: InspectorZonaBase,
    ip_address: str = None
):
    """Crea una asignación de inspector a zona"""
    try:
        # Validar si la zona ya tiene inspector
        zona_ocupada = db.query(InspectorZona).filter(
            InspectorZona.id_zona_inspectorzona == data.id_zona_inspectorzona,
            InspectorZona.borrado == True
        ).first()

        if zona_ocupada:
            # Log de intento de asignar zona ocupada
            await LogServicio.registrar_accion_negocio(
                source="inspector_zona_servicio.crear_inspector_zona",
                accion="asignar_inspector_zona_fallido",
                user_id=data.id_inspector_inspectorzona,
                user_role="inspector",
                estado="failed",
                mensaje=f"Intento de asignar inspector a zona {data.id_zona_inspectorzona} ya ocupada",
                ip_address=ip_address,
                metadata={
                    "id_inspector": data.id_inspector_inspectorzona,
                    "id_zona": data.id_zona_inspectorzona,
                    "razon": "zona_ya_ocupada",
                    "inspector_actual": zona_ocupada.id_inspector_inspectorzona
                }
            )
            raise HTTPException(
                status_code=400,
                detail="La zona ya tiene un inspector asignado"
            )

        # Validar si inspector ya está asignado a esa zona
        asignacion_existente = db.query(InspectorZona).filter(
            InspectorZona.id_inspector_inspectorzona == data.id_inspector_inspectorzona,
            InspectorZona.id_zona_inspectorzona == data.id_zona_inspectorzona,
            InspectorZona.borrado == True
        ).first()

        if asignacion_existente:
            # Log de asignación duplicada
            await LogServicio.registrar_accion_negocio(
                source="inspector_zona_servicio.crear_inspector_zona",
                accion="asignar_inspector_zona_fallido",
                user_id=data.id_inspector_inspectorzona,
                user_role="inspector",
                estado="failed",
                mensaje=f"Inspector {data.id_inspector_inspectorzona} ya asignado a zona {data.id_zona_inspectorzona}",
                ip_address=ip_address,
                metadata={
                    "id_inspector": data.id_inspector_inspectorzona,
                    "id_zona": data.id_zona_inspectorzona,
                    "razon": "asignacion_duplicada"
                }
            )
            raise HTTPException(
                status_code=400,
                detail="El inspector ya está asignado a esta zona"
            )

        # Obtener información adicional para el log
        inspector = db.query(Inspector).filter(
            Inspector.id_inspector == data.id_inspector_inspectorzona
        ).first()
        
        zona = db.query(Zona).filter(
            Zona.id_Zona == data.id_zona_inspectorzona
        ).first()
        
        inspector_nombre = None
        if inspector and inspector.persona:
            inspector_nombre = f"{inspector.persona.nombre} {inspector.persona.apellido}"

        # Crear asignación
        nueva_asignacion = InspectorZona(
            borrado=True,
            id_inspector_inspectorzona=data.id_inspector_inspectorzona,
            id_zona_inspectorzona=data.id_zona_inspectorzona,
        )

        db.add(nueva_asignacion)
        db.commit()
        db.refresh(nueva_asignacion)
        
        # Log de asignación exitosa
        await LogServicio.registrar_accion_negocio(
            source="inspector_zona_servicio.crear_inspector_zona",
            accion="asignar_inspector_zona",
            user_id=data.id_inspector_inspectorzona,
            user_role="inspector",
            estado="success",
            mensaje=f"Inspector asignado a zona: {zona.nombreZona if zona else 'N/A'}",
            ip_address=ip_address,
            metadata={
                "id_asignacion": nueva_asignacion.id_inspector_zona,
                "id_inspector": data.id_inspector_inspectorzona,
                "id_zona": data.id_zona_inspectorzona,
                "nombre_zona": zona.nombreZona if zona else None,
                "inspector_nombre": inspector_nombre,
                "fecha_asignacion": nueva_asignacion.fecha_asignacion.isoformat()
            }
        )
        
        return nueva_asignacion
        
    except HTTPException:
        raise
    except Exception as e:
        # Log de error
        await LogServicio.registrar_error(
            source="inspector_zona_servicio.crear_inspector_zona",
            accion="asignar_inspector_zona",
            error_message=str(e),
            user_id=data.id_inspector_inspectorzona if data else None,
            ip_address=ip_address,
            metadata={
                "id_inspector": data.id_inspector_inspectorzona if data else None,
                "id_zona": data.id_zona_inspectorzona if data else None
            }
        )
        raise


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


async def actualizar_inspector_zona(
    db: Session, 
    asignacion_id: int, 
    data: InspectorZonaCreate,
    ip_address: str = None
):
    """Actualiza una asignación de inspector a zona"""
    try:
        asignacion = db.query(InspectorZona).filter(
            InspectorZona.id_inspector_zona == asignacion_id
        ).first()

        if not asignacion:
            # Log de asignación no encontrada
            await LogServicio.registrar_accion_negocio(
                source="inspector_zona_servicio.actualizar_inspector_zona",
                accion="actualizar_asignacion_inspector",
                estado="failed",
                mensaje=f"Intento de actualizar asignación inexistente: {asignacion_id}",
                ip_address=ip_address,
                metadata={"id_asignacion": asignacion_id}
            )
            return None

        # Guardar datos anteriores
        datos_anteriores = {
            "id_inspector": asignacion.id_inspector_inspectorzona,
            "id_zona": asignacion.id_zona_inspectorzona
        }

        # Obtener información adicional
        inspector_anterior = db.query(Inspector).filter(
            Inspector.id_inspector == asignacion.id_inspector_inspectorzona
        ).first()
        
        zona_anterior = db.query(Zona).filter(
            Zona.id_Zona == asignacion.id_zona_inspectorzona
        ).first()

        # Actualizar
        for key, value in data.dict().items():
            setattr(asignacion, key, value)

        db.commit()
        db.refresh(asignacion)
        
        # Obtener nuevos datos
        inspector_nuevo = db.query(Inspector).filter(
            Inspector.id_inspector == asignacion.id_inspector_inspectorzona
        ).first()
        
        zona_nueva = db.query(Zona).filter(
            Zona.id_Zona == asignacion.id_zona_inspectorzona
        ).first()
        
        # Log de actualización exitosa
        await LogServicio.registrar_accion_negocio(
            source="inspector_zona_servicio.actualizar_inspector_zona",
            accion="actualizar_asignacion_inspector",
            user_id=asignacion.id_inspector_inspectorzona,
            user_role="inspector",
            estado="success",
            mensaje=f"Asignación inspector-zona actualizada: {asignacion_id}",
            ip_address=ip_address,
            metadata={
                "id_asignacion": asignacion_id,
                "datos_anteriores": {
                    "id_inspector": datos_anteriores["id_inspector"],
                    "id_zona": datos_anteriores["id_zona"],
                    "nombre_zona": zona_anterior.nombreZona if zona_anterior else None
                },
                "datos_nuevos": {
                    "id_inspector": asignacion.id_inspector_inspectorzona,
                    "id_zona": asignacion.id_zona_inspectorzona,
                    "nombre_zona": zona_nueva.nombreZona if zona_nueva else None
                }
            }
        )
        
        return asignacion
        
    except Exception as e:
        # Log de error
        await LogServicio.registrar_error(
            source="inspector_zona_servicio.actualizar_inspector_zona",
            accion="actualizar_asignacion_inspector",
            error_message=str(e),
            ip_address=ip_address,
            metadata={"id_asignacion": asignacion_id}
        )
        raise


async def eliminar_inspector_zona(
    db: Session, 
    asignacion_id: int,
    ip_address: str = None
):
    """Elimina lógicamente una asignación de inspector a zona"""
    try:
        asignacion = db.query(InspectorZona).filter(
            InspectorZona.id_inspector_zona == asignacion_id
        ).first()

        if not asignacion:
            # Log de asignación no encontrada
            await LogServicio.registrar_accion_negocio(
                source="inspector_zona_servicio.eliminar_inspector_zona",
                accion="eliminar_asignacion_inspector",
                estado="failed",
                mensaje=f"Intento de eliminar asignación inexistente: {asignacion_id}",
                ip_address=ip_address,
                metadata={"id_asignacion": asignacion_id}
            )
            return None

        # Obtener información antes de eliminar
        id_inspector = asignacion.id_inspector_inspectorzona
        id_zona = asignacion.id_zona_inspectorzona
        
        inspector = db.query(Inspector).filter(
            Inspector.id_inspector == id_inspector
        ).first()
        
        zona = db.query(Zona).filter(
            Zona.id_Zona == id_zona
        ).first()
        
        inspector_nombre = None
        if inspector and inspector.persona:
            inspector_nombre = f"{inspector.persona.nombre} {inspector.persona.apellido}"

        # Borrado lógico
        asignacion.borrado = False
        db.commit()
        db.refresh(asignacion)
        
        # Log de eliminación exitosa
        await LogServicio.registrar_accion_negocio(
            source="inspector_zona_servicio.eliminar_inspector_zona",
            accion="eliminar_asignacion_inspector",
            user_id=id_inspector,
            user_role="inspector",
            estado="success",
            mensaje=f"Asignación inspector-zona eliminada: {zona.nombreZona if zona else 'N/A'}",
            ip_address=ip_address,
            metadata={
                "id_asignacion": asignacion_id,
                "id_inspector": id_inspector,
                "id_zona": id_zona,
                "nombre_zona": zona.nombreZona if zona else None,
                "inspector_nombre": inspector_nombre,
                "tipo_eliminacion": "logica"
            }
        )
        
        return asignacion
        
    except Exception as e:
        # Log de error
        await LogServicio.registrar_error(
            source="inspector_zona_servicio.eliminar_inspector_zona",
            accion="eliminar_asignacion_inspector",
            error_message=str(e),
            ip_address=ip_address,
            metadata={"id_asignacion": asignacion_id}
        )
        raise


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
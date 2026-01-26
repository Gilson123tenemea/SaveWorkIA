from sqlalchemy.orm import Session
from app.modelos.evidencias_fallo import EvidenciaFallo
from app.modelos.registros_asistencia import RegistroAsistencia
from app.esquemas.evidencias_fallo_esquema import EvidenciaFalloCreate
from datetime import datetime
import base64
from app.servicios.notificaciones_fcm_servicio import NotificacionesFCMServicio

# Importar servicio de logs
from app.servicios.log_service import LogServicio


async def guardar_evidencia_fallo(
    db: Session, 
    evidencia: EvidenciaFalloCreate,
    ip_address: str = None
):
    """
    Guarda evidencia de fallo EPP y envía notificación al inspector
    """
    
    try:
        print('\n📸 === GUARDANDO EVIDENCIA DE FALLO === 📸')
        
        # 1️⃣ Decodificar foto
        foto_bytes = base64.b64decode(evidencia.foto_base64)

        # 2️⃣ Crear registro de evidencia
        nuevo = EvidenciaFallo(
            foto_data=foto_bytes,
            detalle_fallo=evidencia.detalle_fallo,
            id_registro=evidencia.id_registro,
            fecha_captura=datetime.now(),
            borrado=True  # ✅ activo
        )

        db.add(nuevo)
        db.commit()
        db.refresh(nuevo)
        
        print(f'✅ Evidencia guardada: ID {nuevo.id_evidencia}')
        
        # 3️⃣ OBTENER INSPECTOR ASOCIADO Y ENVIAR NOTIFICACIÓN
        notificacion_enviada = False
        id_inspector = None
        nombre_trabajador = "N/A"
        nombre_zona = "N/A"
        
        try:
            # Obtener el registro de asistencia para acceder a los datos
            registro = db.query(RegistroAsistencia).filter(
                RegistroAsistencia.id_registro == evidencia.id_registro
            ).first()
            
            if not registro:
                print('⚠️ No se encontró registro de asistencia')
            else:
                # El inspector está en el registro
                id_inspector = registro.id_inspector
                
                # Obtener datos para los logs
                if registro.trabajador and registro.trabajador.persona:
                    nombre_trabajador = f"{registro.trabajador.persona.nombre} {registro.trabajador.persona.apellido}"
                
                if registro.zona:
                    nombre_zona = registro.zona.nombreZona
                
                if not id_inspector:
                    print('⚠️ El registro no tiene inspector asignado')
                else:
                    print(f'🔔 Enviando notificación al inspector {id_inspector}...')
                    
                    # 4️⃣ ENVIAR NOTIFICACIÓN
                    exito = NotificacionesFCMServicio.enviar_notificacion_inspector(
                        db,
                        id_inspector,
                        titulo="⚠️ Falta de Equipamiento",
                        cuerpo=f"👤 {nombre_trabajador}\n📍 {nombre_zona}\n❌ {evidencia.detalle_fallo}",
                        datos={
                            "tipo": "falta_equipo",
                            "id_evidencia": str(nuevo.id_evidencia),
                            "id_registro": str(evidencia.id_registro),
                            "id_zona": str(registro.id_zona),
                            "detalle": evidencia.detalle_fallo
                        }
                    )
                    
                    if exito:
                        print(f'✅ Notificación enviada exitosamente')
                        notificacion_enviada = True
                    else:
                        print(f'⚠️ No se pudo enviar notificación (inspector sin tokens)')
                
        except Exception as e:
            print(f'❌ Error enviando notificación: {e}')
            # No detener el proceso si falla la notificación
        
        # Log de evidencia guardada
        await LogServicio.registrar_accion_negocio(
            source="evidencias_fallo_servicio.guardar_evidencia_fallo",
            accion="guardar_evidencia_fallo",
            user_id=registro.id_trabajador if registro else None,
            user_role="trabajador",
            estado="success",
            mensaje=f"Evidencia de fallo EPP guardada: {evidencia.detalle_fallo}",
            ip_address=ip_address,
            metadata={
                "id_evidencia": nuevo.id_evidencia,
                "id_registro": evidencia.id_registro,
                "detalle_fallo": evidencia.detalle_fallo,
                "id_inspector": id_inspector,
                "notificacion_enviada": notificacion_enviada,
                "trabajador": nombre_trabajador,
                "zona": nombre_zona,
                "fecha_captura": nuevo.fecha_captura.isoformat(),
                "tamaño_foto_bytes": len(foto_bytes)
            }
        )
        
        return nuevo
        
    except Exception as e:
        # Log de error
        await LogServicio.registrar_error(
            source="evidencias_fallo_servicio.guardar_evidencia_fallo",
            accion="guardar_evidencia_fallo",
            error_message=str(e),
            ip_address=ip_address,
            metadata={
                "id_registro": evidencia.id_registro if evidencia else None,
                "detalle_fallo": evidencia.detalle_fallo if evidencia else None
            }
        )
        raise


async def actualizar_evidencia_fallo(
    db: Session, 
    id_evidencia: int, 
    cambios,
    ip_address: str = None
):
    """
    Actualiza una evidencia de fallo (sin enviar notificación)
    """
    
    try:
        print(f'\n📝 === ACTUALIZANDO EVIDENCIA {id_evidencia} === 📝')
        
        evidencia = db.query(EvidenciaFallo).filter(
            EvidenciaFallo.id_evidencia == id_evidencia
        ).first()

        if not evidencia:
            print(f'❌ Evidencia {id_evidencia} no encontrada')
            
            await LogServicio.registrar_accion_negocio(
                source="evidencias_fallo_servicio.actualizar_evidencia_fallo",
                accion="actualizar_evidencia_fallo",
                estado="failed",
                mensaje=f"Intento de actualizar evidencia inexistente: {id_evidencia}",
                ip_address=ip_address,
                metadata={"id_evidencia": id_evidencia}
            )
            
            return None

        # Guardar datos anteriores
        datos_anteriores = {
            "estado": evidencia.estado,
            "observaciones": evidencia.observaciones
        }

        # Actualizar estado
        if cambios.estado is not None:
            evidencia.estado = cambios.estado
            print(f'   Estado: {cambios.estado}')

        # Actualizar observaciones
        if cambios.observaciones is not None:
            evidencia.observaciones = cambios.observaciones
            print(f'   Observaciones: {cambios.observaciones}')

        db.commit()
        db.refresh(evidencia)
        
        print(f'✅ Evidencia actualizada')
        
        # Log de actualización exitosa
        await LogServicio.registrar_accion_negocio(
            source="evidencias_fallo_servicio.actualizar_evidencia_fallo",
            accion="actualizar_evidencia_fallo",
            estado="success",
            mensaje=f"Evidencia {id_evidencia} actualizada",
            ip_address=ip_address,
            metadata={
                "id_evidencia": id_evidencia,
                "datos_anteriores": datos_anteriores,
                "datos_nuevos": {
                    "estado": evidencia.estado,
                    "observaciones": evidencia.observaciones
                }
            }
        )

        return {
            "mensaje": "Evidencia actualizada correctamente",
            "id_evidencia": evidencia.id_evidencia,
            "estado": evidencia.estado,
            "observaciones": evidencia.observaciones
        }
        
    except Exception as e:
        # Log de error
        await LogServicio.registrar_error(
            source="evidencias_fallo_servicio.actualizar_evidencia_fallo",
            accion="actualizar_evidencia_fallo",
            error_message=str(e),
            ip_address=ip_address,
            metadata={"id_evidencia": id_evidencia}
        )
        raise


def obtener_epp_activos_por_zona(db: Session, id_zona: int) -> list[str]:
    """
    Devuelve lista de EPP activos y obligatorios configurados para una zona
    Ej: ["casco", "botas", "chaleco"]
    """
    from app.modelos.zona_epp import ZonaEpp
    
    epps = (
        db.query(ZonaEpp)
        .filter(
            ZonaEpp.id_zona == id_zona,
            ZonaEpp.activo == True,
            ZonaEpp.obligatorio == True
        )
        .all()
    )

    return [e.tipo_epp.lower() for e in epps]
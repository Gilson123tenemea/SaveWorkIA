from sqlalchemy.orm import Session
from app.modelos.evidencias_fallo import EvidenciaFallo
from app.modelos.registros_asistencia import RegistroAsistencia
from app.esquemas.evidencias_fallo_esquema import EvidenciaFalloCreate
from datetime import datetime
import base64
from app.servicios.notificaciones_fcm_servicio import NotificacionesFCMServicio

def guardar_evidencia_fallo(db: Session, evidencia: EvidenciaFalloCreate):
    """
    Guarda evidencia de fallo EPP y envía notificación al inspector
    """
    
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
    try:
        # Obtener el registro de asistencia para acceder a los datos
        registro = db.query(RegistroAsistencia).filter(
            RegistroAsistencia.id_registro == evidencia.id_registro
        ).first()
        
        if not registro:
            print('⚠️ No se encontró registro de asistencia')
            return nuevo
        
        # El inspector está en el registro
        id_inspector = registro.id_inspector
        
        if not id_inspector:
            print('⚠️ El registro no tiene inspector asignado')
            return nuevo
        
        print(f'🔔 Enviando notificación al inspector {id_inspector}...')
        
        # 4️⃣ ENVIAR NOTIFICACIÓN
        exito = NotificacionesFCMServicio.enviar_notificacion_inspector(
            db,
            id_inspector,
            titulo="⚠️ Falta de Equipamiento",
            cuerpo=f"👤 {registro.trabajador.persona.nombre}\n📍 {registro.zona.nombreZona}\n❌ {evidencia.detalle_fallo}",
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
        else:
            print(f'⚠️ No se pudo enviar notificación (inspector sin tokens)')
            
    except Exception as e:
        print(f'❌ Error enviando notificación: {e}')
        # No detener el proceso si falla la notificación
    
    return nuevo


def actualizar_evidencia_fallo(db: Session, id_evidencia: int, cambios):
    """
    Actualiza una evidencia de fallo (sin enviar notificación)
    """
    
    print(f'\n📝 === ACTUALIZANDO EVIDENCIA {id_evidencia} === 📝')
    
    evidencia = db.query(EvidenciaFallo).filter(
        EvidenciaFallo.id_evidencia == id_evidencia
    ).first()

    if not evidencia:
        print(f'❌ Evidencia {id_evidencia} no encontrada')
        return None

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

    return {
        "mensaje": "Evidencia actualizada correctamente",
        "id_evidencia": evidencia.id_evidencia,
        "estado": evidencia.estado,
        "observaciones": evidencia.observaciones
    }


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
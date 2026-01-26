from sqlalchemy.orm import Session
from app.modelos.registros_asistencia import RegistroAsistencia
from app.esquemas.registros_asistencia_esquema import RegistroAsistenciaCreate
from datetime import datetime
from app.modelos.zona_epp import ZonaEpp

from app.servicios.log_service import LogServicio


def obtener_epp_activos_por_zona(db: Session, id_zona: int) -> list[str]:
    """
    Devuelve lista de EPP activos y obligatorios configurados para una zona
    Ej: ["casco", "botas", "chaleco"]
    """
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


async def crear_registro_asistencia(
    db: Session, 
    asistencia: RegistroAsistenciaCreate,
    ip_address: str = None
):
    """
    Crea un registro de asistencia
    
    IMPORTANTE: La notificación se envía SOLO cuando se crea una evidencia de fallo,
    no aquí. Ver: guardar_evidencia_fallo()
    """
    
    try:
        print(f'\n📋 === CREANDO REGISTRO ASISTENCIA === 📋')
        
        nuevo = RegistroAsistencia(
            cumple_epp=asistencia.cumple_epp,
            codigo_ingresado=asistencia.codigo_ingresado,
            id_trabajador=asistencia.id_trabajador,
            id_empresa=asistencia.id_empresa,
            id_zona=asistencia.id_zona,
            id_supervisor=asistencia.id_supervisor,
            id_camara=asistencia.id_camara,
            id_inspector=asistencia.id_inspector,
        )

        if asistencia.fecha_hora:
            nuevo.fecha_hora = asistencia.fecha_hora
        else:
            nuevo.fecha_hora = datetime.now()

        db.add(nuevo)
        db.commit()
        db.refresh(nuevo)
        
        print(f'✅ Registro creado: ID {nuevo.id_registro}')
        
        await LogServicio.registrar_accion_negocio(
            source="registros_asistencia_servicio.crear_registro_asistencia",
            accion="registro_asistencia",
            user_id=asistencia.id_trabajador,
            user_role="trabajador",
            estado="success" if asistencia.cumple_epp else "warning",
            mensaje=f"Registro de asistencia - {'✅ Cumple EPP' if asistencia.cumple_epp else '❌ NO cumple EPP'}",
            ip_address=ip_address,
            metadata={
                "id_registro": nuevo.id_registro,
                "codigo_trabajador": asistencia.codigo_ingresado,
                "id_trabajador": asistencia.id_trabajador,
                "id_empresa": asistencia.id_empresa,
                "id_zona": asistencia.id_zona,
                "id_camara": asistencia.id_camara,
                "id_inspector": asistencia.id_inspector,
                "cumple_epp": asistencia.cumple_epp,
                "fecha_hora": nuevo.fecha_hora.isoformat()
            }
        )
        
        return nuevo
        
    except Exception as e:
        await LogServicio.registrar_error(
            source="registros_asistencia_servicio.crear_registro_asistencia",
            accion="registro_asistencia",
            error_message=str(e),
            user_id=asistencia.id_trabajador if asistencia else None,
            ip_address=ip_address,
            metadata={
                "codigo_trabajador": asistencia.codigo_ingresado if asistencia else None,
                "id_zona": asistencia.id_zona if asistencia else None
            }
        )
        raise
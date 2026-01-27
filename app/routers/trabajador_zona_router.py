from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from app.config import SessionLocal

from app.servicios.trabajador_zona_servicio import (
    crear_trabajador_zona,
    obtener_trabajador_zonas,
    obtener_trabajador_zona_por_id,
    eliminar_fisico_trabajador_zona,
    eliminar_logico_trabajador_zona,
    obtener_zonas_con_detalles_por_supervisor
)

from app.esquemas.trabajador_zona_esquema import (
    TrabajadorZonaCreate,
    TrabajadorZonaResponse
)
from app.esquemas.trabajador_zona_esquema import ZonaDetallesResponse
from app.esquemas.trabajador_zona_esquema import TrabajadorZonaDetalle
from app.servicios.trabajador_zona_servicio import obtener_trabajador_zonas_detalles

# Importar servicio de logs
from app.servicios.log_service import LogServicio

router = APIRouter(prefix="/trabajador_zonas", tags=["Trabajador - Zonas"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def obtener_ip_cliente(request: Request) -> str:
    """Extrae la IP del cliente desde el request"""
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0].strip()
    
    real_ip = request.headers.get("X-Real-IP")
    if real_ip:
        return real_ip
    
    return request.client.host if request.client else "unknown"


@router.get("/supervisor/{id_supervisor}", response_model=list[ZonaDetallesResponse])
async def listar_zonas_por_supervisor(
    id_supervisor: int, 
    request: Request,
    db: Session = Depends(get_db)
):
    """Lista todas las zonas con detalles para un supervisor específico"""
    try:
        ip_address = obtener_ip_cliente(request)
        zonas = obtener_zonas_con_detalles_por_supervisor(db, id_supervisor)
        
        # Log de consulta exitosa
        await LogServicio.registrar_accion_negocio(
            source="trabajador_zona_router.listar_zonas_por_supervisor",
            accion="consultar_zonas_supervisor",
            user_id=id_supervisor,
            user_role="supervisor",
            estado="success",
            mensaje=f"Consulta de zonas por supervisor: {len(zonas)} zonas encontradas",
            ip_address=ip_address,
            metadata={
                "id_supervisor": id_supervisor,
                "total_zonas": len(zonas),
                "zonas_ids": [z["zona"]["id"] for z in zonas] if zonas else []
            }
        )
        
        return zonas
        
    except Exception as e:
        # Log de error
        await LogServicio.registrar_error(
            source="trabajador_zona_router.listar_zonas_por_supervisor",
            accion="consultar_zonas_supervisor",
            error_message=str(e),
            user_id=id_supervisor,
            ip_address=obtener_ip_cliente(request),
            metadata={"id_supervisor": id_supervisor}
        )
        raise


# =====================================================
# 🔥 IMPORTANTE: RUTA DETALLES DEBE IR ANTES DE /{id}
# =====================================================
@router.get("/detalles", response_model=list[TrabajadorZonaDetalle])
async def listar_detalles(
    request: Request,
    db: Session = Depends(get_db)
):
    """Lista todos los detalles de asignaciones trabajador-zona"""
    try:
        ip_address = obtener_ip_cliente(request)
        detalles = obtener_trabajador_zonas_detalles(db)
        
        # Log de consulta exitosa
        await LogServicio.registrar_accion_negocio(
            source="trabajador_zona_router.listar_detalles",
            accion="consultar_asignaciones_detalle",
            estado="success",
            mensaje=f"Consulta de detalles de asignaciones: {len(detalles)} registros",
            ip_address=ip_address,
            metadata={
                "total_asignaciones": len(detalles)
            }
        )
        
        return detalles
        
    except Exception as e:
        # Log de error
        await LogServicio.registrar_error(
            source="trabajador_zona_router.listar_detalles",
            accion="consultar_asignaciones_detalle",
            error_message=str(e),
            ip_address=obtener_ip_cliente(request)
        )
        raise


# ===========================
# 📌 CRUD
# ===========================

@router.post("/", response_model=TrabajadorZonaResponse)
async def crear(
    asignacion: TrabajadorZonaCreate, 
    request: Request,
    db: Session = Depends(get_db)
):
    """Crea una nueva asignación de trabajador a zona"""
    try:
        ip_address = obtener_ip_cliente(request)
        
        # Log de inicio de asignación
        await LogServicio.registrar_accion_negocio(
            source="trabajador_zona_router.crear",
            accion="crear_asignacion_inicio",
            user_id=asignacion.id_trabajador_trabajadorzona,
            estado="pending",
            mensaje=f"Iniciando asignación de trabajador {asignacion.id_trabajador_trabajadorzona} a zona {asignacion.id_zona_trabajadorzona}",
            ip_address=ip_address,
            metadata={
                "id_trabajador": asignacion.id_trabajador_trabajadorzona,
                "id_zona": asignacion.id_zona_trabajadorzona
            }
        )
        
        return await crear_trabajador_zona(db, asignacion, ip_address)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/", response_model=list[TrabajadorZonaResponse])
def listar(db: Session = Depends(get_db)):
    """Lista todas las asignaciones trabajador-zona"""
    return obtener_trabajador_zonas(db)


@router.get("/{asignacion_id}", response_model=TrabajadorZonaResponse)
async def obtener(
    asignacion_id: int, 
    request: Request,
    db: Session = Depends(get_db)
):
    """Obtiene una asignación específica por ID"""
    try:
        ip_address = obtener_ip_cliente(request)
        asignacion = obtener_trabajador_zona_por_id(db, asignacion_id)
        
        if not asignacion:
            await LogServicio.registrar_accion_negocio(
                source="trabajador_zona_router.obtener",
                accion="consultar_asignacion",
                estado="failed",
                mensaje=f"Asignación no encontrada: {asignacion_id}",
                ip_address=ip_address,
                metadata={"id_asignacion": asignacion_id}
            )
            raise HTTPException(status_code=404, detail="Asignación no encontrada")
        
        # Log de consulta exitosa
        await LogServicio.registrar_accion_negocio(
            source="trabajador_zona_router.obtener",
            accion="consultar_asignacion",
            user_id=asignacion.id_trabajador_trabajadorzona,
            estado="success",
            mensaje=f"Consulta de asignación {asignacion_id}",
            ip_address=ip_address,
            metadata={
                "id_asignacion": asignacion_id,
                "id_trabajador": asignacion.id_trabajador_trabajadorzona,
                "id_zona": asignacion.id_zona_trabajadorzona
            }
        )
        
        return asignacion
        
    except HTTPException:
        raise
    except Exception as e:
        await LogServicio.registrar_error(
            source="trabajador_zona_router.obtener",
            accion="consultar_asignacion",
            error_message=str(e),
            ip_address=obtener_ip_cliente(request),
            metadata={"id_asignacion": asignacion_id}
        )
        raise


@router.delete("/{asignacion_id}")
async def eliminar_fisico(
    asignacion_id: int, 
    request: Request,
    db: Session = Depends(get_db)
):
    """Elimina físicamente una asignación trabajador-zona"""
    try:
        ip_address = obtener_ip_cliente(request)
        
        # Log de inicio de eliminación física
        await LogServicio.registrar_accion_negocio(
            source="trabajador_zona_router.eliminar_fisico",
            accion="eliminar_asignacion_fisica_inicio",
            estado="pending",
            mensaje=f"Iniciando eliminación física de asignación {asignacion_id}",
            ip_address=ip_address,
            metadata={"id_asignacion": asignacion_id}
        )
        
        ok = await eliminar_fisico_trabajador_zona(db, asignacion_id, ip_address)
        
        if not ok:
            raise HTTPException(status_code=404, detail="Asignación no encontrada")
        
        return {"mensaje": "Asignación eliminada físicamente"}
        
    except HTTPException:
        raise
    except Exception as e:
        await LogServicio.registrar_error(
            source="trabajador_zona_router.eliminar_fisico",
            accion="eliminar_asignacion_fisica",
            error_message=str(e),
            ip_address=obtener_ip_cliente(request),
            metadata={"id_asignacion": asignacion_id}
        )
        raise


@router.put("/eliminar-logico/{asignacion_id}", response_model=TrabajadorZonaResponse)
async def eliminar_logico(
    asignacion_id: int, 
    request: Request,
    db: Session = Depends(get_db)
):
    """Elimina lógicamente una asignación trabajador-zona (marca como borrado)"""
    try:
        ip_address = obtener_ip_cliente(request)
        
        # Log de inicio de eliminación lógica
        await LogServicio.registrar_accion_negocio(
            source="trabajador_zona_router.eliminar_logico",
            accion="eliminar_asignacion_logica_inicio",
            estado="pending",
            mensaje=f"Iniciando eliminación lógica de asignación {asignacion_id}",
            ip_address=ip_address,
            metadata={"id_asignacion": asignacion_id}
        )
        
        asignacion = await eliminar_logico_trabajador_zona(db, asignacion_id, ip_address)
        
        if not asignacion:
            raise HTTPException(status_code=404, detail="Asignación no encontrada")
        
        return asignacion
        
    except HTTPException:
        raise
    except Exception as e:
        await LogServicio.registrar_error(
            source="trabajador_zona_router.eliminar_logico",
            accion="eliminar_asignacion_logica",
            error_message=str(e),
            ip_address=obtener_ip_cliente(request),
            metadata={"id_asignacion": asignacion_id}
        )
        raise
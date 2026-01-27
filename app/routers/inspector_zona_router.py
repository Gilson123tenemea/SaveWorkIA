from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session

from app.config import SessionLocal
from app.esquemas.inspector_zona_esquema import (
    InspectorZonaCreate,
    InspectorZonaResponse,
    InspectorZonaFullResponse
)
from app.servicios import inspector_zona_servicio

# Importar servicio de logs
from app.servicios.log_service import LogServicio

router = APIRouter(prefix="/inspector_zonas", tags=["Inspector - Zonas"])


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


@router.post("/", response_model=InspectorZonaResponse)
async def crear(
    asignacion: InspectorZonaCreate, 
    request: Request,
    db: Session = Depends(get_db)
):
    """Crea una nueva asignación de inspector a zona"""
    try:
        ip_address = obtener_ip_cliente(request)
        
        # Log de inicio de asignación
        await LogServicio.registrar_accion_negocio(
            source="inspector_zona_router.crear",
            accion="crear_asignacion_inspector_inicio",
            user_id=asignacion.id_inspector_inspectorzona,
            user_role="inspector",
            estado="pending",
            mensaje=f"Iniciando asignación de inspector {asignacion.id_inspector_inspectorzona} a zona {asignacion.id_zona_inspectorzona}",
            ip_address=ip_address,
            metadata={
                "id_inspector": asignacion.id_inspector_inspectorzona,
                "id_zona": asignacion.id_zona_inspectorzona
            }
        )
        
        return await inspector_zona_servicio.crear_inspector_zona(db, asignacion, ip_address)
        
    except HTTPException:
        raise
    except Exception as e:
        await LogServicio.registrar_error(
            source="inspector_zona_router.crear",
            accion="crear_asignacion_inspector",
            error_message=str(e),
            ip_address=obtener_ip_cliente(request),
            metadata={
                "id_inspector": asignacion.id_inspector_inspectorzona if asignacion else None,
                "id_zona": asignacion.id_zona_inspectorzona if asignacion else None
            }
        )
        raise


@router.get("/zonas-disponibles/{empresa_id}/{inspector_id}")
async def zonas_disponibles(
    empresa_id: int,
    inspector_id: int,
    request: Request,
    db: Session = Depends(get_db)
):
    """Obtiene las zonas disponibles para asignar a un inspector"""
    try:
        ip_address = obtener_ip_cliente(request)
        
        zonas = inspector_zona_servicio.obtener_zonas_disponibles_por_inspector(
            db, inspector_id, empresa_id
        )
        
        # Log de consulta exitosa
        await LogServicio.registrar_accion_negocio(
            source="inspector_zona_router.zonas_disponibles",
            accion="consultar_zonas_disponibles",
            user_id=inspector_id,
            user_role="inspector",
            estado="success",
            mensaje=f"Consulta de zonas disponibles para inspector {inspector_id}: {len(zonas)} zonas",
            ip_address=ip_address,
            metadata={
                "id_inspector": inspector_id,
                "id_empresa": empresa_id,
                "total_zonas_disponibles": len(zonas),
                "zonas_ids": [z.id_Zona for z in zonas] if zonas else []
            }
        )
        
        return zonas
        
    except Exception as e:
        await LogServicio.registrar_error(
            source="inspector_zona_router.zonas_disponibles",
            accion="consultar_zonas_disponibles",
            error_message=str(e),
            user_id=inspector_id,
            ip_address=obtener_ip_cliente(request),
            metadata={
                "id_inspector": inspector_id,
                "id_empresa": empresa_id
            }
        )
        raise


@router.get("/", response_model=list[InspectorZonaResponse])
async def listar(
    request: Request,
    db: Session = Depends(get_db)
):
    """Lista todas las asignaciones de inspector-zona activas"""
    try:
        ip_address = obtener_ip_cliente(request)
        asignaciones = inspector_zona_servicio.obtener_inspector_zonas(db)
        
        # Log de consulta exitosa
        await LogServicio.registrar_accion_negocio(
            source="inspector_zona_router.listar",
            accion="listar_asignaciones_inspector",
            estado="success",
            mensaje=f"Consulta de todas las asignaciones inspector-zona: {len(asignaciones)} registros",
            ip_address=ip_address,
            metadata={
                "total_asignaciones": len(asignaciones)
            }
        )
        
        return asignaciones
        
    except Exception as e:
        await LogServicio.registrar_error(
            source="inspector_zona_router.listar",
            accion="listar_asignaciones_inspector",
            error_message=str(e),
            ip_address=obtener_ip_cliente(request)
        )
        raise


@router.get("/{asignacion_id}", response_model=InspectorZonaResponse)
async def obtener(
    asignacion_id: int, 
    request: Request,
    db: Session = Depends(get_db)
):
    """Obtiene una asignación específica por ID"""
    try:
        ip_address = obtener_ip_cliente(request)
        asignacion = inspector_zona_servicio.obtener_inspector_zona_por_id(db, asignacion_id)
        
        if not asignacion:
            await LogServicio.registrar_accion_negocio(
                source="inspector_zona_router.obtener",
                accion="consultar_asignacion_inspector",
                estado="failed",
                mensaje=f"Asignación inspector-zona no encontrada: {asignacion_id}",
                ip_address=ip_address,
                metadata={"id_asignacion": asignacion_id}
            )
            raise HTTPException(status_code=404, detail="Asignación no encontrada")
        
        # Log de consulta exitosa
        await LogServicio.registrar_accion_negocio(
            source="inspector_zona_router.obtener",
            accion="consultar_asignacion_inspector",
            user_id=asignacion.id_inspector_inspectorzona,
            user_role="inspector",
            estado="success",
            mensaje=f"Consulta de asignación inspector-zona: {asignacion_id}",
            ip_address=ip_address,
            metadata={
                "id_asignacion": asignacion_id,
                "id_inspector": asignacion.id_inspector_inspectorzona,
                "id_zona": asignacion.id_zona_inspectorzona
            }
        )
        
        return asignacion
        
    except HTTPException:
        raise
    except Exception as e:
        await LogServicio.registrar_error(
            source="inspector_zona_router.obtener",
            accion="consultar_asignacion_inspector",
            error_message=str(e),
            ip_address=obtener_ip_cliente(request),
            metadata={"id_asignacion": asignacion_id}
        )
        raise


@router.put("/{asignacion_id}", response_model=InspectorZonaResponse)
async def actualizar(
    asignacion_id: int, 
    data: InspectorZonaCreate, 
    request: Request,
    db: Session = Depends(get_db)
):
    """Actualiza una asignación de inspector a zona"""
    try:
        ip_address = obtener_ip_cliente(request)
        
        # Log de inicio de actualización
        await LogServicio.registrar_accion_negocio(
            source="inspector_zona_router.actualizar",
            accion="actualizar_asignacion_inspector_inicio",
            estado="pending",
            mensaje=f"Iniciando actualización de asignación inspector-zona: {asignacion_id}",
            ip_address=ip_address,
            metadata={
                "id_asignacion": asignacion_id,
                "nuevos_datos": {
                    "id_inspector": data.id_inspector_inspectorzona,
                    "id_zona": data.id_zona_inspectorzona
                }
            }
        )
        
        asignacion = await inspector_zona_servicio.actualizar_inspector_zona(
            db, asignacion_id, data, ip_address
        )
        
        if not asignacion:
            raise HTTPException(status_code=404, detail="Asignación no encontrada")
        
        return asignacion
        
    except HTTPException:
        raise
    except Exception as e:
        await LogServicio.registrar_error(
            source="inspector_zona_router.actualizar",
            accion="actualizar_asignacion_inspector",
            error_message=str(e),
            ip_address=obtener_ip_cliente(request),
            metadata={"id_asignacion": asignacion_id}
        )
        raise


@router.delete("/{asignacion_id}", response_model=InspectorZonaResponse)
async def eliminar(
    asignacion_id: int, 
    request: Request,
    db: Session = Depends(get_db)
):
    """Elimina lógicamente una asignación de inspector a zona"""
    try:
        ip_address = obtener_ip_cliente(request)
        
        # Log de inicio de eliminación
        await LogServicio.registrar_accion_negocio(
            source="inspector_zona_router.eliminar",
            accion="eliminar_asignacion_inspector_inicio",
            estado="pending",
            mensaje=f"Iniciando eliminación de asignación inspector-zona: {asignacion_id}",
            ip_address=ip_address,
            metadata={"id_asignacion": asignacion_id}
        )
        
        asignacion = await inspector_zona_servicio.eliminar_inspector_zona(
            db, asignacion_id, ip_address
        )
        
        if not asignacion:
            raise HTTPException(status_code=404, detail="Asignación no encontrada")
        
        return asignacion
        
    except HTTPException:
        raise
    except Exception as e:
        await LogServicio.registrar_error(
            source="inspector_zona_router.eliminar",
            accion="eliminar_asignacion_inspector",
            error_message=str(e),
            ip_address=obtener_ip_cliente(request),
            metadata={"id_asignacion": asignacion_id}
        )
        raise


@router.get("/empresa/{empresa_id}")
async def listar_por_empresa(
    empresa_id: int, 
    request: Request,
    db: Session = Depends(get_db)
):
    """Lista todas las asignaciones de inspector-zona para una empresa específica"""
    try:
        ip_address = obtener_ip_cliente(request)
        asignaciones = inspector_zona_servicio.obtener_asignaciones_completas(db, empresa_id)
        
        # Log de consulta exitosa
        await LogServicio.registrar_accion_negocio(
            source="inspector_zona_router.listar_por_empresa",
            accion="consultar_asignaciones_empresa",
            estado="success",
            mensaje=f"Consulta de asignaciones inspector-zona por empresa {empresa_id}: {len(asignaciones)} registros",
            ip_address=ip_address,
            metadata={
                "id_empresa": empresa_id,
                "total_asignaciones": len(asignaciones),
                "inspectores_ids": list(set([a["inspector"]["id_inspector"] for a in asignaciones])) if asignaciones else [],
                "zonas_ids": [a["zona"]["id_zona"] for a in asignaciones] if asignaciones else []
            }
        )
        
        return asignaciones
        
    except Exception as e:
        await LogServicio.registrar_error(
            source="inspector_zona_router.listar_por_empresa",
            accion="consultar_asignaciones_empresa",
            error_message=str(e),
            ip_address=obtener_ip_cliente(request),
            metadata={"id_empresa": empresa_id}
        )
        raise
from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session
from app.config import get_db
from app.esquemas.token_reset_esquema import (
    SolicitudCambioContraseña,
    VerificarTokenReset
)
from app.servicios import token_reset_servicio

# Importar servicio de logs
from app.servicios.log_service import LogServicio

router = APIRouter(prefix="/auth", tags=["Autenticación"])


def obtener_ip_cliente(request: Request) -> str:
    """Extrae la IP del cliente desde el request"""
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0].strip()
    
    real_ip = request.headers.get("X-Real-IP")
    if real_ip:
        return real_ip
    
    return request.client.host if request.client else "unknown"


@router.post("/solicitar-cambio-contrasena")
async def solicitar_cambio_contrasena(
    request_body: SolicitudCambioContraseña,
    request: Request,
    db: Session = Depends(get_db)
):
    """
    📧 PASO 1: Solicitar token para cambiar contraseña
    
    Endpoint: POST /auth/solicitar-cambio-contrasena
    
    Body:
    {
        "correo": "inspector@example.com",
        "id_persona": 5
    }
    
    Respuesta:
    {
        "mensaje": "Token enviado al correo correctamente",
        "correo": "inspector@example.com",
        "expira_en_minutos": 15
    }
    """
    try:
        ip_address = obtener_ip_cliente(request)
        
        # Log de inicio de solicitud
        await LogServicio.registrar_accion_negocio(
            source="token_reset_router.solicitar_cambio_contrasena",
            accion="solicitud_token_reset_inicio",
            estado="pending",
            mensaje=f"Inicio de solicitud de cambio de contraseña",
            ip_address=ip_address,
            metadata={
                "correo": request_body.correo,
                "id_persona": request_body.id_persona,
                "user_agent": request.headers.get("User-Agent", "unknown")
            }
        )
        
        resultado = await token_reset_servicio.solicitar_token_cambio_contrasena(
            db, request_body, ip_address
        )
        
        return resultado
        
    except Exception as e:
        # Log de error en el router
        await LogServicio.registrar_error(
            source="token_reset_router.solicitar_cambio_contrasena",
            accion="solicitud_token_reset",
            error_message=str(e),
            ip_address=obtener_ip_cliente(request),
            metadata={
                "correo": request_body.correo if request_body else None,
                "id_persona": request_body.id_persona if request_body else None
            }
        )
        raise


@router.post("/confirmar-cambio-contrasena")
async def confirmar_cambio_contrasena(
    request_body: VerificarTokenReset,
    request: Request,
    db: Session = Depends(get_db)
):
    """
    🔐 PASO 2: Confirmar cambio con token y nueva contraseña
    
    Endpoint: POST /auth/confirmar-cambio-contrasena
    
    Body:
    {
        "token": "ABC123...",
        "nuevaContraseña": "MiNuevaContraseña123",
        "id_persona": 5
    }
    
    Respuesta:
    {
        "mensaje": "Contraseña actualizada correctamente",
        "correo": "inspector@example.com",
        "nombre": "Juan"
    }
    """
    try:
        ip_address = obtener_ip_cliente(request)
        
        # Log de inicio de confirmación (sin mostrar el token completo por seguridad)
        await LogServicio.registrar_accion_negocio(
            source="token_reset_router.confirmar_cambio_contrasena",
            accion="confirmar_cambio_contrasena_inicio",
            estado="pending",
            mensaje=f"Inicio de confirmación de cambio de contraseña",
            ip_address=ip_address,
            metadata={
                "id_persona": request_body.id_persona,
                "token_prefix": request_body.token[:8] + "..." if request_body.token else None,  # Solo primeros 8 chars
                "user_agent": request.headers.get("User-Agent", "unknown")
            }
        )
        
        resultado = await token_reset_servicio.verificar_token_y_cambiar_contrasena(
            db, request_body, ip_address
        )
        
        return resultado
        
    except Exception as e:
        # Log de error en el router
        await LogServicio.registrar_error(
            source="token_reset_router.confirmar_cambio_contrasena",
            accion="confirmar_cambio_contrasena",
            error_message=str(e),
            ip_address=obtener_ip_cliente(request),
            metadata={
                "id_persona": request_body.id_persona if request_body else None,
                "tiene_token": bool(request_body.token) if request_body else False
            }
        )
        raise
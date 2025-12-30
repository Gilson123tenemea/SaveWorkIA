from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.config import get_db
from app.esquemas.token_reset_esquema import (
    SolicitudCambioContraseña,
    VerificarTokenReset
)
from app.servicios import token_reset_servicio

router = APIRouter(prefix="/auth", tags=["Autenticación"])

@router.post("/solicitar-cambio-contrasena")
def solicitar_cambio_contrasena(
    request: SolicitudCambioContraseña, 
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
    return token_reset_servicio.solicitar_token_cambio_contrasena(db, request)


@router.post("/confirmar-cambio-contrasena")
def confirmar_cambio_contrasena(
    request: VerificarTokenReset, 
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
    return token_reset_servicio.verificar_token_y_cambiar_contrasena(db, request)
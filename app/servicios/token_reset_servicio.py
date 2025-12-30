import secrets
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from fastapi import HTTPException
from app.modelos.persona import Persona
from app.modelos.token_reset_modelo import TokenReset
from app.seguridad.hash_contrasena import encriptar_contrasena
from app.esquemas.token_reset_esquema import (
    SolicitudCambioContraseña,
    VerificarTokenReset
)
from app.servicios.email_servicio import enviar_email_token_cambio_contrasena

# ⏱️ Token válido por 15 minutos
EXPIRACION_TOKEN_MINUTOS = 15

def solicitar_token_cambio_contrasena(db: Session, datos: SolicitudCambioContraseña):
    """
    📧 PASO 1: Solicitar cambio de contraseña
    
    ✅ Valida que:
    - El correo pertenezca a la persona con id_persona
    - La persona esté activa
    
    ✅ Acciones:
    - Genera un token único
    - Lo guarda en BD con expiración
    - Envía el token al correo
    """
    
    # Buscar persona activa con este correo
    persona = db.query(Persona).filter(
        Persona.id_persona == datos.id_persona,
        Persona.correo == datos.correo,
        Persona.borrado == True  # Solo personas activas
    ).first()

    if not persona:
        raise HTTPException(
            status_code=404,
            detail="El correo no coincide con la persona registrada"
        )

    # ✅ Eliminar tokens anteriores válidos para esta persona
    db.query(TokenReset).filter(
        TokenReset.id_persona == datos.id_persona,
        TokenReset.usado == False,
        TokenReset.fecha_expiracion > datetime.utcnow()
    ).delete()
    db.commit()

    # 🔐 Generar token seguro (32 caracteres aleatorios)
    token_generado = secrets.token_urlsafe(32)

    # Calcular fecha de expiración
    fecha_creacion = datetime.utcnow()
    fecha_expiracion = fecha_creacion + timedelta(minutes=EXPIRACION_TOKEN_MINUTOS)

    # Guardar token en BD
    nuevo_token = TokenReset(
        id_persona=datos.id_persona,
        token=token_generado,
        correo=datos.correo,
        fecha_creacion=fecha_creacion,
        fecha_expiracion=fecha_expiracion,
        usado=False
    )
    db.add(nuevo_token)
    db.commit()
    db.refresh(nuevo_token)

    # 📧 Enviar token al correo
    try:
        enviar_email_token_cambio_contrasena(
            correo=datos.correo,
            nombre=persona.nombre,
            token=token_generado
        )
    except Exception as e:
        # Si falla el email, eliminar el token creado
        db.query(TokenReset).filter(TokenReset.id_token == nuevo_token.id_token).delete()
        db.commit()
        raise HTTPException(
            status_code=500,
            detail="Error al enviar el correo. Intente más tarde"
        )

    return {
        "mensaje": "Token enviado al correo correctamente",
        "correo": datos.correo,
        "expira_en_minutos": EXPIRACION_TOKEN_MINUTOS
    }


def verificar_token_y_cambiar_contrasena(db: Session, datos: VerificarTokenReset):
    """
    🔐 PASO 2: Cambiar contraseña con token
    
    ✅ Valida que:
    - El token exista
    - El token no esté expirado
    - El token no haya sido usado
    - La persona exista y esté activa
    
    ✅ Acciones:
    - Encripta la nueva contraseña
    - Actualiza en BD
    - Marca el token como usado
    """
    
    # Validar que la contraseña tenga mínimo 8 caracteres
    if len(datos.nuevaContraseña) < 8:
        raise HTTPException(
            status_code=400,
            detail="La contraseña debe tener mínimo 8 caracteres"
        )

    # Validar que la contraseña sea fuerte (al menos 1 mayúscula, 1 número)
    if not any(char.isupper() for char in datos.nuevaContraseña):
        raise HTTPException(
            status_code=400,
            detail="La contraseña debe contener al menos una mayúscula"
        )
    
    if not any(char.isdigit() for char in datos.nuevaContraseña):
        raise HTTPException(
            status_code=400,
            detail="La contraseña debe contener al menos un número"
        )

    # Buscar el token en BD
    token_registro = db.query(TokenReset).filter(
        TokenReset.token == datos.token,
        TokenReset.id_persona == datos.id_persona
    ).first()

    if not token_registro:
        raise HTTPException(
            status_code=400,
            detail="Token inválido"
        )

    # Verificar que no esté usado
    if token_registro.usado:
        raise HTTPException(
            status_code=400,
            detail="Este token ya fue utilizado"
        )

    # Verificar que no esté expirado
    if datetime.utcnow() > token_registro.fecha_expiracion:
        raise HTTPException(
            status_code=400,
            detail="El token ha expirado. Solicite uno nuevo"
        )

    # Buscar persona
    persona = db.query(Persona).filter(
        Persona.id_persona == datos.id_persona,
        Persona.borrado == True
    ).first()

    if not persona:
        raise HTTPException(
            status_code=404,
            detail="Persona no encontrada"
        )

    # ✅ Cambiar la contraseña
    persona.contrasena = encriptar_contrasena(datos.nuevaContraseña)

    # ✅ Marcar token como usado
    token_registro.usado = True

    db.commit()

    return {
        "mensaje": "Contraseña actualizada correctamente",
        "correo": persona.correo,
        "nombre": persona.nombre
    }


def limpiar_tokens_expirados(db: Session):
    """
    Limpia tokens expirados de la BD
    (Ejecutar periódicamente con una tarea programada)
    """
    eliminados = db.query(TokenReset).filter(
        TokenReset.fecha_expiracion < datetime.utcnow()
    ).delete()
    db.commit()
    return {"tokens_eliminados": eliminados}
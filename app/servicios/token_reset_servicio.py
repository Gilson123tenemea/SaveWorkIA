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

# Importar servicio de logs
from app.servicios.log_service import LogServicio

# ⏱️ Token válido por 15 minutos
EXPIRACION_TOKEN_MINUTOS = 15


async def solicitar_token_cambio_contrasena(
    db: Session, 
    datos: SolicitudCambioContraseña,
    ip_address: str = None
):
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
    
    try:
        # Log de solicitud de cambio de contraseña iniciada
        await LogServicio.registrar_autenticacion(
            source="token_reset_servicio.solicitar_token_cambio_contrasena",
            accion="solicitud_cambio_contrasena",
            correo=datos.correo,
            estado="pending",
            ip_address=ip_address,
            user_id=datos.id_persona,
            mensaje=f"Solicitud de cambio de contraseña para: {datos.correo}"
        )
        
        # Buscar persona activa con este correo
        persona = db.query(Persona).filter(
            Persona.id_persona == datos.id_persona,
            Persona.correo == datos.correo,
            Persona.borrado == True  # Solo personas activas
        ).first()

        if not persona:
            # Log de solicitud fallida - correo no coincide
            await LogServicio.registrar_autenticacion(
                source="token_reset_servicio.solicitar_token_cambio_contrasena",
                accion="solicitud_cambio_contrasena_fallida",
                correo=datos.correo,
                estado="failed",
                ip_address=ip_address,
                user_id=datos.id_persona,
                mensaje="Correo no coincide con la persona registrada",
                error="Correo o ID de persona inválidos"
            )
            raise HTTPException(
                status_code=404,
                detail="El correo no coincide con la persona registrada"
            )

        # ✅ Eliminar tokens anteriores válidos para esta persona
        tokens_eliminados = db.query(TokenReset).filter(
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
            
            # Log de token generado y enviado exitosamente
            await LogServicio.registrar_autenticacion(
                source="token_reset_servicio.solicitar_token_cambio_contrasena",
                accion="token_cambio_contrasena_enviado",
                correo=datos.correo,
                estado="success",
                ip_address=ip_address,
                user_id=datos.id_persona,
                mensaje=f"Token de cambio de contraseña enviado a: {datos.correo}",
                metadata={
                    "id_token": nuevo_token.id_token,
                    "expiracion_minutos": EXPIRACION_TOKEN_MINUTOS,
                    "fecha_expiracion": fecha_expiracion.isoformat(),
                    "tokens_anteriores_eliminados": tokens_eliminados,
                    "nombre_usuario": persona.nombre,
                    "rol": persona.rol
                }
            )
            
        except Exception as e:
            # Si falla el email, eliminar el token creado
            db.query(TokenReset).filter(TokenReset.id_token == nuevo_token.id_token).delete()
            db.commit()
            
            # Log de error al enviar email
            await LogServicio.registrar_error(
                source="token_reset_servicio.solicitar_token_cambio_contrasena",
                accion="envio_email_token",
                error_message=f"Error al enviar email: {str(e)}",
                user_id=datos.id_persona,
                ip_address=ip_address,
                metadata={
                    "correo": datos.correo,
                    "error_detalle": str(e)
                }
            )
            
            raise HTTPException(
                status_code=500,
                detail="Error al enviar el correo. Intente más tarde"
            )

        return {
            "mensaje": "Token enviado al correo correctamente",
            "correo": datos.correo,
            "expira_en_minutos": EXPIRACION_TOKEN_MINUTOS
        }
        
    except HTTPException:
        raise
    except Exception as e:
        # Log de error general
        await LogServicio.registrar_error(
            source="token_reset_servicio.solicitar_token_cambio_contrasena",
            accion="solicitud_cambio_contrasena",
            error_message=str(e),
            user_id=datos.id_persona if datos else None,
            ip_address=ip_address,
            metadata={
                "correo": datos.correo if datos else None
            }
        )
        raise


async def verificar_token_y_cambiar_contrasena(
    db: Session, 
    datos: VerificarTokenReset,
    ip_address: str = None
):
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
    
    try:
        # Log de intento de cambio de contraseña con token
        await LogServicio.registrar_autenticacion(
            source="token_reset_servicio.verificar_token_y_cambiar_contrasena",
            accion="verificar_token_cambio_contrasena",
            correo=None,  # No tenemos correo aún
            estado="pending",
            ip_address=ip_address,
            user_id=datos.id_persona,
            mensaje=f"Intento de cambio de contraseña con token para persona {datos.id_persona}"
        )
        
        # Validar que la contraseña tenga mínimo 8 caracteres
        if len(datos.nuevaContraseña) < 8:
            await LogServicio.registrar_autenticacion(
                source="token_reset_servicio.verificar_token_y_cambiar_contrasena",
                accion="cambio_contrasena_fallido",
                correo=None,
                estado="failed",
                ip_address=ip_address,
                user_id=datos.id_persona,
                mensaje="Contraseña rechazada: menos de 8 caracteres",
                error="Contraseña muy corta"
            )
            raise HTTPException(
                status_code=400,
                detail="La contraseña debe tener mínimo 8 caracteres"
            )

        # Validar que la contraseña sea fuerte (al menos 1 mayúscula, 1 número)
        if not any(char.isupper() for char in datos.nuevaContraseña):
            await LogServicio.registrar_autenticacion(
                source="token_reset_servicio.verificar_token_y_cambiar_contrasena",
                accion="cambio_contrasena_fallido",
                correo=None,
                estado="failed",
                ip_address=ip_address,
                user_id=datos.id_persona,
                mensaje="Contraseña rechazada: sin mayúsculas",
                error="Contraseña débil"
            )
            raise HTTPException(
                status_code=400,
                detail="La contraseña debe contener al menos una mayúscula"
            )
        
        if not any(char.isdigit() for char in datos.nuevaContraseña):
            await LogServicio.registrar_autenticacion(
                source="token_reset_servicio.verificar_token_y_cambiar_contrasena",
                accion="cambio_contrasena_fallido",
                correo=None,
                estado="failed",
                ip_address=ip_address,
                user_id=datos.id_persona,
                mensaje="Contraseña rechazada: sin números",
                error="Contraseña débil"
            )
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
            await LogServicio.registrar_autenticacion(
                source="token_reset_servicio.verificar_token_y_cambiar_contrasena",
                accion="cambio_contrasena_fallido",
                correo=None,
                estado="failed",
                ip_address=ip_address,
                user_id=datos.id_persona,
                mensaje="Token inválido proporcionado",
                error="Token no existe"
            )
            raise HTTPException(
                status_code=400,
                detail="Token inválido"
            )

        # Verificar que no esté usado
        if token_registro.usado:
            await LogServicio.registrar_autenticacion(
                source="token_reset_servicio.verificar_token_y_cambiar_contrasena",
                accion="cambio_contrasena_fallido",
                correo=token_registro.correo,
                estado="failed",
                ip_address=ip_address,
                user_id=datos.id_persona,
                mensaje="Intento de usar token ya utilizado",
                error="Token ya usado",
                metadata={
                    "id_token": token_registro.id_token,
                    "fecha_creacion": token_registro.fecha_creacion.isoformat()
                }
            )
            raise HTTPException(
                status_code=400,
                detail="Este token ya fue utilizado"
            )

        # Verificar que no esté expirado
        if datetime.utcnow() > token_registro.fecha_expiracion:
            await LogServicio.registrar_autenticacion(
                source="token_reset_servicio.verificar_token_y_cambiar_contrasena",
                accion="cambio_contrasena_fallido",
                correo=token_registro.correo,
                estado="failed",
                ip_address=ip_address,
                user_id=datos.id_persona,
                mensaje="Intento de usar token expirado",
                error="Token expirado",
                metadata={
                    "id_token": token_registro.id_token,
                    "fecha_expiracion": token_registro.fecha_expiracion.isoformat(),
                    "tiempo_expirado_minutos": int((datetime.utcnow() - token_registro.fecha_expiracion).total_seconds() / 60)
                }
            )
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
            await LogServicio.registrar_autenticacion(
                source="token_reset_servicio.verificar_token_y_cambiar_contrasena",
                accion="cambio_contrasena_fallido",
                correo=token_registro.correo,
                estado="failed",
                ip_address=ip_address,
                user_id=datos.id_persona,
                mensaje="Persona no encontrada o inactiva",
                error="Usuario no existe"
            )
            raise HTTPException(
                status_code=404,
                detail="Persona no encontrada"
            )

        # ✅ Cambiar la contraseña
        persona.contrasena = encriptar_contrasena(datos.nuevaContraseña)

        # ✅ Marcar token como usado
        token_registro.usado = True

        db.commit()

        # Log de cambio de contraseña exitoso
        await LogServicio.registrar_autenticacion(
            source="token_reset_servicio.verificar_token_y_cambiar_contrasena",
            accion="cambio_contrasena_exitoso",
            correo=persona.correo,
            estado="success",
            ip_address=ip_address,
            user_id=datos.id_persona,
            mensaje=f"Contraseña actualizada exitosamente para: {persona.correo}",
            metadata={
                "id_token": token_registro.id_token,
                "nombre_usuario": persona.nombre,
                "rol": persona.rol,
                "fecha_token_creado": token_registro.fecha_creacion.isoformat(),
                "tiempo_uso_token_minutos": int((datetime.utcnow() - token_registro.fecha_creacion).total_seconds() / 60)
            }
        )

        return {
            "mensaje": "Contraseña actualizada correctamente",
            "correo": persona.correo,
            "nombre": persona.nombre
        }
        
    except HTTPException:
        raise
    except Exception as e:
        # Log de error general
        await LogServicio.registrar_error(
            source="token_reset_servicio.verificar_token_y_cambiar_contrasena",
            accion="cambio_contrasena",
            error_message=str(e),
            user_id=datos.id_persona if datos else None,
            ip_address=ip_address
        )
        raise


async def limpiar_tokens_expirados(db: Session):
    """
    Limpia tokens expirados de la BD
    (Ejecutar periódicamente con una tarea programada)
    """
    try:
        eliminados = db.query(TokenReset).filter(
            TokenReset.fecha_expiracion < datetime.utcnow()
        ).delete()
        db.commit()
        
        # Log de limpieza de tokens
        await LogServicio.registrar_accion_negocio(
            source="token_reset_servicio.limpiar_tokens_expirados",
            accion="limpieza_tokens_expirados",
            estado="success",
            mensaje=f"Limpieza de tokens expirados: {eliminados} tokens eliminados",
            metadata={
                "tokens_eliminados": eliminados,
                "fecha_limpieza": datetime.utcnow().isoformat()
            }
        )
        
        return {"tokens_eliminados": eliminados}
        
    except Exception as e:
        # Log de error en limpieza
        await LogServicio.registrar_error(
            source="token_reset_servicio.limpiar_tokens_expirados",
            accion="limpieza_tokens_expirados",
            error_message=str(e)
        )
        raise
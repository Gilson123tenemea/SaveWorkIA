
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from datetime import datetime
from app.modelos.fcm_token_modelo import FCMToken
from app.modelos.inspector import Inspector
from app.esquemas.fcm_token_esquema import FCMTokenRegistro

def registrar_token_fcm(
    db: Session,
    id_inspector: int,
    datos: FCMTokenRegistro
):
    """
    ✅ Registra un nuevo token FCM para un inspector
    
    Un inspector puede tener múltiples tokens (logeado en varios celulares)
    Cada vez que se logea en un nuevo celular, se crea un nuevo registro
    
    Flujo:
    1. Verifica que el inspector exista y esté activo
    2. Verifica que el token no esté duplicado
    3. Si es nuevo → lo crea
    """
    
    # 🔎 PASO 1: Validar que el inspector existe y está activo
    inspector = db.query(Inspector).filter(
        Inspector.id_inspector == id_inspector,
        Inspector.borrado == True
    ).first()

    if not inspector:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Inspector no encontrado o inactivo"
        )

    print(f"✅ Inspector validado: {inspector.id_inspector}")

    # 🔎 PASO 2: Buscar si el token ya existe
    token_existente = db.query(FCMToken).filter(
        FCMToken.token_fcm == datos.token_fcm,
        FCMToken.borrado == True
    ).first()

    if token_existente:
        # Token ya está registrado → no hacer nada
        print(f"⚠️ Token ya existe para inspector {token_existente.id_inspector}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Este token ya está registrado"
        )

    # 🔎 PASO 3: Crear nuevo token FCM
    print(f"✨ Creando nuevo token FCM para inspector {id_inspector}...")
    
    nuevo_token = FCMToken(
        id_inspector=id_inspector,
        token_fcm=datos.token_fcm,
        borrado=True
    )
    
    db.add(nuevo_token)
    db.commit()
    db.refresh(nuevo_token)

    print(f"✅ Token creado: {nuevo_token.id_fcm_token}")

    return {
        "mensaje": "Token FCM registrado correctamente",
        "id_fcm_token": nuevo_token.id_fcm_token,
        "id_inspector": id_inspector,
        "token_fcm": datos.token_fcm[:20] + "...",
        "fecha_registro": nuevo_token.fecha_registro.isoformat()
    }

def obtener_tokens_inspector(db: Session, id_inspector: int):
    """
    📋 Obtiene todos los tokens FCM activos de un inspector
    (todos los celulares en los que está logeado)
    """
    # Validar que el inspector existe
    inspector = db.query(Inspector).filter(
        Inspector.id_inspector == id_inspector,
        Inspector.borrado == True
    ).first()

    if not inspector:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Inspector no encontrado"
        )

    # Consultar tokens activos del inspector
    tokens = db.query(FCMToken).filter(
        FCMToken.id_inspector == id_inspector,
        FCMToken.borrado == True
    ).all()

    return [
        {
            "id_fcm_token": token.id_fcm_token,
            "id_inspector": token.id_inspector,
            "token_fcm": token.token_fcm[:20] + "...",
            "fecha_registro": token.fecha_registro.isoformat()
        }
        for token in tokens
    ]

def eliminar_token_fcm(db: Session, id_inspector: int, token_fcm: str):
    """
    🗑️ Elimina (borrado lógico) un token FCM
    
    Cuando el usuario hace logout desde un celular
    """
    # Buscar token
    token = db.query(FCMToken).filter(
        FCMToken.id_inspector == id_inspector,
        FCMToken.token_fcm == token_fcm,
        FCMToken.borrado == True
    ).first()

    if not token:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Token no encontrado para este inspector"
        )

    # Borrado lógico
    token.borrado = False
    db.commit()

    print(f"🗑️ Token eliminado para inspector {id_inspector}")

    return {
        "mensaje": "Token eliminado correctamente",
        "id_fcm_token": token.id_fcm_token,
        "id_inspector": id_inspector
    }

def obtener_tokens_para_notificacion(db: Session, id_inspector: int) -> list:
    """
    🔔 Obtiene TODOS los tokens activos de un inspector
    para enviar notificaciones a TODOS sus dispositivos
    """
    tokens = db.query(FCMToken).filter(
        FCMToken.id_inspector == id_inspector,
        FCMToken.borrado == True
    ).all()

    if not tokens:
        print(f"⚠️ Inspector {id_inspector} no tiene tokens activos")
        return []
    
    print(f"✅ {len(tokens)} tokens encontrados para inspector {id_inspector}")
    return [token.token_fcm for token in tokens]
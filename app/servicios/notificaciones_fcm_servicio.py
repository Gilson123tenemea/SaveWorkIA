import firebase_admin
from firebase_admin import credentials, messaging
from sqlalchemy.orm import Session
from app.modelos.fcm_token_modelo import FCMToken
import os

class NotificacionesFCMServicio:
    """
    Servicio para enviar notificaciones push a través de Firebase Admin SDK
    """
    
    # Inicializar Firebase (solo una vez)
    _inicializado = False
    
    @staticmethod
    def inicializar():
        """Inicializa Firebase Admin SDK"""
        if NotificacionesFCMServicio._inicializado:
            return
        
        try:
            # Ruta al archivo de credenciales
            # Tu google-services.json convertido a formato Admin SDK
            ruta_credenciales = os.path.join(
                os.path.dirname(__file__),
                '../configuracion/saveworkia-firebase-adminsdk-fbsvc-f8d50b63fe.json'
            )
            
            # Inicializar solo si el archivo existe
            if os.path.exists(ruta_credenciales):
                cred = credentials.Certificate(ruta_credenciales)
                firebase_admin.initialize_app(cred)
                print('✅ Firebase Admin SDK inicializado')
                NotificacionesFCMServicio._inicializado = True
            else:
                print(f'⚠️ Archivo no encontrado: {ruta_credenciales}')
                
        except Exception as e:
            print(f'❌ Error inicializando Firebase: {e}')
    
    @staticmethod
    def enviar_notificacion_inspector(
        db: Session,
        id_inspector: int,
        titulo: str,
        cuerpo: str,
        datos: dict = None
    ) -> bool:
        """
        Envía notificación a TODOS los dispositivos de un inspector
        
        Args:
            db: Sesión de BD
            id_inspector: ID del inspector
            titulo: Título de la notificación
            cuerpo: Cuerpo del mensaje
            datos: Datos adicionales (dict)
        
        Returns:
            True si se envió, False si falló
        """
        
        print(f'\n📤 === ENVIANDO NOTIFICACIÓN AL INSPECTOR {id_inspector} === 📤')
        
        # Inicializar Firebase si no está listo
        NotificacionesFCMServicio.inicializar()
        
        # 1️⃣ Obtener todos los tokens activos del inspector
        tokens = db.query(FCMToken).filter(
            FCMToken.id_inspector == id_inspector,
            FCMToken.borrado == True  # Solo activos
        ).all()
        
        if not tokens:
            print(f'⚠️ Inspector {id_inspector} no tiene tokens registrados')
            return False
        
        print(f'✅ {len(tokens)} token(s) encontrado(s)')
        
        # 2️⃣ Enviar a cada token
        tokens_exitosos = 0
        for token in tokens:
            try:
                # Crear mensaje
                mensaje = messaging.Message(
                    notification=messaging.Notification(
                        title=titulo,
                        body=cuerpo
                    ),
                    data=datos or {},
                    token=token.token_fcm
                )
                
                # Enviar
                response = messaging.send(mensaje)
                
                print(f'✅ Enviado a: {token.token_fcm[:20]}...')
                tokens_exitosos += 1
                
            except Exception as e:
                print(f'❌ Error enviando a {token.token_fcm[:20]}...: {e}')
        
        print(f'✅ Notificaciones exitosas: {tokens_exitosos}/{len(tokens)}\n')
        return tokens_exitosos > 0
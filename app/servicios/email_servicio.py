# -*- coding: utf-8 -*-
import smtplib
import logging
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.header import Header
from email.utils import formataddr
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 📧 CONFIGURACIÓN - EMAIL QUE ENVIARÁ LOS TOKENS
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
SENDER_EMAIL = os.getenv("SMTP_EMAIL")  # TU email, NO el del usuario
SENDER_PASSWORD = os.getenv("SMTP_PASSWORD")  # Contraseña de app

if not SENDER_EMAIL or not SENDER_PASSWORD:
    raise ValueError("Configura SMTP_EMAIL y SMTP_PASSWORD en .env")

def enviar_email_token_cambio_contrasena(correo: str, nombre: str, token: str):
    """
    Envía un token al correo del USUARIO para que cambie su contraseña
    
    correo: Email del USUARIO (ej: tenemeaaguilar@gmail.com)
    nombre: Nombre del USUARIO
    token: Token generado
    """
    
    try:
        mensaje = MIMEMultipart("alternative")
        mensaje["Subject"] = Header("Token de Cambio de Contrasena", "utf-8")
        mensaje["From"] = formataddr((str(Header("Sistema de Supervision", "utf-8")), SENDER_EMAIL))
        mensaje["To"] = correo  # ← Aquí va el email del USUARIO

        html = """
        <html>
          <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
              <h2 style="color: #2563eb;">Cambio de Contrasena</h2>
              
              <p>Hola <strong>{nombre}</strong>,</p>
              
              <p>Solicitaste cambiar tu contrasena en el Sistema de Supervision.</p>
              
              <div style="background-color: #f3f4f6; padding: 15px; border-radius: 8px; margin: 20px 0;">
                <p style="margin: 0; color: #6b7280; font-size: 12px;">Tu token de validacion es:</p>
                <p style="margin: 10px 0; font-size: 24px; font-weight: bold; color: #2563eb; letter-spacing: 3px; font-family: monospace;">
                  {token}
                </p>
              </div>
              
              <p style="color: #ef4444;"><strong>Importante:</strong></p>
              <ul style="color: #6b7280; margin: 10px 0;">
                <li>Este token expira en <strong>15 minutos</strong></li>
                <li>No compartas este token con nadie</li>
                <li>Si no solicitaste este cambio, ignora este email</li>
                <li>Solo podras usar este token una vez</li>
              </ul>
              
              <hr style="border: none; border-top: 1px solid #e5e7eb; margin: 20px 0;">
              
              <p style="color: #9ca3af; font-size: 12px;">
                Sistema de Supervision de Seguridad<br>
                2026 Todos los derechos reservados
              </p>
            </div>
          </body>
        </html>
        """.format(nombre=nombre, token=token)

        parte_html = MIMEText(html, "html", "utf-8")
        mensaje.attach(parte_html)

        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(SENDER_EMAIL, SENDER_PASSWORD)  # Login con TU email
            server.send_message(mensaje)
            
        logger.info(f"Email enviado a {correo}")
        return True
        
    except Exception as e:
        logger.error(f"Error al enviar email: {str(e)}")
        import traceback
        traceback.print_exc()
        raise Exception(f"No se pudo enviar el email: {str(e)}")
# app/routers/camara_ia.py
"""
Router para manejo de streams de webcam con detección YOLO
Captura frames en buffer para posterior análisis de EPP
"""

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
import cv2
from sqlalchemy.orm import Session
from app.servicios.deteccion_epp import procesar_frame
from app.servicios.camara_servicio import obtener_camara_por_id
from app.servicios.camara_buffer_servicio import (
    actualizar_buffer_frame,
    limpiar_buffer_camara,
    obtener_estado_buffers
)
from app.config import get_db

router = APIRouter(prefix="/webcam", tags=["IA - Webcam"])

# Variables globales para manejar múltiples cámaras
camaras_activas = {}  # {id_camara: cv2.VideoCapture}


def generar_stream_webcam(id_camara: int, ip_address: str):
    """
    Genera stream MJPEG optimizado para una cámara específica.
    
    Flujo:
    1. Abre cámara (local o remota)
    2. Captura frames continuamente
    3. Procesa con YOLO (skip_frames=2)
    4. Guarda último frame en buffer
    5. Envía MJPEG al cliente
    
    Args:
        id_camara: ID de la cámara en BD
        ip_address: IP o "127.0.0.1" para local
    """
    
    # 1️⃣ ABRIR CÁMARA
    if "127.0.0.1" in ip_address or "localhost" in ip_address:
        # Cámara local
        backends = [
            (cv2.CAP_DSHOW, "DirectShow"),
            (cv2.CAP_MSMF, "MSMF"),
            (0, "Default")
        ]
        
        cap = None
        for backend, name in backends:
            try:
                cap = cv2.VideoCapture(0, backend)
                if cap.isOpened():
                    print(f"✅ Cámara local abierta con {name} (ID: {id_camara})")
                    break
                else:
                    cap.release()
            except:
                pass
        
        if cap is None or not cap.isOpened():
            print(f"❌ No se pudo abrir cámara con ningún backend")
            return
    else:
        # Cámara remota
        stream_url = f"rtsp://{ip_address}"
        cap = cv2.VideoCapture(stream_url)
        print(f"✅ Conectando a cámara remota: {stream_url}")
    
    camaras_activas[id_camara] = cap
    
    # 2️⃣ CONFIGURAR CÁMARA
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    cap.set(cv2.CAP_PROP_FPS, 30)
    cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
    cap.set(cv2.CAP_PROP_AUTOFOCUS, 1)
    
    if not cap.isOpened():
        print(f"❌ No se pudo abrir cámara ID: {id_camara}")
        camaras_activas.pop(id_camara, None)
        cap.release()
        return
    
    print(f"✅ Cámara {id_camara} abierta correctamente")
    
    frame_count = 0
    reintentos_fallidos = 0
    
    try:
        while True:
            ret, frame = cap.read()
            
            if not ret:
                reintentos_fallidos += 1
                if reintentos_fallidos > 10:
                    print(f"❌ Cámara {id_camara} desconectada después de 10 intentos")
                    break
                print(f"⚠ Reintento {reintentos_fallidos}/10 para cámara {id_camara}")
                import time
                time.sleep(0.5)
                continue
            
            reintentos_fallidos = 0
            
            # 3️⃣ FLIP Y PROCESAR
            frame = cv2.flip(frame, 1)
            
            # 4️⃣ PROCESAR CON YOLO (skip_frames=2 → procesa cada 2 frames)
            frame_anotado, detecciones = procesar_frame(
                frame,
                id_camara=id_camara,
                skip_frames=2
            )
            
            frame_count += 1
            
            # 5️⃣ 🔥 GUARDAR FRAME EN BUFFER (para análisis posterior)
            actualizar_buffer_frame(id_camara, frame)
            
            # Log cada 30 frames
            if frame_count % 30 == 0:
                print(f"✅ Cámara {id_camara} | Frame {frame_count} | "
                      f"Detecciones: {len(detecciones) if detecciones is not None else 0}")
            
            # 6️⃣ CODIFICAR A JPEG
            _, buffer = cv2.imencode(
                ".jpg",
                frame_anotado,
                [cv2.IMWRITE_JPEG_QUALITY, 70]
            )
            frame_bytes = buffer.tobytes()
            
            # 7️⃣ ENVIAR FRAME AL CLIENTE (MJPEG)
            yield (
                b"--frame\r\n"
                b"Content-Type: image/jpeg\r\n"
                b"Content-Length: " + str(len(frame_bytes)).encode() + b"\r\n\r\n"
                + frame_bytes
                + b"\r\n"
            )
            
    except GeneratorExit:
        print(f"🔴 Stream terminado para cámara {id_camara}")
    except Exception as e:
        print(f"❌ Error en stream de cámara {id_camara}: {e}")
    finally:
        # 8️⃣ LIMPIAR RECURSOS
        if id_camara in camaras_activas:
            camaras_activas[id_camara].release()
            camaras_activas.pop(id_camara, None)
            limpiar_buffer_camara(id_camara)  # Limpiar buffer
            print(f"✅ Cámara {id_camara} liberada")


@router.get("/stream/{id_camara}")
async def stream_webcam(id_camara: int, db: Session = Depends(get_db)):
    """
    Inicia stream de webcam usando ID de cámara.
    Recupera IP de la BD y conecta a esa cámara.
    
    Returns:
        StreamingResponse con MJPEG
    """
    try:
        # Obtener cámara de BD
        camara = obtener_camara_por_id(db, id_camara)
        
        print(f"🎥 Iniciando stream para cámara ID {id_camara} | IP: {camara.ipAddress}")
        
        return StreamingResponse(
            generar_stream_webcam(id_camara, camara.ipAddress),
            media_type="multipart/x-mixed-replace; boundary=frame"
        )
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/stop/{id_camara}")
async def detener_stream(id_camara: int):
    """
    Detiene el stream de una cámara específica.
    Libera recursos y limpia buffer.
    """
    if id_camara in camaras_activas:
        cap = camaras_activas[id_camara]
        cap.release()
        camaras_activas.pop(id_camara, None)
        limpiar_buffer_camara(id_camara)
        
        return {
            "status": "✅ Cámara detenida",
            "id_camara": id_camara
        }
    
    return {
        "status": "⚠ Cámara no encontrada",
        "id_camara": id_camara
    }


@router.get("/camaras-activas")
async def listar_camaras_activas():
    """Lista todas las cámaras activas."""
    return {
        "camaras_activas": list(camaras_activas.keys()),
        "total": len(camaras_activas)
    }


@router.get("/estado-buffers")
async def estado_buffers():
    """Retorna estado de buffers de frames (debugging)."""
    return obtener_estado_buffers()
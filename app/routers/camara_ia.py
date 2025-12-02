from fastapi import APIRouter
from fastapi.responses import StreamingResponse
import time
import cv2
from app.servicios.deteccion_epp import procesar_frame  # Importa la función optimizada

router = APIRouter(prefix="/webcam", tags=["IA - Webcam"])

# Variables globales para la webcam
cap = None
frame_actual = None

def generar_stream_webcam():
    """Genera stream MJPEG optimizado."""
    global cap, frame_actual
    
    # 5️⃣ ABRIR WEBCAM CON MEJOR CONFIGURACIÓN
    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)   # Resolución fija
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    cap.set(cv2.CAP_PROP_FPS, 30)
    cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)  # Buffer pequeño = frames frescos
    
    # Para hardware acceleration (si tu cámara lo soporta)
    cap.set(cv2.CAP_PROP_AUTOFOCUS, 1)
    
    if not cap.isOpened():
        print("❌ No se pudo abrir la webcam")
        cap.release()
        return
    
    print("✅ Webcam abierta correctamente")
    
    frame_count = 0
    
    try:
        while True:
            ret, frame = cap.read()
            
            if not ret:
                print("⚠ No se pudo leer frame, reintentando...")
                continue
            
            # 6️⃣ FLIP SOLO SI ES NECESARIO
            frame = cv2.flip(frame, 1)
            
            # 7️⃣ DETECCIÓN (aquí está el procesamiento pesado)
            frame_anotado, detecciones = procesar_frame(frame)
            
            frame_actual = frame_anotado
            frame_count += 1
            
            # Mostrar FPS cada 30 frames
            if frame_count % 30 == 0:
                print(f"✅ Frame {frame_count} procesado | "
                      f"Detecciones: {len(detecciones) if detecciones is not None else 0}")
            
            # 8️⃣ CODIFICAR A JPEG (compresión más agresiva)
            _, buffer = cv2.imencode(
                ".jpg", 
                frame_anotado,
                [cv2.IMWRITE_JPEG_QUALITY, 70]  # Calidad 70 (0-100)
            )
            frame_bytes = buffer.tobytes()
            
            # 9️⃣ ENVIAR FRAME
            yield (
                b"--frame\r\n"
                b"Content-Type: image/jpeg\r\n"
                b"Content-Length: " + str(len(frame_bytes)).encode() + b"\r\n\r\n"
                + frame_bytes
                + b"\r\n"
            )
            
            # NO USAR time.sleep() - puede causar lentitud
            # El stream se regula naturalmente por la velocidad de lectura
            
    except GeneratorExit:
        print("🔴 Stream terminado por cliente...")
    except Exception as e:
        print(f"❌ Error en stream: {e}")
    finally:
        if cap:
            cap.release()
            print("✅ Webcam liberada")


@router.get("/stream")
async def stream_webcam():
    """Endpoint para obtener stream de webcam."""
    return StreamingResponse(
        generar_stream_webcam(),
        media_type="multipart/x-mixed-replace; boundary=frame"
    )


@router.get("/health")
async def health_check():
    """Verificar si hay stream activo."""
    return {
        "status": "online",
        "frame_actual": frame_actual is not None
    }
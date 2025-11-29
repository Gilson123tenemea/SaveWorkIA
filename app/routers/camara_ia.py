from fastapi import APIRouter
from fastapi.responses import StreamingResponse
import cv2
import time
from app.servicios.deteccion_epp import procesar_frame

router = APIRouter(prefix="/webcam", tags=["IA - Webcam"])

def generar_stream_webcam():
    cap = cv2.VideoCapture(0)  # 0 = Webcam del computador

    if not cap.isOpened():
        print("❌ No se pudo abrir la webcam")
        return

    print("✅ Webcam abierta correctamente")

    while True:
        ret, frame = cap.read()
        if not ret:
            continue
        frame = cv2.flip(frame, 1)

        # Procesar con YOLO
        frame_anotado, _ = procesar_frame(frame)

        _, buffer = cv2.imencode(".jpg", frame_anotado)
        frame_bytes = buffer.tobytes()

        yield (
            b"--frame\r\n"
            b"Content-Type: image/jpeg\r\n\r\n" + frame_bytes + b"\r\n"
        )

        time.sleep(0.066)


@router.get("/stream")
async def stream_webcam():
    return StreamingResponse(
        generar_stream_webcam(),
        media_type="multipart/x-mixed-replace; boundary=frame"
    )

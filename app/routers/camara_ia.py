from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import StreamingResponse
import cv2
import time

from app.config import get_db
from app.servicios.deteccion_epp import procesar_frame
from app.servicios.camara_servicio import obtener_camara_por_id

router = APIRouter(prefix="/ia/camaras", tags=["IA - Cámaras"])


def generar_stream(url_stream):
    cap = cv2.VideoCapture(url_stream)

    if not cap.isOpened():
        raise HTTPException(status_code=400, detail="No se pudo conectar a la cámara")

    while True:
        ret, frame = cap.read()
        if not ret:
            continue

        # Procesar con YOLO
        frame_anotado, _ = procesar_frame(frame)

        _, buffer = cv2.imencode(".jpg", frame_anotado)
        frame_bytes = buffer.tobytes()

        yield (
            b"--frame\r\n"
            b"Content-Type: image/jpeg\r\n\r\n" + frame_bytes + b"\r\n"
        )

        time.sleep(0.03)


@router.get("/{id_camara}/stream")
async def stream_con_ia(id_camara: int, db=Depends(get_db)):
    camara = obtener_camara_por_id(db, id_camara)

    if not camara:
        raise HTTPException(status_code=404, detail="Cámara no encontrada")

    print("📷 Cámara encontrada:", camara.__dict__)

    # ✔ Aquí se toma la URL real desde ipAddress
    url_stream = camara.ipAddress

    return StreamingResponse(
        generar_stream(url_stream),
        media_type="multipart/x-mixed-replace; boundary=frame"
    )

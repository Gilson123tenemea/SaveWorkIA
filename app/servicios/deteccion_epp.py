from ultralytics import YOLO
import cv2
import numpy as np

# Cargar modelo YOLO
model = YOLO("app/modelos_yolo/best.pt")


def procesar_frame(frame):
    """Procesa un frame y devuelve detecciones + frame con bounding boxes."""

    img = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    resultados = model.predict(img, imgsz=640, conf=0.5)

    anotado = resultados[0].plot()  # Esto está en RGB

    # 🔥 Convertir RGB → BGR para que los colores se vean normales
    anotado_bgr = cv2.cvtColor(anotado, cv2.COLOR_RGB2BGR)

    return anotado_bgr, resultados[0].boxes

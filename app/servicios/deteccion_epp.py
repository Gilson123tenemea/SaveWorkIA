from ultralytics import YOLO
import cv2
import numpy as np

# Cargar modelo YOLO
model = YOLO("app/modelos_yolo/best.pt")


def procesar_frame(frame):
    """Procesa un frame y devuelve detecciones + frame con bounding boxes."""

    # Convertir a formato correcto
    img = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    # Realizar predicción
    resultados = model.predict(img, imgsz=640, conf=0.5)

    # Dibujar cuadros
    anotado = resultados[0].plot()  # retorna imagen con bounding boxes

    return anotado, resultados[0].boxes

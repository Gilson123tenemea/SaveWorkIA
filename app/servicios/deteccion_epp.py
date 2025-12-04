from ultralytics import YOLO
import cv2
import numpy as np
from sqlalchemy.orm import Session
from app.modelos.camara_modelo import Camara
import time

# Cargar modelo YOLO UNA SOLA VEZ
model = YOLO("app/modelos_yolo/best.pt")

# 🔥 PRECALENTAR MODELO (warmup) - evita delay en primera inferencia
dummy_frame = np.zeros((480, 640, 3), dtype=np.uint8)
model.predict(dummy_frame, imgsz=416, verbose=False)
print("✅ Modelo precalentado")

# Variables para caché de detecciones
cache_detecciones = {}
frame_contador_cache = {}

def procesar_frame(frame, id_camara: int = 1, skip_frames: int = 2):
    """
    Procesa un frame y devuelve detecciones.
    Skip_frames: procesa cada N frames (2 = cada 2 frames, 3 = cada 3 frames)
    """
    
    if id_camara not in frame_contador_cache:
        frame_contador_cache[id_camara] = 0
        cache_detecciones[id_camara] = None
    
    frame_contador_cache[id_camara] += 1
    frame_anotado = frame.copy()
    
    # 🔥 OPTIMIZACIÓN: Procesar solo cada N frames
    if frame_contador_cache[id_camara] % skip_frames == 0:
        # 1️⃣ OPTIMIZACIÓN: Procesar directamente en BGR
        resultados = model.predict(
            frame, 
            imgsz=416,  # ⚡ Tamaño óptimo para velocidad en CPU
            conf=0.25,  # Reducir confianza para detectar MÁS objetos
            iou=0.4,    # Reducir IOU para evitar fusionar detecciones
            verbose=False  # No imprimir logs
        )
        
        boxes = resultados[0].boxes
        cache_detecciones[id_camara] = boxes
    else:
        # Reutilizar detecciones del frame anterior (más rápido)
        boxes = cache_detecciones[id_camara]
    
    # 2️⃣ DIBUJAR MANUALMENTE (más rápido y controlable que .plot())
    if boxes is not None and len(boxes) > 0:
        for box in boxes:
            try:
                # Obtener coordenadas
                x1, y1, x2, y2 = map(int, box.xyxy[0])
                conf = float(box.conf[0])
                cls = int(box.cls[0])
                
                # Nombre de la clase
                class_name = model.names[cls]
                
                # 3️⃣ DIBUJAR BBOX
                # Verde si confianza es alta, Rojo si es baja
                color = (0, 255, 0) if conf > 0.6 else (0, 0, 255)
                cv2.rectangle(frame_anotado, (x1, y1), (x2, y2), color, 2)
                
                # 4️⃣ DIBUJAR ETIQUETA
                if conf > 0.6:
                    estado = "✓ PRESENTE"
                else:
                    estado = "✗ FALTA"
                
                label = f"{class_name} {conf:.2f} | {estado}"
                font = cv2.FONT_HERSHEY_SIMPLEX
                font_scale = 0.5
                thickness = 1
                
                # Fondo para la etiqueta
                text_size = cv2.getTextSize(label, font, font_scale, thickness)[0]
                cv2.rectangle(
                    frame_anotado,
                    (x1, y1 - text_size[1] - 5),
                    (x1 + text_size[0], y1),
                    color,
                    -1
                )
                cv2.putText(
                    frame_anotado,
                    label,
                    (x1, y1 - 5),
                    font,
                    font_scale,
                    (255, 255, 255),
                    thickness
                )
            except Exception as e:
                print(f"⚠ Error dibujando bbox: {e}")
                continue
    
    return frame_anotado, boxes


def obtener_camara_por_id(db: Session, id_camara: int):
    """Obtiene una cámara por su ID."""
    camara = db.query(Camara).filter(Camara.id_camara == id_camara).first()
    
    if not camara:
        raise Exception(f"Cámara con ID {id_camara} no encontrada")
    
    return camara
from ultralytics import YOLO
import cv2
import numpy as np

# Cargar modelo YOLO UNA SOLA VEZ
model = YOLO("app/modelos_yolo/best.pt")

def procesar_frame(frame):
    """Procesa un frame y devuelve detecciones + frame con bounding boxes."""
    
    # 1️⃣ OPTIMIZACIÓN: Procesar directamente en BGR
    resultados = model.predict(
        frame, 
        imgsz=416,  # ⚡ Tamaño óptimo para velocidad en CPU
        conf=0.25,  # Reducir confianza para detectar MÁS objetos
        iou=0.4,    # Reducir IOU para evitar fusionar detecciones
        verbose=False  # No imprimir logs
    )
    
    boxes = resultados[0].boxes
    
    # 2️⃣ DIBUJAR MANUALMENTE (más rápido y controlable que .plot())
    frame_anotado = frame.copy()
    
    if boxes is not None and len(boxes) > 0:
        for box in boxes:
            # Obtener coordenadas
            x1, y1, x2, y2 = map(int, box.xyxy[0])
            conf = float(box.conf[0])
            cls = int(box.cls[0])
            
            # Nombre de la clase
            class_name = model.names[cls]
            
            # 3️⃣ DIBUJAR BBOX
            # Verde si confianza es alta (equipo puesto), Rojo si es baja (equipo no puesto)
            color = (0, 255, 0) if conf > 0.6 else (0, 0, 255)  # Verde si >60%, Rojo si <60%
            cv2.rectangle(frame_anotado, (x1, y1), (x2, y2), color, 2)
            
            # 4️⃣ DIBUJAR ETIQUETA
            # Determinar estado
            if conf > 0.6:
                estado = "✓ PRESENTE"
                color_texto = (0, 255, 0)  # Verde
            else:
                estado = "✗ FALTA"
                color_texto = (0, 0, 255)  # Rojo
            
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
                (255, 255, 255),  # Texto blanco para mejor contraste
                thickness
            )
    
    return frame_anotado, boxes
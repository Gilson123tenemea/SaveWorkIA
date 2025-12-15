"""
Servicio para analizar detección de EPP en frames
Lógica robusta: PRESENCIA tiene prioridad sobre AUSENCIA
NORMALIZADO A IDS DE BD
"""

import base64
import cv2
from app.servicios.deteccion_epp import model

# =========================================
# YOLO → ID BD (ZonaEpp.tipo_epp)
# =========================================
MAPA_CLASES = {
    "helmet": ("casco", True),
    "no-helmet": ("casco", False),

    "vest": ("chaleco", True),
    "no-vest": ("chaleco", False),

    "gloves": ("guantes", True),
    "no-gloves": ("guantes", False),

    "boots": ("botas", True),
    "no-boots": ("botas", False),

    # 🔥 FIX DEFINITIVO
    "goggles": ("gafas", True),
    "no-goggles": ("gafas", False),

    "mask": ("mascarilla", True),
    "no-mask": ("mascarilla", False),

    "ear-protectors": ("protectores_auditivos", True),
    "no-ear-protectors": ("protectores_auditivos", False),
}


def analizar_frame_epp(frame):
    resultados = model.predict(
        frame,
        imgsz=416,
        conf=0.25,
        iou=0.4,
        verbose=False
    )

    boxes = resultados[0].boxes

    # ===============================
    # Inicializar detecciones
    # ===============================
    implementos = {}

    detecciones_yolo = []

    # ===============================
    # Procesar YOLO
    # ===============================
    if boxes is not None and len(boxes) > 0:
        print(f"📦 Total boxes detectados: {len(boxes)}")

        for box in boxes:
            conf = float(box.conf[0])
            cls = int(box.cls[0])
            class_name = model.names[cls].lower()

            print(f"  → {class_name}: {conf:.2f}")

            if conf < 0.40 or class_name not in MAPA_CLASES:
                continue

            implemento, es_presencia = MAPA_CLASES[class_name]

            detecciones_yolo.append({
                "class_name": class_name,
                "confidence": conf
            })

            if implemento not in implementos:
                implementos[implemento] = {
                    "detectado": False,
                    "confirmado": False,
                    "confianza": 0.0
                }

            estado = implementos[implemento]

            # 🔥 PRESENCIA MANDA
            if es_presencia:
                estado["detectado"] = True
                estado["confirmado"] = True
                estado["confianza"] = conf
            else:
                if not estado["confirmado"]:
                    estado["detectado"] = False
                    estado["confianza"] = conf

    else:
        print("⚠ No se detectaron boxes")

    # ===============================
    # Resultado
    # ===============================
    return {
        "detecciones": implementos,          # 👈 IDs BD
        "detecciones_yolo": detecciones_yolo,
        "foto_base64": frame_a_base64(frame)
    }


def frame_a_base64(frame):
    try:
        _, buffer = cv2.imencode(".jpg", frame, [cv2.IMWRITE_JPEG_QUALITY, 85])
        return base64.b64encode(buffer).decode("utf-8")
    except Exception as e:
        print(f"❌ Error base64: {e}")
        return None

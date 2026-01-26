"""
Servicio para analizar detección de EPP en frames
Lógica robusta: PRESENCIA tiene prioridad sobre AUSENCIA
NORMALIZADO A IDS DE BD
"""

import base64
import cv2
from app.servicios.deteccion_epp import model

# Importar servicio de logs
from app.servicios.log_service import LogServicio

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


async def analizar_frame_epp(frame, metadata: dict = None):
    """
    Analiza un frame para detectar EPP usando YOLO
    
    Args:
        frame: Frame de la cámara (numpy array)
        metadata: Información adicional para logs (id_camara, id_zona, etc.)
    
    Returns:
        dict con detecciones, detecciones_yolo y foto_base64
    """
    try:
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
        total_detecciones = 0
        detecciones_confirmadas = 0

        # ===============================
        # Procesar YOLO
        # ===============================
        if boxes is not None and len(boxes) > 0:
            total_detecciones = len(boxes)
            print(f"📦 Total boxes detectados: {total_detecciones}")

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
                    detecciones_confirmadas += 1
                else:
                    if not estado["confirmado"]:
                        estado["detectado"] = False
                        estado["confianza"] = conf

        else:
            print("⚠ No se detectaron boxes")

        # Convertir frame a base64
        foto_base64 = frame_a_base64(frame)

        # Log del análisis de EPP
        await LogServicio.registrar_accion_negocio(
            source="analisis_epp_servicio.analizar_frame_epp",
            accion="analisis_epp_ia",
            estado="success",
            mensaje=f"Análisis EPP completado: {detecciones_confirmadas} EPP detectados",
            metadata={
                "total_boxes_yolo": total_detecciones,
                "detecciones_confirmadas": detecciones_confirmadas,
                "implementos_detectados": list(implementos.keys()),
                "detecciones_yolo": detecciones_yolo,
                "id_camara": metadata.get("id_camara") if metadata else None,
                "id_zona": metadata.get("id_zona") if metadata else None,
                "codigo_trabajador": metadata.get("codigo_trabajador") if metadata else None
            }
        )

        # ===============================
        # Resultado
        # ===============================
        return {
            "detecciones": implementos,          # 👈 IDs BD
            "detecciones_yolo": detecciones_yolo,
            "foto_base64": foto_base64
        }
        
    except Exception as e:
        print(f"❌ Error analizando frame EPP: {e}")
        
        # Log de error
        await LogServicio.registrar_error(
            source="analisis_epp_servicio.analizar_frame_epp",
            accion="analisis_epp_ia",
            error_message=str(e),
            metadata={
                "frame_shape": frame.shape if frame is not None else None,
                "id_camara": metadata.get("id_camara") if metadata else None
            }
        )
        
        raise


def frame_a_base64(frame):
    try:
        _, buffer = cv2.imencode(".jpg", frame, [cv2.IMWRITE_JPEG_QUALITY, 85])
        return base64.b64encode(buffer).decode("utf-8")
    except Exception as e:
        print(f"❌ Error base64: {e}")
        return None
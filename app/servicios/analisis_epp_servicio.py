# app/servicios/analisis_epp_servicio.py
"""
Servicio para analizar detección de EPP en frames
Retorna: cumple_epp (bool), detecciones (dict), foto_base64 (str)
"""

import base64
import cv2
import numpy as np
from app.servicios.deteccion_epp import model

MAPA_CLASES = {
    "helmet": "casco",
    "vest": "chaleco",
    "boots": "botas",
    "gloves": "guantes",
    "glasses": "lentes"
}


def analizar_frame_epp(frame):
    """
    Analiza un frame con YOLO y retorna análisis completo de EPP
    
    Args:
        frame: imagen numpy (BGR)
    
    Returns:
        dict con:
        - cumple_epp: bool (True si tiene TODOS los implementos)
        - detecciones: dict con estado de cada implemento
        - foto_base64: frame convertido a base64
        - detalle_fallo: string describiendo qué falta
        - frame_procesado: frame con bounding boxes dibujados
    """
    
    # 1️⃣ PREDECIR CON YOLO
    resultados = model.predict(
        frame,
        imgsz=416,
        conf=0.25,
        iou=0.4,
        verbose=False
    )
    
    boxes = resultados[0].boxes
    
    # 2️⃣ INICIALIZAR DETECCIONES (implementos requeridos)
    # Los implementos OBLIGATORIOS para cumplir EPP
    implementos_detectados = {
        'casco': {'detectado': False, 'confianza': 0.0},
        'chaleco': {'detectado': False, 'confianza': 0.0},
        'guantes': {'detectado': False, 'confianza': 0.0},
        'botas': {'detectado': False, 'confianza': 0.0},
        'lentes': {'detectado': False, 'confianza': 0.0}  # Opcional pero registramos
    }
    
    
    # 3️⃣ PROCESAR DETECCIONES
    if boxes is not None and len(boxes) > 0:
        print(f"📦 Total boxes detectados: {len(boxes)}")
        for box in boxes:
            try:
                conf = float(box.conf[0])
                cls = int(box.cls[0])
                class_name = model.names[cls].lower()
                
                print(f"  → {class_name}: {conf:.2f}")  # 🔥 DEBUG
                
                if class_name in MAPA_CLASES:
                    nombre_interno = MAPA_CLASES[class_name]
                else:
                    print(f"⚠ Clase YOLO no reconocida: {class_name}")
                    continue

                if nombre_interno in implementos_detectados:
                    if conf > 0.40:
                     implementos_detectados[nombre_interno]['detectado'] = True
                     implementos_detectados[nombre_interno]['confianza'] = conf
            except Exception as e:
                print(f"⚠ Error procesando box: {e}")
                continue
    else:
        print("⚠ No se detectaron boxes")
    
    # 4️⃣ EVALUAR CUMPLIMIENTO DE EPP
    # Implementos OBLIGATORIOS (todos deben estar presentes)
    implementos_obligatorios = ['casco', 'chaleco', 'guantes', 'botas']
    
    cumple_epp = all(
        implementos_detectados[imp]['detectado'] 
        for imp in implementos_obligatorios
    )
    
    # 5️⃣ GENERAR DETALLE DE FALLO
    detalle_fallo = _generar_detalle_fallo(implementos_detectados, cumple_epp)
    
    # 6️⃣ PROCESAR FRAME PARA MOSTRAR EN FRONT
    frame_procesado = _dibujar_detecciones(frame, implementos_detectados)
    
    # 7️⃣ CONVERTIR FRAME A BASE64 (para guardar como foto)
    foto_base64 = _frame_a_base64(frame)
    
    return {
        'cumple_epp': cumple_epp,
        'detecciones': implementos_detectados,
        'foto_base64': foto_base64,
        'detalle_fallo': detalle_fallo,
        'frame_procesado': frame_procesado
    }


def _generar_detalle_fallo(implementos, cumple_epp):
    """
    Genera string descriptivo del estado de EPP
    """
    if cumple_epp:
        return "✅ Trabajador cumple con todos los implementos de seguridad"
    
    # Encontrar qué falta
    faltantes = []
    for imp, estado in implementos.items():
        # Solo verificar obligatorios
        if imp in ['casco', 'chaleco', 'guantes', 'botas']:
            if not estado['detectado']:
                faltantes.append(imp.upper())
    
    if faltantes:
        return f"❌ INCUMPLIMIENTO EPP: Falta(n) {', '.join(faltantes)}"
    
    return "⚠ Error en análisis"


def _dibujar_detecciones(frame, implementos):
    """
    Dibuja resumen visual de detecciones en el frame
    Retorna frame con overlay de información
    """
    frame_display = frame.copy()
    altura, ancho = frame.shape[:2]
    
    # Coordenadas y tamaño del panel informativo
    panel_y = 30
    panel_x = 10
    font = cv2.FONT_HERSHEY_SIMPLEX
    font_scale = 0.6
    thickness = 2
    line_height = 30
    
    # Color de fondo (semi-transparente)
    overlay = frame_display.copy()
    cv2.rectangle(
        overlay,
        (panel_x, 10),
        (panel_x + 350, panel_y + (len(implementos) * line_height) + 20),
        (0, 0, 0),
        -1
    )
    frame_display = cv2.addWeighted(overlay, 0.7, frame_display, 0.3, 0)
    
    # Dibujar cada implemento
    y_offset = panel_y
    for imp, estado in implementos.items():
        detectado = estado['detectado']
        confianza = estado['confianza']
        
        # Color según si está detectado
        color = (0, 255, 0) if detectado else (0, 0, 255)
        
        # Estado visual
        estado_str = f"✓ {imp.upper()}" if detectado else f"✗ {imp.upper()}"
        
        # Dibujar texto
        cv2.putText(
            frame_display,
            estado_str,
            (panel_x + 15, y_offset),
            font,
            font_scale,
            color,
            thickness
        )
        
        # Dibujar confianza si está detectado
        if detectado:
            conf_text = f"{confianza:.2f}"
            cv2.putText(
                frame_display,
                conf_text,
                (panel_x + 250, y_offset),
                font,
                0.5,
                (255, 255, 0),
                1
            )
        
        y_offset += line_height
    
    return frame_display


def _frame_a_base64(frame):
    """
    Convierte un frame numpy a string base64
    Para guardar como foto en la BD
    """
    try:
        _, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 85])
        # 🔥 FIX: buffer ya es bytes, no necesita .tobytes()
        foto_base64 = base64.b64encode(buffer).decode('utf-8')
        return foto_base64
    except Exception as e:
        print(f"❌ Error convirtiendo frame a base64: {e}")
        return None


def base64_a_foto(base64_str, ruta_salida):
    """
    Convierte base64 a archivo JPG en disco
    
    Args:
        base64_str: string en base64
        ruta_salida: ruta completa del archivo (ej: "fotos/foto_1.jpg")
    
    Returns:
        bool: True si se guardó exitosamente
    """
    try:
        # Decodificar base64
        img_data = base64.b64decode(base64_str)
        
        # Escribir en archivo
        with open(ruta_salida, 'wb') as f:
            f.write(img_data)
        
        print(f"✅ Foto guardada en: {ruta_salida}")
        return True
    except Exception as e:
        print(f"❌ Error guardando foto: {e}")
        return False
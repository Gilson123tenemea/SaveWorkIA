# app/servicios/camara_buffer_servicio.py
"""
Servicio para guardar y recuperar últimos frames de cada cámara
Necesario para capturar foto cuando se verifica EPP
"""

import numpy as np
from typing import Optional

# Diccionario global para guardar último frame de cada cámara
# {id_camara: frame_numpy}
buffer_frames = {}

# Información adicional sobre cada cámara
info_camaras = {}


def actualizar_buffer_frame(id_camara: int, frame: np.ndarray) -> None:
    """
    Actualiza el último frame capturado de una cámara
    Se llama en cada iteración del stream
    
    Args:
        id_camara: ID de la cámara
        frame: imagen numpy (BGR)
    """
    try:
        if frame is not None and frame.size > 0:
            # Guardar copia del frame (no referencia)
            buffer_frames[id_camara] = frame.copy()
    except Exception as e:
        print(f"⚠ Error actualizando buffer frame {id_camara}: {e}")


def obtener_ultimo_frame_camara(id_camara: int) -> Optional[np.ndarray]:
    """
    Obtiene el último frame capturado de una cámara
    Se usa cuando se verifica EPP
    
    Args:
        id_camara: ID de la cámara
    
    Returns:
        Frame numpy (BGR) o None si no existe
    """
    frame = buffer_frames.get(id_camara, None)
    
    if frame is None:
        print(f"⚠ No hay frame disponible para cámara {id_camara}")
        return None
    
    # Retornar copia para evitar modificaciones externas
    return frame.copy()


def limpiar_buffer_camara(id_camara: int) -> bool:
    """
    Limpia el buffer de una cámara (cuando se detiene stream)
    
    Args:
        id_camara: ID de la cámara
    
    Returns:
        bool: True si se limpió exitosamente
    """
    try:
        if id_camara in buffer_frames:
            del buffer_frames[id_camara]
            print(f"✅ Buffer de cámara {id_camara} limpiado")
            return True
        return False
    except Exception as e:
        print(f"❌ Error limpiando buffer {id_camara}: {e}")
        return False


def limpiar_todos_buffers() -> None:
    """Limpia todos los buffers (usar al apagar servidor)"""
    buffer_frames.clear()
    info_camaras.clear()
    print("✅ Todos los buffers limpios")


def obtener_estado_buffers() -> dict:
    """
    Retorna info de qué cámaras tienen frames en buffer
    Útil para debugging
    
    Returns:
        dict con estado de buffers
    """
    camaras_activas = []
    
    for id_cam, frame in buffer_frames.items():
        if frame is not None:
            camaras_activas.append({
                'id_camara': id_cam,
                'tamaño_frame': frame.shape,
                'bytes': frame.nbytes
            })
    
    return {
        'total_camaras': len(camaras_activas),
        'camaras': camaras_activas
    }
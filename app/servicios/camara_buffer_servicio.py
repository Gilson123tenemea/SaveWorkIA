# app/servicios/camara_buffer_servicio.py
"""
Servicio para guardar y recuperar últimos frames de cada cámara
Necesario para capturar foto cuando se verifica EPP
"""

import numpy as np
from typing import Optional

# Importar servicio de logs
from app.servicios.log_service import LogServicio

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


async def obtener_ultimo_frame_camara(id_camara: int, log_metadata: dict = None) -> Optional[np.ndarray]:
    """
    Obtiene el último frame capturado de una cámara
    Se usa cuando se verifica EPP
    
    Args:
        id_camara: ID de la cámara
        log_metadata: Metadata adicional para el log
    
    Returns:
        Frame numpy (BGR) o None si no existe
    """
    try:
        frame = buffer_frames.get(id_camara, None)
        
        if frame is None:
            print(f"⚠ No hay frame disponible para cámara {id_camara}")
            
            # Log de advertencia cuando no hay frame
            await LogServicio.registrar_accion_negocio(
                source="camara_buffer_servicio.obtener_ultimo_frame_camara",
                accion="obtener_frame_buffer",
                estado="failed",
                mensaje=f"No hay frame disponible en buffer para cámara {id_camara}",
                metadata={
                    "id_camara": id_camara,
                    "camaras_en_buffer": list(buffer_frames.keys()),
                    **(log_metadata or {})
                }
            )
            
            return None
        
        # Log exitoso (solo en casos importantes, no en cada frame)
        if log_metadata and log_metadata.get("log_success", False):
            await LogServicio.registrar_accion_negocio(
                source="camara_buffer_servicio.obtener_ultimo_frame_camara",
                accion="obtener_frame_buffer",
                estado="success",
                mensaje=f"Frame obtenido del buffer para verificación EPP",
                metadata={
                    "id_camara": id_camara,
                    "frame_shape": frame.shape,
                    "frame_size_bytes": frame.nbytes,
                    **(log_metadata or {})
                }
            )
        
        # Retornar copia para evitar modificaciones externas
        return frame.copy()
        
    except Exception as e:
        print(f"❌ Error obteniendo frame de buffer {id_camara}: {e}")
        
        # Log de error
        await LogServicio.registrar_error(
            source="camara_buffer_servicio.obtener_ultimo_frame_camara",
            accion="obtener_frame_buffer",
            error_message=str(e),
            metadata={
                "id_camara": id_camara,
                **(log_metadata or {})
            }
        )
        
        return None


async def limpiar_buffer_camara(id_camara: int) -> bool:
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
            
            # Log de limpieza de buffer
            await LogServicio.registrar_accion_negocio(
                source="camara_buffer_servicio.limpiar_buffer_camara",
                accion="limpiar_buffer_camara",
                estado="success",
                mensaje=f"Buffer de cámara {id_camara} limpiado",
                metadata={
                    "id_camara": id_camara,
                    "camaras_restantes": list(buffer_frames.keys())
                }
            )
            
            return True
            
        return False
        
    except Exception as e:
        print(f"❌ Error limpiando buffer {id_camara}: {e}")
        
        # Log de error
        await LogServicio.registrar_error(
            source="camara_buffer_servicio.limpiar_buffer_camara",
            accion="limpiar_buffer_camara",
            error_message=str(e),
            metadata={"id_camara": id_camara}
        )
        
        return False


async def limpiar_todos_buffers() -> None:
    """Limpia todos los buffers (usar al apagar servidor)"""
    try:
        cantidad_buffers = len(buffer_frames)
        camaras_limpiadas = list(buffer_frames.keys())
        
        buffer_frames.clear()
        info_camaras.clear()
        
        print("✅ Todos los buffers limpios")
        
        # Log de limpieza total
        await LogServicio.registrar_accion_negocio(
            source="camara_buffer_servicio.limpiar_todos_buffers",
            accion="limpiar_todos_buffers",
            estado="success",
            mensaje=f"Todos los buffers limpiados: {cantidad_buffers} cámaras",
            metadata={
                "cantidad_buffers": cantidad_buffers,
                "camaras_limpiadas": camaras_limpiadas
            }
        )
        
    except Exception as e:
        print(f"❌ Error limpiando todos los buffers: {e}")
        
        # Log de error
        await LogServicio.registrar_error(
            source="camara_buffer_servicio.limpiar_todos_buffers",
            accion="limpiar_todos_buffers",
            error_message=str(e)
        )


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
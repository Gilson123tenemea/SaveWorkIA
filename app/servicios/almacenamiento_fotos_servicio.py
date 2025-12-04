# app/servicios/almacenamiento_fotos_servicio.py
"""
Servicio para guardar fotos de fallos de EPP
Soporta almacenamiento local en disco
Puede extenderse para AWS S3, Azure Blob, etc.
"""

import os
import base64
from datetime import datetime
from pathlib import Path
from typing import Optional

# Configuración de rutas
CARPETA_FOTOS = "almacenamiento/evidencias"
CARPETA_FOTOS_TEMPORAL = "almacenamiento/temporal"

# Crear carpetas si no existen
Path(CARPETA_FOTOS).mkdir(parents=True, exist_ok=True)
Path(CARPETA_FOTOS_TEMPORAL).mkdir(parents=True, exist_ok=True)


def generar_nombre_archivo(id_trabajador: int, id_registro: int) -> str:
    """
    Genera nombre único para archivo de foto
    Formato: TRABAJADOR_{id}_REGISTRO_{id}_{timestamp}.jpg
    
    Args:
        id_trabajador: ID del trabajador
        id_registro: ID del registro de asistencia
    
    Returns:
        string con nombre del archivo
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    nombre = f"TRABAJADOR_{id_trabajador}_REGISTRO_{id_registro}_{timestamp}.jpg"
    return nombre


def guardar_foto_desde_base64(
    base64_str: str,
    id_trabajador: int,
    id_registro: int,
    usar_temporal: bool = False
) -> Optional[str]:
    """
    Guarda foto desde string base64 a disco
    
    Args:
        base64_str: imagen en base64
        id_trabajador: ID del trabajador
        id_registro: ID del registro
        usar_temporal: si True, guarda en carpeta temporal (para debugging)
    
    Returns:
        string con ruta relativa o None si falla
    """
    try:
        if not base64_str:
            print("❌ Base64 vacío")
            return None
        
        # Seleccionar carpeta
        carpeta = CARPETA_FOTOS_TEMPORAL if usar_temporal else CARPETA_FOTOS
        
        # Generar nombre de archivo
        nombre_archivo = generar_nombre_archivo(id_trabajador, id_registro)
        ruta_completa = os.path.join(carpeta, nombre_archivo)
        
        # Decodificar base64
        img_data = base64.b64decode(base64_str)
        
        # Guardar archivo
        with open(ruta_completa, 'wb') as f:
            f.write(img_data)
        
        print(f"✅ Foto guardada: {ruta_completa}")
        
        # Retornar ruta relativa (para guardar en BD)
        ruta_relativa = os.path.join(carpeta, nombre_archivo).replace("\\", "/")
        return ruta_relativa
    
    except Exception as e:
        print(f"❌ Error guardando foto: {e}")
        return None


def guardar_foto_desde_archivo(
    ruta_origen: str,
    id_trabajador: int,
    id_registro: int
) -> Optional[str]:
    """
    Copia foto desde ruta origen a carpeta de almacenamiento
    
    Args:
        ruta_origen: ruta completa del archivo original
        id_trabajador: ID del trabajador
        id_registro: ID del registro
    
    Returns:
        string con ruta relativa o None si falla
    """
    try:
        if not os.path.exists(ruta_origen):
            print(f"❌ Archivo no existe: {ruta_origen}")
            return None
        
        # Generar nombre y ruta destino
        nombre_archivo = generar_nombre_archivo(id_trabajador, id_registro)
        ruta_destino = os.path.join(CARPETA_FOTOS, nombre_archivo)
        
        # Copiar archivo
        with open(ruta_origen, 'rb') as f_origen:
            contenido = f_origen.read()
        
        with open(ruta_destino, 'wb') as f_destino:
            f_destino.write(contenido)
        
        print(f"✅ Foto copiada: {ruta_destino}")
        
        # Retornar ruta relativa
        ruta_relativa = os.path.join(CARPETA_FOTOS, nombre_archivo).replace("\\", "/")
        return ruta_relativa
    
    except Exception as e:
        print(f"❌ Error copiando foto: {e}")
        return None


def obtener_ruta_foto(foto_url: str) -> str:
    """
    Retorna ruta completa de foto a partir de ruta relativa
    Útil para acceder a fotos almacenadas
    
    Args:
        foto_url: ruta relativa guardada en BD
    
    Returns:
        ruta completa del archivo
    """
    return os.path.abspath(foto_url)


def obtener_foto_como_base64(foto_url: str) -> Optional[str]:
    """
    Lee foto del disco y la convierte a base64
    Útil para enviar al frontend
    
    Args:
        foto_url: ruta relativa guardada en BD
    
    Returns:
        string base64 o None si falla
    """
    try:
        ruta_completa = obtener_ruta_foto(foto_url)
        
        if not os.path.exists(ruta_completa):
            print(f"❌ Foto no existe: {ruta_completa}")
            return None
        
        with open(ruta_completa, 'rb') as f:
            contenido = f.read()
        
        base64_str = base64.b64encode(contenido).decode('utf-8')
        return base64_str
    
    except Exception as e:
        print(f"❌ Error leyendo foto: {e}")
        return None


def eliminar_foto(foto_url: str) -> bool:
    """
    Elimina foto del disco (borrado físico)
    
    Args:
        foto_url: ruta relativa guardada en BD
    
    Returns:
        bool: True si se eliminó
    """
    try:
        ruta_completa = obtener_ruta_foto(foto_url)
        
        if os.path.exists(ruta_completa):
            os.remove(ruta_completa)
            print(f"✅ Foto eliminada: {ruta_completa}")
            return True
        else:
            print(f"⚠ Foto no existe: {ruta_completa}")
            return False
    
    except Exception as e:
        print(f"❌ Error eliminando foto: {e}")
        return False


def obtener_espacio_usado() -> dict:
    """
    Calcula espacio usado por fotos almacenadas
    Útil para monitoreo
    
    Returns:
        dict con información de uso
    """
    try:
        total_bytes = 0
        total_archivos = 0
        
        for root, dirs, files in os.walk(CARPETA_FOTOS):
            for archivo in files:
                ruta_archivo = os.path.join(root, archivo)
                total_bytes += os.path.getsize(ruta_archivo)
                total_archivos += 1
        
        # Convertir a MB
        total_mb = total_bytes / (1024 * 1024)
        
        return {
            'total_archivos': total_archivos,
            'total_bytes': total_bytes,
            'total_mb': round(total_mb, 2),
            'carpeta': CARPETA_FOTOS
        }
    
    except Exception as e:
        print(f"❌ Error calculando espacio: {e}")
        return {}
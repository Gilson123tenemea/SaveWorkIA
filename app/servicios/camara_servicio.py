# app/servicios/camara_servicio.py
from sqlalchemy.orm import Session, joinedload
from fastapi import HTTPException, status
from datetime import date

from app.modelos.camara_modelo import Camara
from app.modelos.zona_modelo import Zona
from app.modelos.empresa_modelo import Empresa  # IMPORTANTE
from app.esquemas.camara_esquema import CamaraCreate, CamaraUpdate

from app.Validaciones.camara_validaciones import (
    validar_codigo_camara, validar_ip,
    validar_tipo_camara, validar_estado_camara,
)

import requests
import cv2
import numpy as np

# ============================================================
# 🔹 REGLA DE NEGOCIO DE DUPLICADOS
# ============================================================
def validar_unicidad_camara(db: Session, camara: CamaraCreate):

    zona = db.query(Zona).filter(
        Zona.id_Zona == camara.id_zona,
        Zona.borrado == True
    ).first()

    if not zona:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="La zona seleccionada no existe o está inactiva"
        )

    empresa_id = zona.id_empresa_zona

    zonas_empresa = db.query(Zona.id_Zona).filter(
        Zona.id_empresa_zona == empresa_id
    ).subquery()

    # -------------------------
    # 🔍 VALIDAR CÓDIGO (esto sí se mantiene)
    # -------------------------
    codigo_dup = db.query(Camara).filter(
        Camara.codigo == camara.codigo,
        Camara.id_zona.in_(zonas_empresa),
        Camara.borrado == True
    ).first()

    if codigo_dup:
        raise HTTPException(
            status_code=400,
            detail="Ya existe una cámara activa con ese código en esta empresa"
        )

    # ❌ VALIDACIÓN DE IP ELIMINADA

# ============================================================
# 🔹 CREAR CÁMARA
# ============================================================
def crear_camara(db: Session, camara: CamaraCreate):

    validar_codigo_camara(camara.codigo)
    validar_ip(camara.ipAddress)
    validar_tipo_camara(camara.tipo)
    validar_estado_camara(camara.estado)

    validar_unicidad_camara(db, camara)

    nueva = Camara(**camara.model_dump())
    nueva.borrado = True

    db.add(nueva)
    db.commit()
    db.refresh(nueva)
    return nueva


# ============================================================
# 🔹 LISTAR
# ============================================================
def obtener_camaras(db: Session, skip=0, limit=100):
    return (
        db.query(Camara)
        .options(joinedload(Camara.zona).joinedload(Zona.empresa))
        .filter(Camara.borrado == True)
        .offset(skip)
        .limit(limit)
        .all()
    )


def obtener_camaras_por_zona(db: Session, zona_id: int, skip=0, limit=100):
    return (
        db.query(Camara)
        .filter(Camara.id_zona == zona_id, Camara.borrado == True)
        .offset(skip)
        .limit(limit)
        .all()
    )


def obtener_camaras_por_administrador(db: Session, administrador_id: int, skip=0, limit=100):
    return (
        db.query(Camara)
        .filter(Camara.id_administrador == administrador_id, Camara.borrado == True)
        .offset(skip)
        .limit(limit)
        .all()
    )


# ============================================================
# 🔹 OBTENER UNA CÁMARA
# ============================================================
def obtener_camara_por_id(db: Session, camara_id: int):
    cam = db.query(Camara).filter(Camara.id_camara == camara_id).first()
    if not cam:
        raise HTTPException(404, "Cámara no encontrada")
    return cam


# ============================================================
# 🔹 ACTUALIZAR SOLO ESTADO
# ============================================================
def actualizar_camara(db: Session, camara_id: int, camara_update: CamaraUpdate):
    cam = obtener_camara_por_id(db, camara_id)

    data = camara_update.model_dump(exclude_unset=True)

    if set(data.keys()) != {"estado"}:
        raise HTTPException(
            status_code=400,
            detail="Solo se permite actualizar el estado de la cámara"
        )

    validar_estado_camara(data["estado"])

    cam.estado = data["estado"]
    db.commit()
    db.refresh(cam)
    return cam


# ============================================================
# 🔹 ELIMINAR
# ============================================================
def eliminar_camara(db: Session, camara_id: int):
    cam = obtener_camara_por_id(db, camara_id)
    cam.borrado = False
    db.commit()
    return {"message": "Cámara eliminada correctamente"}


def eliminar_camara_permanente(db: Session, camara_id: int):
    cam = obtener_camara_por_id(db, camara_id)
    db.delete(cam)
    db.commit()
    return {"message": "Cámara eliminada permanentemente"}

def probar_conexion_camara(url: str):
    """
    Intenta conectarse a la cámara y obtiene 1 frame.
    Si funciona, devuelve True.
    """
    try:
        # Para IP Webcam:
        test_url = (
            url if "shot.jpg" in url 
            else url.replace("video", "shot.jpg")
        )

        resp = requests.get(test_url, timeout=3)

        if resp.status_code != 200:
            return False, "La cámara no respondió correctamente"

        # Validar que sea una imagen válida
        img_np = np.frombuffer(resp.content, np.uint8)
        frame = cv2.imdecode(img_np, cv2.IMREAD_COLOR)

        if frame is None:
            return False, "No se pudo decodificar imagen"

        return True, "Conexión exitosa"

    except Exception as e:
        return False, str(e)
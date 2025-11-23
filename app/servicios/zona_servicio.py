from sqlalchemy.orm import Session
from app.modelos.zona_modelo import Zona
from app.esquemas.zona_esquema import ZonaCreate, ZonaUpdate
from fastapi import HTTPException, status
from app.modelos.camara_modelo import Camara
from app.modelos.trabajador_zona import TrabajadorZona
from sqlalchemy import func

# 🔹 Validaciones
from app.Validaciones.zona_validaciones import (
    validar_nombre_zona,
    validar_coordenada
)


# ============================================================
# 🔹 CREAR ZONA
# ============================================================
def crear_zona(db: Session, zona: ZonaCreate):

    validar_nombre_zona(zona.nombreZona)
    validar_coordenada(zona.latitud, "latitud")
    validar_coordenada(zona.longitud, "longitud")

    zona_existente = db.query(Zona).filter(
        Zona.nombreZona == zona.nombreZona,
        Zona.id_empresa_zona == zona.id_empresa_zona
    ).first()

    if zona_existente and zona_existente.borrado is True:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ya existe una zona activa con ese nombre en esta empresa"
        )

    nueva_zona = Zona(**zona.dict())
    nueva_zona.borrado = True

    db.add(nueva_zona)
    db.commit()
    db.refresh(nueva_zona)

    return nueva_zona


# ============================================================
# 🔹 LISTAR TODAS LAS ZONAS
# ============================================================
def obtener_zonas(db: Session, skip: int = 0, limit: int = 100):
    return (
        db.query(Zona)
        .filter(Zona.borrado == True)
        .offset(skip)
        .limit(limit)
        .all()
    )


# ============================================================
# 🔹 LISTAR ZONAS POR EMPRESA
# ============================================================
def obtener_zonas_por_empresa_con_detalles(db: Session, empresa_id: int):
    zonas = db.query(Zona).filter(
        Zona.id_empresa_zona == empresa_id,
        Zona.borrado == True
    ).all()

    respuesta = []

    for zona in zonas:
        total_camaras = db.query(func.count(Camara.id_camara)).filter(
            Camara.id_zona == zona.id_Zona,
            Camara.borrado == True
        ).scalar()

        total_trabajadores = db.query(func.count(TrabajadorZona.id_trabajador_zona)).filter(
            TrabajadorZona.id_zona_trabajadorzona == zona.id_Zona,
            TrabajadorZona.borrado == True
        ).scalar()

        respuesta.append({
            "id_Zona": zona.id_Zona,
            "nombreZona": zona.nombreZona,
            "latitud": zona.latitud,
            "longitud": zona.longitud,
            "id_empresa_zona": zona.id_empresa_zona,
            "id_administrador_zona": zona.id_administrador_zona,  # 🔥 AÑADIDO
            "total_camaras": total_camaras,
            "total_trabajadores": total_trabajadores
        })

    return respuesta


# ============================================================
# 🔹 LISTAR POR ADMINISTRADOR
# ============================================================
def obtener_zonas_por_administrador(db: Session, administrador_id: int, skip: int = 0, limit: int = 100):
    return (
        db.query(Zona)
        .filter(Zona.id_administrador_zona == administrador_id, Zona.borrado == True)
        .offset(skip)
        .limit(limit)
        .all()
    )


# ============================================================
# 🔹 OBTENER POR ID
# ============================================================
def obtener_zona_por_id(db: Session, zona_id: int):
    zona = db.query(Zona).filter(Zona.id_Zona == zona_id).first()
    if not zona:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Zona no encontrada"
        )
    return zona


# ============================================================
# 🔹 ACTUALIZAR ZONA (CORREGIDO COMPLETO)
# ============================================================
def actualizar_zona(db: Session, zona_id: int, zona_update: ZonaUpdate):

    zona = obtener_zona_por_id(db, zona_id)

    # Validaciones
    if zona_update.nombreZona is not None:
        validar_nombre_zona(zona_update.nombreZona)

    if zona_update.latitud is not None:
        validar_coordenada(zona_update.latitud, "latitud")

    if zona_update.longitud is not None:
        validar_coordenada(zona_update.longitud, "longitud")

    # Actualizar campos
    for campo, valor in zona_update.dict(exclude_unset=True).items():
        setattr(zona, campo, valor)

    db.commit()
    db.refresh(zona)

    # 🔥 RECONSTRUIR RESPUESTA COMPLETA COMO EXIGE ZonaResponse
    total_camaras = db.query(func.count(Camara.id_camara)).filter(
        Camara.id_zona == zona.id_Zona,
        Camara.borrado == True
    ).scalar()

    total_trabajadores = db.query(func.count(TrabajadorZona.id_trabajador_zona)).filter(
        TrabajadorZona.id_zona_trabajadorzona == zona.id_Zona,
        TrabajadorZona.borrado == True
    ).scalar()

    return {
        "id_Zona": zona.id_Zona,
        "nombreZona": zona.nombreZona,
        "latitud": zona.latitud,
        "longitud": zona.longitud,
        "id_empresa_zona": zona.id_empresa_zona,
        "id_administrador_zona": zona.id_administrador_zona,  # 🔥 OBLIGATORIO
        "borrado": zona.borrado,
        "total_camaras": total_camaras,
        "total_trabajadores": total_trabajadores
    }


# ============================================================
# 🔹 ELIMINAR LÓGICO
# ============================================================
def eliminar_zona(db: Session, zona_id: int):

    zona = obtener_zona_por_id(db, zona_id)

    total_camaras = db.query(func.count(Camara.id_camara)).filter(
        Camara.id_zona == zona_id,
        Camara.borrado == True
    ).scalar()

    if total_camaras > 0:
        raise HTTPException(
            status_code=400,
            detail="No se puede eliminar esta zona porque tiene cámaras registradas."
        )

    zona.borrado = False
    db.commit()

    return {"message": "Zona eliminada correctamente"}


# ============================================================
# 🔹 ELIMINAR FÍSICO
# ============================================================
def eliminar_zona_permanente(db: Session, zona_id: int):
    zona = obtener_zona_por_id(db, zona_id)
    db.delete(zona)
    db.commit()
    return {"message": "Zona eliminada permanentemente"}

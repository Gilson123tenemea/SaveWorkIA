from sqlalchemy.orm import Session
from sqlalchemy import func
from fastapi import HTTPException, status

from app.modelos.zona_modelo import Zona
from app.modelos.camara_modelo import Camara
from app.modelos.trabajador_zona import TrabajadorZona

from app.esquemas.zona_esquema import ZonaCreate, ZonaUpdate

# 🔹 Validaciones
from app.Validaciones.zona_validaciones import (
    validar_nombre_zona,
    validar_coordenada
)

# ============================================================
# 🔹 VALIDAR NOMBRE ÚNICO POR EMPRESA
# ============================================================
def validar_nombre_unico_por_empresa(db: Session, nombre: str, empresa_id: int, zona_id: int = None):

    query = db.query(Zona).filter(
        Zona.nombreZona == nombre,
        Zona.id_empresa_zona == empresa_id,
        Zona.borrado == True
    )

    # Evitar conflicto al editar
    if zona_id:
        query = query.filter(Zona.id_Zona != zona_id)

    existe = query.first()

    if existe:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ya existe una zona con ese nombre en esta empresa."
        )


# ============================================================
# 🔹 CREAR ZONA
# ============================================================
def crear_zona(db: Session, zona: ZonaCreate):

    validar_nombre_zona(zona.nombreZona)
    validar_coordenada(zona.latitud, "latitud")
    validar_coordenada(zona.longitud, "longitud")

    # 🛑 Validación de nombre único
    validar_nombre_unico_por_empresa(db, zona.nombreZona, zona.id_empresa_zona)

    nueva_zona = Zona(**zona.dict())
    nueva_zona.borrado = True  # Activo

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
# 🔹 LISTAR ZONAS POR EMPRESA (CON DETALLES COMPLETOS)
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
            "id_administrador_zona": zona.id_administrador_zona,
            "total_camaras": total_camaras,
            "total_trabajadores": total_trabajadores,
            "borrado": zona.borrado
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
# 🔹 ACTUALIZAR ZONA
# ============================================================
def actualizar_zona(db: Session, zona_id: int, zona_update: ZonaUpdate):

    zona = obtener_zona_por_id(db, zona_id)

    # Validaciones
    if zona_update.nombreZona is not None:
        validar_nombre_zona(zona_update.nombreZona)
        validar_nombre_unico_por_empresa(
            db,
            zona_update.nombreZona,
            zona.id_empresa_zona,
            zona_id
        )

    if zona_update.latitud is not None:
        validar_coordenada(zona_update.latitud, "latitud")

    if zona_update.longitud is not None:
        validar_coordenada(zona_update.longitud, "longitud")

    # Actualizar campos válidos
    for campo, valor in zona_update.dict(exclude_unset=True).items():
        setattr(zona, campo, valor)

    db.commit()
    db.refresh(zona)

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
        "id_administrador_zona": zona.id_administrador_zona,
        "borrado": zona.borrado,
        "total_camaras": total_camaras,
        "total_trabajadores": total_trabajadores
    }


# ============================================================
# 🔹 VALIDAR RELACIONES ANTES DE ELIMINAR
# ============================================================
def validar_relaciones_zona(db: Session, zona_id: int):

    if db.query(Camara).filter(Camara.id_zona == zona_id, Camara.borrado == True).first():
        raise HTTPException(
            status_code=400,
            detail="No se puede eliminar esta zona porque tiene cámaras registradas."
        )

    if db.query(TrabajadorZona).filter(
        TrabajadorZona.id_zona_trabajadorzona == zona_id,
        TrabajadorZona.borrado == True
    ).first():
        raise HTTPException(
            status_code=400,
            detail="No se puede eliminar esta zona porque tiene trabajadores asignados."
        )


# ============================================================
# 🔹 ELIMINAR LÓGICO
# ============================================================
def eliminar_zona(db: Session, zona_id: int):

    obtener_zona_por_id(db, zona_id)  # Validar existencia
    validar_relaciones_zona(db, zona_id)

    zona = obtener_zona_por_id(db, zona_id)
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

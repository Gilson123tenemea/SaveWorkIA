from sqlalchemy.orm import Session
from app.modelos.zona_modelo import Zona
from app.esquemas.zona_esquema import ZonaCreate, ZonaUpdate
from fastapi import HTTPException, status
from app.modelos.camara_modelo import Camara
from app.modelos.trabajador_zona import TrabajadorZona
from sqlalchemy import func

# 🔹 Importar las validaciones nuevas
from app.Validaciones.zona_validaciones import (
    validar_nombre_zona,
    validar_coordenada
)


def crear_zona(db: Session, zona: ZonaCreate):
    """
    Crea una nueva zona en la base de datos.
    Solo prohíbe crear si existe una zona activa (borrado=True).
    Si existe una zona con el mismo nombre pero borrada (False), sí se permite crear.
    """

    # ============================
    # 🔍 VALIDACIONES NUEVAS
    # ============================
    validar_nombre_zona(zona.nombreZona)
    validar_coordenada(zona.latitud, "latitud")
    validar_coordenada(zona.longitud, "longitud")

    zona_existente = db.query(Zona).filter(
        Zona.nombreZona == zona.nombreZona,
        Zona.id_empresa_zona == zona.id_empresa_zona
    ).first()

    # ❌ Ya existe una zona activa → NO permitir
    if zona_existente and zona_existente.borrado is True:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ya existe una zona activa con ese nombre en esta empresa"
        )

    nueva_zona = Zona(**zona.dict())
    nueva_zona.borrado = True  # siempre crear activa

    db.add(nueva_zona)
    db.commit()
    db.refresh(nueva_zona)

    return nueva_zona



def obtener_zonas(db: Session, skip: int = 0, limit: int = 100):
    """
    Obtiene todas las zonas activas (borrado=True)
    """
    return (
        db.query(Zona)
        .filter(Zona.borrado == True)
        .offset(skip)
        .limit(limit)
        .all()
    )



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

            "total_camaras": total_camaras,
            "total_trabajadores": total_trabajadores
        })

    return respuesta



def obtener_zonas_por_administrador(db: Session, administrador_id: int, skip: int = 0, limit: int = 100):
    return (
        db.query(Zona)
        .filter(Zona.id_administrador_zona == administrador_id, Zona.borrado == True)
        .offset(skip)
        .limit(limit)
        .all()
    )



def obtener_zona_por_id(db: Session, zona_id: int):
    zona = db.query(Zona).filter(Zona.id_Zona == zona_id).first()
    if not zona:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Zona no encontrada"
        )
    return zona



def actualizar_zona(db: Session, zona_id: int, zona_update: ZonaUpdate):
    zona = obtener_zona_por_id(db, zona_id)

    # ============================
    # 🔍 VALIDACIONES NUEVAS EN UPDATE (solo si vienen)
    # ============================
    if zona_update.nombreZona is not None:
        validar_nombre_zona(zona_update.nombreZona)

    if zona_update.latitud is not None:
        validar_coordenada(zona_update.latitud, "latitud")

    if zona_update.longitud is not None:
        validar_coordenada(zona_update.longitud, "longitud")

    for campo, valor in zona_update.dict(exclude_unset=True).items():
        setattr(zona, campo, valor)

    db.commit()
    db.refresh(zona)
    return zona



def eliminar_zona(db: Session, zona_id: int):
    """
    Eliminación lógica de una zona (borrado=False)
    No se puede eliminar si tiene cámaras activas.
    """

    zona = obtener_zona_por_id(db, zona_id)

    # ❌ Validar cámaras activas
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



def eliminar_zona_permanente(db: Session, zona_id: int):
    """
    Eliminación física definitiva.
    """
    zona = obtener_zona_por_id(db, zona_id)
    db.delete(zona)
    db.commit()
    return {"message": "Zona eliminada permanentemente"}

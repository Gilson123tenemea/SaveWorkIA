from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.modelos.zona_epp import ZonaEpp
from app.modelos.zona_modelo import Zona
from app.esquemas.zona_epp_esquema import ZonaEppCreate

# --------------------------------------------------
# Crear EPP para una zona
# --------------------------------------------------
def crear_epp_zona(db: Session, data: ZonaEppCreate):

    # Validar zona
    zona = db.query(Zona).filter(
        Zona.id_Zona == data.id_zona,
        Zona.borrado == True
    ).first()

    if not zona:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Zona no encontrada o inactiva"
        )

    # Evitar duplicados
    existe = db.query(ZonaEpp).filter(
        ZonaEpp.id_zona == data.id_zona,
        ZonaEpp.tipo_epp == data.tipo_epp,
        ZonaEpp.activo == True
    ).first()

    if existe:
        raise HTTPException(
            status_code=400,
            detail="Este EPP ya está configurado para la zona"
        )

    nuevo = ZonaEpp(
        id_zona=data.id_zona,
        tipo_epp=data.tipo_epp,
        obligatorio=data.obligatorio
    )

    db.add(nuevo)
    db.commit()
    db.refresh(nuevo)

    return nuevo


# --------------------------------------------------
# Obtener EPP activos por zona
# --------------------------------------------------
def obtener_epp_por_zona(db: Session, id_zona: int):
    return (
        db.query(ZonaEpp)
        .filter(
            ZonaEpp.id_zona == id_zona,
            ZonaEpp.activo == True
        )
        .all()
    )


# --------------------------------------------------
# Actualizar EPP de una zona (reset + crear)
# --------------------------------------------------
def actualizar_epp_de_zona(db: Session, id_zona: int, epps: list[str]):

    # Validar zona
    zona = db.query(Zona).filter(
        Zona.id_Zona == id_zona,
        Zona.borrado == True
    ).first()

    if not zona:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Zona no encontrada o inactiva"
        )

    # 1️⃣ Desactivar todos los EPP actuales de la zona
    db.query(ZonaEpp).filter(
        ZonaEpp.id_zona == id_zona,
        ZonaEpp.activo == True
    ).update(
        {"activo": False},
        synchronize_session=False
    )

    # 2️⃣ Crear nuevamente los EPP seleccionados
    nuevos = []

    for tipo in epps:
        nuevo = ZonaEpp(
            id_zona=id_zona,
            tipo_epp=tipo,
            obligatorio=True,
            activo=True
        )
        db.add(nuevo)
        nuevos.append(nuevo)

    db.commit()

    return {
        "message": "EPP de la zona actualizados correctamente",
        "total": len(nuevos)
    }

from sqlalchemy.orm import Session
from app.modelos.camara_modelo import Camara
from app.esquemas.camara_esquema import CamaraCreate, CamaraUpdate
from fastapi import HTTPException, status
from datetime import date
from sqlalchemy.orm import joinedload
from app.modelos.zona_modelo import Zona



def crear_camara(db: Session, camara: CamaraCreate):
    # código único
    if db.query(Camara).filter(Camara.codigo == camara.codigo).first():
        raise HTTPException(status_code=400, detail="El código de cámara ya está registrado")

    # IP única
    if db.query(Camara).filter(Camara.ipAddress == camara.ipAddress).first():
        raise HTTPException(status_code=400, detail="La dirección IP ya está en uso")

    nueva = Camara(**camara.model_dump())
    db.add(nueva)
    db.commit()
    db.refresh(nueva)
    return nueva

def obtener_camaras(db: Session, skip: int = 0, limit: int = 100):
    return (
        db.query(Camara)
        .options(
            joinedload(Camara.zona).joinedload(Zona.empresa)
        )
        .filter(Camara.borrado == True)
        .offset(skip)
        .limit(limit)
        .all()
    )


def obtener_camaras_por_zona(db: Session, zona_id: int, skip: int = 0, limit: int = 100):
    return (db.query(Camara)
            .filter(Camara.id_zona == zona_id, Camara.borrado == True)
            .offset(skip).limit(limit).all())

def obtener_camaras_por_administrador(db: Session, administrador_id: int, skip: int = 0, limit: int = 100):
    return (db.query(Camara)
            .filter(Camara.id_administrador == administrador_id, Camara.borrado == True)
            .offset(skip).limit(limit).all())

def obtener_camaras_por_estado(db: Session, estado: str, skip: int = 0, limit: int = 100):
    return (db.query(Camara)
            .filter(Camara.estado == estado, Camara.borrado == True)
            .offset(skip).limit(limit).all())

def obtener_camara_por_id(db: Session, camara_id: int):
    cam = db.query(Camara).filter(Camara.id_camara == camara_id).first()
    if not cam:
        raise HTTPException(status_code=404, detail="Cámara no encontrada")
    return cam

def obtener_camara_por_codigo(db: Session, codigo: str):
    cam = db.query(Camara).filter(Camara.codigo == codigo).first()
    if not cam:
        raise HTTPException(status_code=404, detail="Cámara no encontrada")
    return cam

def actualizar_camara(db: Session, camara_id: int, camara_update: CamaraUpdate):
    cam = obtener_camara_por_id(db, camara_id)

    data = camara_update.model_dump(exclude_unset=True)

    # validar unicidad si cambian código/IP
    if "codigo" in data:
        existe = db.query(Camara).filter(Camara.codigo == data["codigo"], Camara.id_camara != camara_id).first()
        if existe:
            raise HTTPException(status_code=400, detail="El código de cámara ya está registrado")

    if "ipAddress" in data:
        existe_ip = db.query(Camara).filter(Camara.ipAddress == data["ipAddress"], Camara.id_camara != camara_id).first()
        if existe_ip:
            raise HTTPException(status_code=400, detail="La dirección IP ya está en uso")

    for k, v in data.items():
        setattr(cam, k, v)

    db.commit()
    db.refresh(cam)
    return cam

def actualizar_ultima_transmision(db: Session, camara_id: int):
    cam = obtener_camara_por_id(db, camara_id)
    cam.ultimaTransmision = date.today()
    db.commit()
    db.refresh(cam)
    return cam

def actualizar_ultima_revision(db: Session, camara_id: int):
    cam = obtener_camara_por_id(db, camara_id)
    cam.ultima_revision = date.today()
    db.commit()
    db.refresh(cam)
    return cam

def cambiar_estado_camara(db: Session, camara_id: int, nuevo_estado: str):
    cam = obtener_camara_por_id(db, camara_id)
    cam.estado = nuevo_estado
    db.commit()
    db.refresh(cam)
    return cam

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

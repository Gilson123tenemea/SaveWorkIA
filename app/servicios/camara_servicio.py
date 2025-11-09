from sqlalchemy.orm import Session
from app.modelos.camara_modelo import Camara
from app.esquemas.camara_esquema import CamaraCreate, CamaraUpdate
from fastapi import HTTPException, status
from datetime import date

def crear_camara(db: Session, camara: CamaraCreate):
    """
    Crea una nueva cámara en la base de datos
    """
    # Verificar si el código ya existe
    camara_existente = db.query(Camara).filter(Camara.codigo == camara.codigo).first()
    if camara_existente:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El código de cámara ya está registrado"
        )
    
    # Verificar si la IP ya existe
    ip_existente = db.query(Camara).filter(Camara.ipAddress == camara.ipAddress).first()
    if ip_existente:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="La dirección IP ya está en uso"
        )
    
    nueva_camara = Camara(**camara.dict())
    db.add(nueva_camara)
    db.commit()
    db.refresh(nueva_camara)
    return nueva_camara

def obtener_camaras(db: Session, skip: int = 0, limit: int = 100):
    """
    Obtiene todas las cámaras (no borradas por defecto)
    """
    return db.query(Camara).filter(Camara.borrado == True).offset(skip).limit(limit).all()

def obtener_camaras_por_zona(db: Session, zona_id: int, skip: int = 0, limit: int = 100):
    """
    Obtiene todas las cámaras de una zona específica
    """
    return db.query(Camara).filter(
        Camara.id_zona == zona_id,
        Camara.borrado == True
    ).offset(skip).limit(limit).all()

def obtener_camaras_por_administrador(db: Session, administrador_id: int, skip: int = 0, limit: int = 100):
    """
    Obtiene todas las cámaras asignadas a un administrador
    """
    return db.query(Camara).filter(
        Camara.id_administrador == administrador_id,
        Camara.borrado == True
    ).offset(skip).limit(limit).all()

def obtener_camaras_por_estado(db: Session, estado: str, skip: int = 0, limit: int = 100):
    """
    Obtiene todas las cámaras con un estado específico (activa, inactiva, mantenimiento, etc.)
    """
    return db.query(Camara).filter(
        Camara.estado == estado,
        Camara.borrado == True
    ).offset(skip).limit(limit).all()

def obtener_camara_por_id(db: Session, camara_id: int):
    """
    Obtiene una cámara por su ID
    """
    camara = db.query(Camara).filter(Camara.id_camara == camara_id).first()
    if not camara:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cámara no encontrada"
        )
    return camara

def obtener_camara_por_codigo(db: Session, codigo: str):
    """
    Obtiene una cámara por su código
    """
    camara = db.query(Camara).filter(Camara.codigo == codigo).first()
    if not camara:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cámara no encontrada"
        )
    return camara

def actualizar_camara(db: Session, camara_id: int, camara_update: CamaraUpdate):
    """
    Actualiza los datos de una cámara
    """
    camara = obtener_camara_por_id(db, camara_id)
    
    # Actualizar solo los campos que no son None
    for campo, valor in camara_update.dict(exclude_unset=True).items():
        setattr(camara, campo, valor)
    
    db.commit()
    db.refresh(camara)
    return camara

def actualizar_ultima_transmision(db: Session, camara_id: int):
    """
    Actualiza la fecha de última transmisión de una cámara a la fecha actual
    """
    camara = obtener_camara_por_id(db, camara_id)
    camara.ultimaTransmision = date.today()
    db.commit()
    db.refresh(camara)
    return camara

def actualizar_ultima_revision(db: Session, camara_id: int):
    """
    Actualiza la fecha de última revisión de una cámara a la fecha actual
    """
    camara = obtener_camara_por_id(db, camara_id)
    camara.ultima_revision = date.today()
    db.commit()
    db.refresh(camara)
    return camara

def cambiar_estado_camara(db: Session, camara_id: int, nuevo_estado: str):
    """
    Cambia el estado de una cámara
    """
    camara = obtener_camara_por_id(db, camara_id)
    camara.estado = nuevo_estado
    db.commit()
    db.refresh(camara)
    return camara

def eliminar_camara(db: Session, camara_id: int):
    """
    Eliminación lógica de una cámara (marca borrado = False)
    """
    camara = obtener_camara_por_id(db, camara_id)
    camara.borrado = False
    db.commit()
    return {"message": "Cámara eliminada correctamente"}

def eliminar_camara_permanente(db: Session, camara_id: int):
    """
    Eliminación física de una cámara de la base de datos
    """
    camara = obtener_camara_por_id(db, camara_id)
    db.delete(camara)
    db.commit()
    return {"message": "Cámara eliminada permanentemente"}
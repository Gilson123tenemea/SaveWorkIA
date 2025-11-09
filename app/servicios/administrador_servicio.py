from sqlalchemy.orm import Session
from app.modelos.administrador import Administrador
from app.esquemas.administrador_esquema import AdministradorCreate

def crear_administrador(db: Session, administrador: AdministradorCreate):
    nuevo_admin = Administrador(**administrador.dict())
    db.add(nuevo_admin)
    db.commit()
    db.refresh(nuevo_admin)
    return nuevo_admin

def obtener_administradores(db: Session):
    return db.query(Administrador).all()

def obtener_administrador_por_id(db: Session, admin_id: int):
    return db.query(Administrador).filter(Administrador.id_administrador == admin_id).first()

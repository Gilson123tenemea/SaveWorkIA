from sqlalchemy.orm import Session
from app.modelos.trabajador import Trabajador
from app.esquemas.trabajador_esquema import TrabajadorCreate

def crear_trabajador(db: Session, trabajador: TrabajadorCreate):
    nuevo_trabajador = Trabajador(**trabajador.dict())
    db.add(nuevo_trabajador)
    db.commit()
    db.refresh(nuevo_trabajador)
    return nuevo_trabajador

def obtener_trabajadores(db: Session):
    return db.query(Trabajador).all()

def obtener_trabajador_por_id(db: Session, trabajador_id: int):
    return db.query(Trabajador).filter(Trabajador.id_trabajador == trabajador_id).first()

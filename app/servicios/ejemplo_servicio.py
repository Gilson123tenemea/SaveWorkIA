# app/servicios/ejemplo_servicio.py
from sqlalchemy.orm import Session
from app.modelos.ejemplo import Ejemplo
from app.esquemas.ejemplo_esquema import EjemploCrear

def obtener_ejemplos(db: Session, skip: int = 0, limit: int = 10):
    return db.query(Ejemplo).offset(skip).limit(limit).all()

def obtener_ejemplo(db: Session, ejemplo_id: int):
    return db.query(Ejemplo).filter(Ejemplo.id == ejemplo_id).first()

def crear_ejemplo(db: Session, ejemplo: EjemploCrear):
    db_ejemplo = Ejemplo(nombre=ejemplo.nombre, descripcion=ejemplo.descripcion)
    db.add(db_ejemplo)
    db.commit()
    db.refresh(db_ejemplo)
    return db_ejemplo

def eliminar_ejemplo(db: Session, ejemplo_id: int):
    obj = db.query(Ejemplo).filter(Ejemplo.id == ejemplo_id).first()
    if obj:
        db.delete(obj)
        db.commit()
    return obj

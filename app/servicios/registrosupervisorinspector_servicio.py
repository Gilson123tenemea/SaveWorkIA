from sqlalchemy.orm import Session
from app.modelos.registrosupervisorinspector import RegistroSupervisorInspector
from app.esquemas.registrosupervisorinspector_esquema import RegistroSupervisorInspectorCreate

def crear_registro(db: Session, registro: RegistroSupervisorInspectorCreate):
    nuevo_registro = RegistroSupervisorInspector(**registro.dict())
    db.add(nuevo_registro)
    db.commit()
    db.refresh(nuevo_registro)
    return nuevo_registro

def obtener_registros(db: Session):
    return db.query(RegistroSupervisorInspector).all()

def obtener_registro_por_id(db: Session, registro_id: int):
    return db.query(RegistroSupervisorInspector).filter(
        RegistroSupervisorInspector.id_registrosupervisorins == registro_id
    ).first()

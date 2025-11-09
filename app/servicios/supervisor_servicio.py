from sqlalchemy.orm import Session
from app.modelos.supervisor import Supervisor
from app.esquemas.supervisor_esquema import SupervisorCreate

def crear_supervisor(db: Session, supervisor: SupervisorCreate):
    nuevo_supervisor = Supervisor(**supervisor.dict())
    db.add(nuevo_supervisor)
    db.commit()
    db.refresh(nuevo_supervisor)
    return nuevo_supervisor

def obtener_supervisores(db: Session):
    return db.query(Supervisor).all()

def obtener_supervisor_por_id(db: Session, supervisor_id: int):
    return db.query(Supervisor).filter(Supervisor.id_supervisor == supervisor_id).first()

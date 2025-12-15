from sqlalchemy.orm import Session
from app.modelos.registros_asistencia import RegistroAsistencia
from app.esquemas.registros_asistencia_esquema import RegistroAsistenciaCreate
from datetime import datetime
from app.modelos.zona_epp import ZonaEpp

def obtener_epp_activos_por_zona(db: Session, id_zona: int) -> list[str]:
    """
    Devuelve lista de EPP activos configurados para una zona
    Ej: ["casco", "botas", "chaleco"]
    """
    epps = (
        db.query(ZonaEpp)
        .filter(
            ZonaEpp.id_zona == id_zona,
            ZonaEpp.activo == True
        )
        .all()
    )

    return [e.tipo_epp for e in epps]

def crear_registro_asistencia(db: Session, asistencia: RegistroAsistenciaCreate):
    nuevo = RegistroAsistencia(
        cumple_epp = asistencia.cumple_epp,
        codigo_ingresado = asistencia.codigo_ingresado,
        id_trabajador = asistencia.id_trabajador,
        id_empresa = asistencia.id_empresa,
        id_zona = asistencia.id_zona,
        id_supervisor = asistencia.id_supervisor,
        id_camara = asistencia.id_camara,   
        id_inspector = asistencia.id_inspector,
    )

    # Si el front no envía fecha_hora, usamos la actual
    if asistencia.fecha_hora:
        nuevo.fecha_hora = asistencia.fecha_hora
    else:
        nuevo.fecha_hora = datetime.now()

    db.add(nuevo)
    db.commit()
    db.refresh(nuevo)
    return nuevo

def obtener_epp_activos_por_zona(db: Session, id_zona: int) -> list[str]:
    """
    Devuelve lista de EPP activos y obligatorios configurados para una zona
    Ej: ["casco", "botas", "chaleco"]
    """
    epps = (
        db.query(ZonaEpp)
        .filter(
            ZonaEpp.id_zona == id_zona,
            ZonaEpp.activo == True,
            ZonaEpp.obligatorio == True
        )
        .all()
    )

    return [e.tipo_epp.lower() for e in epps]

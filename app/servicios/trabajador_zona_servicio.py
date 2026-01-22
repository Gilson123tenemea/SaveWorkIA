from sqlalchemy.orm import Session
from app.modelos.supervisor import Supervisor
from app.modelos.zona_modelo import Zona
from sqlalchemy import func
from app.modelos.inspector_zona import InspectorZona
from app.modelos.inspector import Inspector
from app.modelos.persona import Persona
from app.modelos.camara_modelo import Camara
from app.modelos.trabajador_zona import TrabajadorZona
from app.esquemas.trabajador_zona_esquema import TrabajadorZonaCreate
from app.modelos.trabajador import Trabajador
from app.modelos.registros_asistencia import RegistroAsistencia
from app.modelos.evidencias_fallo import EvidenciaFallo
from app.esquemas.trabajador_zona_esquema import TrabajadorZonaCreate
from app.modelos.trabajador import Trabajador

def obtener_zonas_con_detalles_por_supervisor(db: Session, id_supervisor: int):
    supervisor = db.query(Supervisor).filter(
        Supervisor.id_supervisor == id_supervisor,
        Supervisor.borrado == True
    ).first()

    if not supervisor:
        return []

    empresa_id = supervisor.id_empresa_supervisor
    zonas = db.query(Zona).filter(
        Zona.id_empresa_zona == empresa_id,
        Zona.borrado == True
    ).all()

    respuesta = []

    for zona in zonas:

        inspector_zona = db.query(InspectorZona).filter(
            InspectorZona.id_zona_inspectorzona == zona.id_Zona,
            InspectorZona.borrado == True
        ).first()

        inspector_data = None

        if inspector_zona:

            inspector = db.query(Inspector).filter(
                Inspector.id_inspector == inspector_zona.id_inspector_inspectorzona,
                Inspector.borrado == True
            ).first()

            if inspector:
                persona = db.query(Persona).filter(
                    Persona.id_persona == inspector.id_persona_inspector,
                    Persona.borrado == True
                ).first()

                if persona:
                    inspector_data = {
                        "nombre": persona.nombre,
                        "apellido": persona.apellido,
                        "cedula": persona.cedula
                    }

        # ❌ Si NO hay inspector, no agregamos esta zona
        if inspector_data is None:
            continue

        total_camaras = db.query(Camara).filter(
            Camara.id_zona == zona.id_Zona,
            Camara.borrado == True
        ).count()

        total_trabajadores = db.query(TrabajadorZona).filter(
            TrabajadorZona.id_zona_trabajadorzona == zona.id_Zona,
            TrabajadorZona.borrado == True
        ).count()

        # 📝 Total de registros de asistencia en la zona
        total_registros = db.query(RegistroAsistencia).filter(
            RegistroAsistencia.id_zona == zona.id_Zona
        ).count()

        # 🚨 Total de fallos en la zona (cumple_epp = False)
        total_fallos = db.query(RegistroAsistencia).filter(
            RegistroAsistencia.id_zona == zona.id_Zona,
            RegistroAsistencia.cumple_epp == False
        ).count()

        respuesta.append({
            "zona": {
                "id": zona.id_Zona,
                "nombre": zona.nombreZona,
                "latitud": zona.latitud,
                "longitud": zona.longitud,
            },
            "inspector": inspector_data,
            "total_camaras": total_camaras,
            "total_trabajadores": total_trabajadores,
            "total_registros": total_registros,
            "total_fallos": total_fallos
        })

    return respuesta


# ===========================
# 📌 CRUD Trabajador-Zona
# ===========================

def crear_trabajador_zona(db: Session, datos: TrabajadorZonaCreate):
    nueva_asignacion = TrabajadorZona(
        id_trabajador_trabajadorzona=datos.id_trabajador_trabajadorzona,
        id_zona_trabajadorzona=datos.id_zona_trabajadorzona,
        borrado=True
    )
    db.add(nueva_asignacion)
    db.commit()
    db.refresh(nueva_asignacion)
    return nueva_asignacion


def obtener_trabajador_zonas(db: Session):
    return db.query(TrabajadorZona).all()


def obtener_trabajador_zona_por_id(db: Session, asignacion_id: int):
    return db.query(TrabajadorZona).filter(
        TrabajadorZona.id_trabajador_zona == asignacion_id
    ).first()


# 🔥 Eliminación física
def eliminar_fisico_trabajador_zona(db: Session, asignacion_id: int):
    asignacion = obtener_trabajador_zona_por_id(db, asignacion_id)
    if asignacion:
        db.delete(asignacion)
        db.commit()
        return True
    return False


# 🔥 Eliminación lógica
def eliminar_logico_trabajador_zona(db: Session, asignacion_id: int):
    asignacion = obtener_trabajador_zona_por_id(db, asignacion_id)
    if asignacion:
        asignacion.borrado = False
        db.commit()
        db.refresh(asignacion)
        return asignacion
    return None

def obtener_trabajador_zonas_detalles(db: Session):

    filas = (
        db.query(
            TrabajadorZona.id_trabajador_zona.label("id_asignacion"),
            Trabajador.id_trabajador.label("trabajador_id"),
            Persona.nombre.label("trabajador_nombre"),
            Persona.apellido.label("trabajador_apellido"),
            Persona.cedula.label("trabajador_cedula"),
            Trabajador.cargo.label("trabajador_cargo"),
            Zona.id_Zona.label("zona_id"),
            Zona.nombreZona.label("zona_nombre"),
        )
        .join(Trabajador, TrabajadorZona.id_trabajador_trabajadorzona == Trabajador.id_trabajador)
        .join(Persona, Trabajador.id_persona_trabajador == Persona.id_persona)
        .join(Zona, TrabajadorZona.id_zona_trabajadorzona == Zona.id_Zona)
        .filter(TrabajadorZona.borrado == True)
        .all()
    )

    resultado = []
    for row in filas:
        resultado.append({
            "id_asignacion": row.id_asignacion,
            "trabajador_id": row.trabajador_id,
            "trabajador_nombre": row.trabajador_nombre,
            "trabajador_apellido": row.trabajador_apellido,
            "trabajador_cedula": row.trabajador_cedula,
            "trabajador_cargo": row.trabajador_cargo,
            "zona_id": row.zona_id,
            "zona_nombre": row.zona_nombre,
        })

    return resultado
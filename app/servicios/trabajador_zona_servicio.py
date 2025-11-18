from sqlalchemy.orm import Session
from app.modelos.supervisor import Supervisor
from app.modelos.zona_modelo import Zona
from app.modelos.inspector_zona import InspectorZona
from app.modelos.inspector import Inspector
from app.modelos.persona import Persona
from app.modelos.camara_modelo import Camara
from app.modelos.trabajador_zona import TrabajadorZona
from app.esquemas.trabajador_zona_esquema import TrabajadorZonaCreate


def obtener_zonas_con_detalles_por_supervisor(db: Session, id_supervisor: int):

    # 1️⃣ Obtener supervisor
    supervisor = db.query(Supervisor).filter(
        Supervisor.id_supervisor == id_supervisor,
        Supervisor.borrado == True
    ).first()

    if not supervisor:
        return []

    empresa_id = supervisor.id_empresa_supervisor

    # 2️⃣ Listar zonas de esa empresa
    zonas = db.query(Zona).filter(
      Zona.id_empresa_zona == empresa_id,
      Zona.borrado == True
    ).all()


    respuesta = []

    for zona in zonas:

        # 3️⃣ Obtener inspector asignado
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

        # 4️⃣ Contar cámaras
        total_camaras = db.query(Camara).filter(
            Camara.id_zona == zona.id_Zona,
            Camara.borrado == True
        ).count()

        # 5️⃣ Contar trabajadores
        total_trabajadores = db.query(TrabajadorZona).filter(
            TrabajadorZona.id_zona_trabajadorzona == zona.id_Zona,
            TrabajadorZona.borrado == True
        ).count()

        # 6️⃣ Armar respuesta final
        respuesta.append({
            "zona": {
                "id": zona.id_Zona,
                "nombre": zona.nombreZona,
                "latitud": zona.latitud,
                "longitud": zona.longitud,
            },
            "inspector": inspector_data,
            "total_camaras": total_camaras,
            "total_trabajadores": total_trabajadores
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

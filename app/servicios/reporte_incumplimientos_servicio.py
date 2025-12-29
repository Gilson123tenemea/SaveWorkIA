# app/servicios/reporte_incumplimientos_service.py

from sqlalchemy.orm import Session, joinedload
from fastapi import HTTPException
from datetime import date
from sqlalchemy import func
from app.modelos.registros_asistencia import RegistroAsistencia
from app.modelos.evidencias_fallo import EvidenciaFallo
from app.modelos.trabajador import Trabajador
from app.modelos.persona import Persona
from app.modelos.inspector import Inspector
from app.modelos.camara_modelo import Camara
from app.modelos.zona_modelo import Zona
import base64
from datetime import datetime
from app.modelos.inspector_zona import InspectorZona
from datetime import datetime, timedelta
from app.modelos.zona_epp import ZonaEpp
from app.utils.mapeo_epp import MAPEO_EPP_YOLO



from app.esquemas.reporte_incumplimientos_esquema import (
    IncumplimientoResponse,
    TrabajadorInfo,
    InspectorInfo,
    CamaraInfo,
    EvidenciaInfo
)

def obtener_epp_humanos_por_zona(db: Session, id_zona: int) -> list[str]:
    """
    Devuelve los EPP obligatorios y activos de una zona
    SIN duplicados
    Ej: ["casco", "gafas"]
    """

    epps = (
        db.query(ZonaEpp.tipo_epp)
        .filter(
            ZonaEpp.id_zona == id_zona,
            ZonaEpp.activo == True,
            ZonaEpp.obligatorio == True
        )
        .distinct()
        .all()
    )

    # Convierte de [(casco,), (gafas,)] → ["casco", "gafas"]
    return [epp[0] for epp in epps]

def obtener_incumplimientos_por_supervisor(db: Session, id_supervisor: int):

    hoy = date.today()
    inicio_dia = datetime.combine(hoy, datetime.min.time())
    fin_dia = datetime.combine(hoy, datetime.max.time())

    registros = (
        db.query(RegistroAsistencia)
        .join(EvidenciaFallo, EvidenciaFallo.id_registro == RegistroAsistencia.id_registro)
        .options(
            joinedload(RegistroAsistencia.trabajador).joinedload(Trabajador.persona),
            joinedload(RegistroAsistencia.inspector),
            joinedload(RegistroAsistencia.camara).joinedload(Camara.zona),
        )
        .filter(
            RegistroAsistencia.id_supervisor == id_supervisor,
            RegistroAsistencia.cumple_epp == False,
            RegistroAsistencia.fecha_hora.between(inicio_dia, fin_dia)
        )
        .all()
    )

    if not registros:
        return []

    resultados = []
    for reg in registros:
        evidencia = (
            db.query(EvidenciaFallo)
            .filter(EvidenciaFallo.id_registro == reg.id_registro)
            .first()
        )

        trabajador_persona = reg.trabajador.persona
        camara = reg.camara
        zona = camara.zona

        inspector_info = None
        if reg.inspector and reg.inspector.persona:
            p = reg.inspector.persona
            inspector_info = {"nombre": p.nombre, "apellido": p.apellido}

        foto_base64 = (
            base64.b64encode(evidencia.foto_data).decode("utf-8")
            if evidencia and evidencia.foto_data
            else None
        )

        clases_detectadas = (
            [c.strip().lower() for c in evidencia.detalle_fallo.split(",") if c.strip()]
            if evidencia and evidencia.detalle_fallo
            else []
        )

        epps_zona = obtener_epp_humanos_por_zona(db, zona.id_Zona)

        resultados.append({
            "trabajador": {
                "nombre": trabajador_persona.nombre,
                "apellido": trabajador_persona.apellido,
                "cedula": trabajador_persona.cedula
            },
            "inspector": inspector_info,
            "camara": {
                "codigo": camara.codigo,
                "zona": zona.nombreZona
            },
            "fecha_registro": reg.fecha_hora,
            "detecciones": clases_detectadas,
            "epps_zona": epps_zona,
            "evidencia": {
                "detalle": evidencia.detalle_fallo if evidencia else None,
                "foto_base64": foto_base64,
                "fecha": evidencia.fecha_captura if evidencia else None
            }
        })

    return resultados


def obtener_incumplimientos_trabajador(
    db: Session,
    cedula: str | None = None,
    codigo_trabajador: str | None = None,
    id_trabajador: int | None = None
):

    # ===========================
    # 1️⃣ OBTENER TRABAJADOR
    # ===========================
    query = db.query(Trabajador).join(Persona)

    if cedula:
        query = query.filter(Persona.cedula == cedula)
    elif codigo_trabajador:
        query = query.filter(Trabajador.codigo_trabajador == codigo_trabajador)
    elif id_trabajador:
        query = query.filter(Trabajador.id_trabajador == id_trabajador)
    else:
        raise HTTPException(400, "Debe enviar cedula, codigo_trabajador o id_trabajador")

    trabajador = query.first()
    if not trabajador:
        raise HTTPException(404, "Trabajador no encontrado")

    persona = trabajador.persona

    # ===========================
    # 2️⃣ ESTADÍSTICAS
    # ===========================
    todos = (
        db.query(RegistroAsistencia)
        .filter(RegistroAsistencia.id_trabajador == trabajador.id_trabajador)
        .all()
    )

    total = len(todos)
    cumple = len([r for r in todos if r.cumple_epp is True])
    incumple = total - cumple
    tasa = (cumple / total * 100) if total > 0 else 0

    # ===========================
    # 3️⃣ INCUMPLIMIENTOS
    # ===========================
    registros = (
        db.query(RegistroAsistencia)
        .join(EvidenciaFallo, EvidenciaFallo.id_registro == RegistroAsistencia.id_registro)
        .options(
            joinedload(RegistroAsistencia.inspector).joinedload(Inspector.persona),
            joinedload(RegistroAsistencia.camara).joinedload(Camara.zona)
        )
        .filter(
            RegistroAsistencia.id_trabajador == trabajador.id_trabajador,
            RegistroAsistencia.cumple_epp == False
        )
        .order_by(RegistroAsistencia.fecha_hora.desc())
        .all()
    )

    historial = []

    for reg in registros:
        evidencia = (
            db.query(EvidenciaFallo)
            .filter(EvidenciaFallo.id_registro == reg.id_registro)
            .first()
        )

        # Inspector
        inspector_info = None
        if reg.inspector:
            p = reg.inspector.persona
            inspector_info = {
                "nombre": p.nombre,
                "apellido": p.apellido
            }

        # Foto
        foto_base64 = None
        if evidencia and evidencia.foto_data:
            foto_base64 = base64.b64encode(evidencia.foto_data).decode("utf-8")

        # 🔥 CLASES YOLO DETECTADAS
        clases_detectadas = []
        if evidencia and evidencia.detalle_fallo:
            clases_detectadas = [
                c.strip() for c in evidencia.detalle_fallo.split(",") if c.strip()
            ]

        # 🔥 EPP OBLIGATORIOS DE LA ZONA (ES → YOLO)
        zona = reg.camara.zona
        epps_zona = obtener_epp_humanos_por_zona(db, zona.id_Zona)
        historial.append({
            "trabajador": {
                "nombre": persona.nombre,
                "apellido": persona.apellido,
                "cedula": persona.cedula
            },
            "inspector": inspector_info,
            "camara": {
                "codigo": reg.camara.codigo,
                "zona": zona.nombreZona
            },
            "fecha_registro": reg.fecha_hora,

            # 🔥 CLAVES QUE USA EL FRONT
            "detecciones": clases_detectadas,
            "epps_zona": epps_zona,

            "evidencia": {
                "detalle": evidencia.detalle_fallo,
                "foto_base64": foto_base64,
                "fecha": evidencia.fecha_captura
            }
        })

    return {
        "estadisticas": {
            "total": total,
            "cumple": cumple,
            "incumple": incumple,
            "tasa": round(tasa, 2)
        },
        "historial": historial
    }
def obtener_detecciones_filtradas(
    db: Session,
    id_empresa: int,
    fecha_desde: str | None,
    fecha_hasta: str | None,
    id_inspector: int | None,
    id_zona: int | None,
):

    query = (
        db.query(RegistroAsistencia)
        .join(EvidenciaFallo, EvidenciaFallo.id_registro == RegistroAsistencia.id_registro)
        .options(
            joinedload(RegistroAsistencia.trabajador).joinedload(Trabajador.persona),
            joinedload(RegistroAsistencia.inspector).joinedload(Inspector.persona),
            joinedload(RegistroAsistencia.camara).joinedload(Camara.zona)
        )
        .filter(
            RegistroAsistencia.id_empresa == id_empresa,
            RegistroAsistencia.cumple_epp == False
        )
    )

    # ============================
    # 1️⃣ FILTRO POR FECHAS
    # ============================
    if fecha_desde:
        query = query.filter(
            RegistroAsistencia.fecha_hora >= datetime.strptime(fecha_desde, "%Y-%m-%d")
        )

    if fecha_hasta:
        query = query.filter(
            RegistroAsistencia.fecha_hora <= (
                datetime.strptime(fecha_hasta, "%Y-%m-%d")
                + timedelta(days=1)
                - timedelta(seconds=1)
            )
        )

    # ============================
    # 2️⃣ FILTRO POR INSPECTOR
    # ============================
    if id_inspector:
        query = query.filter(RegistroAsistencia.id_inspector == id_inspector)

    if id_zona:
        query = query.filter(RegistroAsistencia.id_zona == id_zona)

    registros = query.order_by(RegistroAsistencia.fecha_hora.desc()).all()
    resultados = []

    for reg in registros:
        evidencia = (
            db.query(EvidenciaFallo)
            .filter(EvidenciaFallo.id_registro == reg.id_registro)
            .first()
        )

        # Inspector
        inspector_info = None
        if reg.inspector:
            p = reg.inspector.persona
            inspector_info = {"nombre": p.nombre, "apellido": p.apellido}

        # Foto
        foto_base64 = None
        if evidencia and evidencia.foto_data:
            foto_base64 = base64.b64encode(evidencia.foto_data).decode("utf-8")

        # 🔥 YOLO
        clases_detectadas = []
        if evidencia and evidencia.detalle_fallo:
            clases_detectadas = [
                c.strip() for c in evidencia.detalle_fallo.split(",") if c.strip()
            ]

        # 🔥 EPP DE ZONA (ES → YOLO)
        zona = reg.camara.zona
        epps_zona = obtener_epp_humanos_por_zona(db, zona.id_Zona)

        tper = reg.trabajador.persona

        resultados.append({
            "trabajador": {
                "nombre": tper.nombre,
                "apellido": tper.apellido,
                "cedula": tper.cedula,
            },
            "inspector": inspector_info,
            "camara": {
                "codigo": reg.camara.codigo,
                "zona": zona.nombreZona,
            },
            "fecha_registro": reg.fecha_hora,

            # 🔥 CLAVES PARA EL FRONT
            "detecciones": clases_detectadas,
            "epps_zona": epps_zona,

            "evidencia": {
                "detalle": evidencia.detalle_fallo,
                "foto_base64": foto_base64,
                "fecha": evidencia.fecha_captura,
            }
        })

    return resultados


def obtener_inspectores_por_empresa(db: Session, id_empresa: int):

    inspectores_ids = (
        db.query(InspectorZona.id_inspector_inspectorzona)
        .join(Zona, Zona.id_Zona == InspectorZona.id_zona_inspectorzona)
        .filter(
            Zona.id_empresa_zona == id_empresa,
            Zona.borrado == True,
            InspectorZona.borrado == True
        )
        .distinct()
        .all()
    )

    ids = [row[0] for row in inspectores_ids]

    inspectores = (
        db.query(Inspector)
        .filter(
            Inspector.id_inspector.in_(ids),
            Inspector.borrado == True
        )
        .all()
    )

    resultados = []
    for ins in inspectores:
        persona = ins.persona
        resultados.append({
            "id": ins.id_inspector,
            "nombre": persona.nombre,
            "apellido": persona.apellido
        })

    return resultados

def obtener_zonas_filtradas(db: Session, id_empresa: int, id_inspector: int | None):

    # ===========================
    # 1️⃣ SIN INSPECTOR → TODAS LAS ZONAS DE LA EMPRESA
    # ===========================
    if not id_inspector:
        zonas = (
            db.query(Zona)
            .filter(
                Zona.id_empresa_zona == id_empresa,
                Zona.borrado == True
            )
            .all()
        )

        return [{"id": z.id_Zona, "nombre": z.nombreZona} for z in zonas]

    # ===========================
    # 2️⃣ CON INSPECTOR → ZONAS ASIGNADAS
    # ===========================
    zonas_inspector_ids = (
        db.query(InspectorZona.id_zona_inspectorzona)
        .filter(
            InspectorZona.id_inspector_inspectorzona == id_inspector,
            InspectorZona.borrado == True
        )
        .all()
    )

    ids_zonas = [z[0] for z in zonas_inspector_ids]

    zonas = (
        db.query(Zona)
        .filter(
            Zona.id_Zona.in_(ids_zonas),
            Zona.borrado == True
        )
        .all()
    )

    return [{"id": z.id_Zona, "nombre": z.nombreZona} for z in zonas]

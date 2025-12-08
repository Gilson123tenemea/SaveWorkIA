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

from app.esquemas.reporte_incumplimientos_esquema import (
    IncumplimientoResponse,
    TrabajadorInfo,
    InspectorInfo,
    CamaraInfo,
    EvidenciaInfo
)


def obtener_incumplimientos_por_supervisor(db: Session, id_supervisor: int):

    hoy = date.today()

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
            func.date(RegistroAsistencia.fecha_hora) == hoy
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

        # Inspector
        if reg.inspector:
            inspector_persona = db.query(Persona).filter(
                Persona.id_persona == reg.inspector.id_persona_inspector
            ).first()

            inspector_info = InspectorInfo(
                nombre=inspector_persona.nombre,
                apellido=inspector_persona.apellido
            )
        else:
            inspector_info = InspectorInfo(nombre=None, apellido=None)

        camara = reg.camara
        zona = camara.zona

        # ✅ Convertir bytes a base64
        foto_base64 = None
        if evidencia and evidencia.foto_data:
            foto_base64 = base64.b64encode(evidencia.foto_data).decode("utf-8")

        resultados.append(
            IncumplimientoResponse(
                trabajador=TrabajadorInfo(
                    nombre=trabajador_persona.nombre,
                    apellido=trabajador_persona.apellido,
                    cedula=trabajador_persona.cedula
                ),
                inspector=inspector_info,
                camara=CamaraInfo(
                    codigo=camara.codigo,
                    zona=zona.nombreZona
                ),
                evidencia=EvidenciaInfo(
                    detalle=evidencia.detalle_fallo,
                    foto_base64=foto_base64,
                    fecha=evidencia.fecha_captura
                ),
                fecha_registro=reg.fecha_hora
            )
        )

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
    # 2️⃣ OBTENER TODOS LOS REGISTROS DEL TRABAJADOR (para estadisticas)
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
    # 3️⃣ OBTENER SOLO LOS INCUMPLIMIENTOS (LÓGICA ACTUAL SIN CAMBIOS)
    # ===========================
    registros = (
        db.query(RegistroAsistencia)
        .join(EvidenciaFallo, EvidenciaFallo.id_registro == RegistroAsistencia.id_registro)
        .options(
            joinedload(RegistroAsistencia.inspector),
            joinedload(RegistroAsistencia.camara).joinedload(Camara.zona)
        )
        .filter(
            RegistroAsistencia.id_trabajador == trabajador.id_trabajador,
            RegistroAsistencia.cumple_epp == False
        )
        .order_by(RegistroAsistencia.fecha_hora.desc())
        .all()
    )

    resultados = []

    for reg in registros:
        evidencia = db.query(EvidenciaFallo).filter(EvidenciaFallo.id_registro == reg.id_registro).first()

        # Inspector
        if reg.inspector:
            inspector_persona = reg.inspector.persona
            inspector_info = InspectorInfo(
                nombre=inspector_persona.nombre,
                apellido=inspector_persona.apellido
            )
        else:
            inspector_info = InspectorInfo(nombre=None, apellido=None)

        # Foto base64
        foto_base64 = None
        if evidencia and evidencia.foto_data:
            foto_base64 = base64.b64encode(evidencia.foto_data).decode("utf-8")

        resultados.append(
            IncumplimientoResponse(
                trabajador=TrabajadorInfo(
                    nombre=persona.nombre,
                    apellido=persona.apellido,
                    cedula=persona.cedula
                ),
                inspector=inspector_info,
                camara=CamaraInfo(
                    codigo=reg.camara.codigo,
                    zona=reg.camara.zona.nombreZona
                ),
                evidencia=EvidenciaInfo(
                    detalle=evidencia.detalle_fallo,
                    foto_base64=foto_base64,
                    fecha=evidencia.fecha_captura
                ),
                fecha_registro=reg.fecha_hora
            )
        )

    # ===========================
    # 4️⃣ RETORNAR UN OBJETO NUEVO
    # ===========================
    return {
        "estadisticas": {
            "total": total,
            "cumple": cumple,
            "incumple": incumple,
            "tasa": round(tasa, 2)
        },
        "historial": resultados
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
       fecha_d = datetime.strptime(fecha_desde, "%Y-%m-%d")
       query = query.filter(RegistroAsistencia.fecha_hora >= fecha_d)

    if fecha_hasta:
       fecha_h = datetime.strptime(fecha_hasta, "%Y-%m-%d") + timedelta(days=1) - timedelta(seconds=1)
       query = query.filter(RegistroAsistencia.fecha_hora <= fecha_h)


    # ==================================
    # 2️⃣ FILTRO POR INSPECTOR
    # ==================================
    zonas_validas = []

    if id_inspector:
        query = query.filter(RegistroAsistencia.id_inspector == id_inspector)

        zonas_inspector = (
            db.query(InspectorZona.id_zona_inspectorzona)
            .filter(
                InspectorZona.id_inspector_inspectorzona == id_inspector,
                InspectorZona.borrado == True
            )
            .all()
        )
        zonas_validas = [z[0] for z in zonas_inspector]

        if id_zona is None:
            query = query.filter(RegistroAsistencia.id_zona.in_(zonas_validas))

    else:
        # ============================
        # 3️⃣ SIN INSPECTOR → ZONAS = TODAS LAS DE LA EMPRESA
        # ============================
        zonas_empresa = (
            db.query(Zona.id_Zona)
            .filter(
                Zona.id_empresa_zona == id_empresa,
                Zona.borrado == True
            )
            .all()
        )
        zonas_validas = [z[0] for z in zonas_empresa]

        if id_zona is None:
            query = query.filter(RegistroAsistencia.id_zona.in_(zonas_validas))

    # ==================================
    # 4️⃣ FILTRO FINAL POR ZONA (si el usuario la seleccionó)
    # ==================================
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

        # Inspector info
        if reg.inspector:
            ins = reg.inspector.persona
            inspector_info = InspectorInfo(nombre=ins.nombre, apellido=ins.apellido)
        else:
            inspector_info = InspectorInfo(nombre=None, apellido=None)

        # Foto base64
        foto_base64 = None
        if evidencia and evidencia.foto_data:
            foto_base64 = base64.b64encode(evidencia.foto_data).decode("utf-8")

        tper = reg.trabajador.persona

        resultados.append(
            IncumplimientoResponse(
                trabajador=TrabajadorInfo(
                    nombre=tper.nombre,
                    apellido=tper.apellido,
                    cedula=tper.cedula,
                ),
                inspector=inspector_info,
                camara=CamaraInfo(
                    codigo=reg.camara.codigo,
                    zona=reg.camara.zona.nombreZona,
                ),
                evidencia=EvidenciaInfo(
                    detalle=evidencia.detalle_fallo,
                    foto_base64=foto_base64,
                    fecha=evidencia.fecha_captura,
                ),
                fecha_registro=reg.fecha_hora,
            )
        )

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

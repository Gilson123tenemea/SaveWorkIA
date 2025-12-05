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

from app.esquemas.reporte_incumplimientos_esquema import (
    IncumplimientoResponse,
    TrabajadorInfo,
    InspectorInfo,
    CamaraInfo,
    EvidenciaInfo
)


def obtener_incumplimientos_por_supervisor(db: Session, id_supervisor: int):

    hoy = date.today()  # Ejemplo: 2025-12-04

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
            RegistroAsistencia.cumple_epp == False,             # Solo incumplimientos
            func.date(RegistroAsistencia.fecha_hora) == hoy     # 🔥 Solo registros del día actual
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

        # Inspector corregido (sin operador walrus)
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
                    foto_url=evidencia.foto_url,
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

    # Buscar trabajador usando cualquier parámetro
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

    # Obtener todos los registros incumplidos del trabajador
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

        inspector_info = None
        if reg.inspector:
            inspector_persona = reg.inspector.persona
            inspector_info = InspectorInfo(
                nombre=inspector_persona.nombre,
                apellido=inspector_persona.apellido
            )
        else:
            inspector_info = InspectorInfo(nombre=None, apellido=None)

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
                    foto_url=evidencia.foto_url,
                    fecha=evidencia.fecha_captura
                ),
                fecha_registro=reg.fecha_hora
            )
        )

    return resultados
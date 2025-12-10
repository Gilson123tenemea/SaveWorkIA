# app/servicios/reporte_inspector_incumplimiento_servicio.py

from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func
import base64
from datetime import datetime, timedelta
from fastapi import HTTPException
from app.modelos.inspector_zona import InspectorZona

from app.modelos.registros_asistencia import RegistroAsistencia
from app.modelos.evidencias_fallo import EvidenciaFallo
from app.modelos.trabajador import Trabajador
from app.modelos.persona import Persona
from app.modelos.camara_modelo import Camara
from app.modelos.zona_modelo import Zona

from app.esquemas.reporte_inspector_incumplimiento_esquema import (
    TrabajadorInfo,
    CamaraInfo,
    EvidenciaInfo,
    IncumplimientoInspectorResponse
)


def obtener_incumplimientos_por_inspector(
    db: Session,
    id_inspector: int,
    fecha_desde: str | None = None,
    fecha_hasta: str | None = None,
    id_zona: int | None = None
):
    query = (
        db.query(RegistroAsistencia)
        .join(EvidenciaFallo, EvidenciaFallo.id_registro == RegistroAsistencia.id_registro)
        .options(
            joinedload(RegistroAsistencia.trabajador).joinedload(Trabajador.persona),
            joinedload(RegistroAsistencia.camara).joinedload(Camara.zona)
        )
        .filter(
            RegistroAsistencia.id_inspector == id_inspector,
            RegistroAsistencia.cumple_epp == False
        )
    )

    # ============================
    # 1️⃣ FILTRO POR FECHA DESDE
    # ============================
    if fecha_desde:
        fecha_d = datetime.strptime(fecha_desde, "%Y-%m-%d")
        query = query.filter(RegistroAsistencia.fecha_hora >= fecha_d)

    # ============================
    # 2️⃣ FILTRO POR FECHA HASTA
    # ============================
    if fecha_hasta:
        fecha_h = datetime.strptime(fecha_hasta, "%Y-%m-%d") + timedelta(days=1) - timedelta(seconds=1)
        query = query.filter(RegistroAsistencia.fecha_hora <= fecha_h)

    # ============================
    # 3️⃣ FILTRO POR ZONA
    # ============================
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

        # Convertir imagen
        foto_base64 = None
        if evidencia and evidencia.foto_data:
            foto_base64 = base64.b64encode(evidencia.foto_data).decode("utf-8")

        tper = reg.trabajador.persona
        cam = reg.camara

        resultados.append(
            IncumplimientoInspectorResponse(
              trabajador=TrabajadorInfo(
              nombre=tper.nombre,
              apellido=tper.apellido,
              cedula=tper.cedula
            ),
             camara=CamaraInfo(
             codigo=cam.codigo,
             zona=cam.zona.nombreZona
            ),
             evidencia=EvidenciaInfo(
              id_evidencia=evidencia.id_evidencia,
              detalle=evidencia.detalle_fallo,
              foto_base64=foto_base64,
              fecha=evidencia.fecha_captura,
              estado=evidencia.estado,
              observaciones=evidencia.observaciones
),

            fecha_registro=reg.fecha_hora
    )
)


    return resultados

def obtener_incumplimientos_por_cedula(db: Session, cedula: str):

    # 1️⃣ BUSCAR TRABAJADOR POR CEDULA
    trabajador = (
        db.query(Trabajador)
        .join(Persona)
        .filter(Persona.cedula == cedula)
        .first()
    )

    if not trabajador:
        raise HTTPException(404, detail="Trabajador no encontrado")

    persona = trabajador.persona

    # 2️⃣ OBTENER INCUMPLIMIENTOS DEL TRABAJADOR
    registros = (
        db.query(RegistroAsistencia)
        .join(EvidenciaFallo, EvidenciaFallo.id_registro == RegistroAsistencia.id_registro)
        .options(
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
        evidencia = (
            db.query(EvidenciaFallo)
            .filter(EvidenciaFallo.id_registro == reg.id_registro)
            .first()
        )

        # Convertir imagen a base64
        foto_base64 = None
        if evidencia and evidencia.foto_data:
            foto_base64 = base64.b64encode(evidencia.foto_data).decode("utf-8")

        # Armar respuesta
        resultados.append(
            IncumplimientoInspectorResponse(
                trabajador=TrabajadorInfo(
                    nombre=persona.nombre,
                    apellido=persona.apellido,
                    cedula=persona.cedula
                ),
                camara=CamaraInfo(
                    codigo=reg.camara.codigo,
                    zona=reg.camara.zona.nombreZona
                ),
                evidencia=EvidenciaInfo(
                    id_evidencia=evidencia.id_evidencia,
                    detalle=evidencia.detalle_fallo,
                    foto_base64=foto_base64,
                    fecha=evidencia.fecha_captura,
                    estado=evidencia.estado,
                    observaciones=evidencia.observaciones
                ),
                fecha_registro=reg.fecha_hora
            )
        )

    return resultados


def obtener_zonas_por_inspector(db: Session, id_inspector: int):

    zonas_ids = (
        db.query(InspectorZona.id_zona_inspectorzona)
        .filter(
            InspectorZona.id_inspector_inspectorzona == id_inspector,
            InspectorZona.borrado == True  
        )
        .all()
    )

    ids = [z[0] for z in zonas_ids]

    if not ids:
        return []  

    zonas = (
        db.query(Zona)
        .filter(
            Zona.id_Zona.in_(ids),
            Zona.borrado == True
        )
        .all()
    )

    return [
        {
            "id": z.id_Zona,
            "nombre": z.nombreZona
        }
        for z in zonas
    ]

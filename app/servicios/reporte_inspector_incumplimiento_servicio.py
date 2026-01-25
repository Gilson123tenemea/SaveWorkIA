# app/servicios/reporte_inspector_incumplimiento_servicio.py

from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func
import base64
from datetime import datetime, timedelta
from fastapi import HTTPException
from app.modelos.inspector_zona import InspectorZona
from datetime import datetime, timedelta
from app.modelos.registros_asistencia import RegistroAsistencia
from app.modelos.evidencias_fallo import EvidenciaFallo
from app.modelos.trabajador import Trabajador
from app.modelos.persona import Persona
from app.modelos.camara_modelo import Camara
from app.modelos.zona_modelo import Zona
from app.modelos.zona_epp import ZonaEpp
from app.utils.mapeo_epp import MAPEO_EPP_YOLO

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
    from datetime import date, datetime, timedelta
    
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

    
    if id_zona:
        query = query.filter(RegistroAsistencia.id_zona == id_zona)
    else:
        if fecha_desde:
            fecha_d = datetime.strptime(fecha_desde, "%Y-%m-%d")
            query = query.filter(RegistroAsistencia.fecha_hora >= fecha_d)
        else:
            hoy = date.today()
            inicio_dia = datetime.combine(hoy, datetime.min.time())
            query = query.filter(RegistroAsistencia.fecha_hora >= inicio_dia)

        if fecha_hasta:
            fecha_h = datetime.strptime(fecha_hasta, "%Y-%m-%d") + timedelta(days=1) - timedelta(seconds=1)
            query = query.filter(RegistroAsistencia.fecha_hora <= fecha_h)
        else:
            hoy = date.today()
            fin_dia = datetime.combine(hoy, datetime.max.time())
            query = query.filter(RegistroAsistencia.fecha_hora <= fin_dia)

    registros = query.order_by(RegistroAsistencia.fecha_hora.desc()).all()

    resultados = []

    for reg in registros:
        evidencia = (
            db.query(EvidenciaFallo)
            .filter(EvidenciaFallo.id_registro == reg.id_registro)
            .first()
        )

        foto_base64 = None
        if evidencia and evidencia.foto_data:
            foto_base64 = base64.b64encode(evidencia.foto_data).decode("utf-8")

        tper = reg.trabajador.persona
        cam = reg.camara

        clases_detectadas = []
        if evidencia and evidencia.detalle_fallo:
            clases_detectadas = [
                c.strip() for c in evidencia.detalle_fallo.split(",") if c.strip()
            ]

        zona = reg.camara.zona
        epps_zona = obtener_epp_humanos_por_zona(db, zona.id_Zona)

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
                fecha_registro=reg.fecha_hora,
                detecciones=clases_detectadas,  
                epps_zona=epps_zona  
            )
        )

    return resultados

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

def obtener_incumplimientos_por_cedula(db: Session, cedula: str):
    from datetime import date
    
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

    # ✅ CONTAR REVISADOS (estado == 0/False en evidencias_fallo)
    # Los revisados son los que tienen estado = False (0 en BD)
    todas_evidencias = (
        db.query(EvidenciaFallo)
        .join(RegistroAsistencia, RegistroAsistencia.id_registro == EvidenciaFallo.id_registro)
        .filter(
            RegistroAsistencia.id_trabajador == trabajador.id_trabajador
        )
        .all()
    )
    
    # Contamos los que tienen estado == False (revisados)
    revisados = sum(1 for ev in todas_evidencias if ev.estado is False)

    # ===========================
    # 3️⃣ INCUMPLIMIENTOS
    # ===========================
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

        # 📸 Foto
        foto_base64 = None
        if evidencia and evidencia.foto_data:
            foto_base64 = base64.b64encode(evidencia.foto_data).decode("utf-8")

        # 🔥 CLASES YOLO DETECTADAS
        clases_detectadas = []
        if evidencia and evidencia.detalle_fallo:
            clases_detectadas = [   
                c.strip() for c in evidencia.detalle_fallo.split(",") if c.strip()
            ]

        # 🔥 EPP OBLIGATORIOS DE LA ZONA
        zona = reg.camara.zona
        epps_zona = obtener_epp_humanos_por_zona(db, zona.id_Zona)

        resultados.append(
            IncumplimientoInspectorResponse(
                trabajador=TrabajadorInfo(
                    nombre=persona.nombre,
                    apellido=persona.apellido,
                    cedula=persona.cedula
                ),
                camara=CamaraInfo(
                    codigo=reg.camara.codigo,
                    zona=zona.nombreZona
                ),
                detecciones=clases_detectadas,
                epps_zona=epps_zona,
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

    # ===========================
    # 4️⃣ RESPONSE FINAL
    # ===========================
    return {
        "estadisticas": {
            "total": total,
            "cumple": cumple,
            "incumple": incumple,
            "revisados": revisados,
            "tasa": round(tasa, 2)
        },
        "historial": resultados
    }


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

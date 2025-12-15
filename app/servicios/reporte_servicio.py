# app/servicios/reporte_servicio.py
import io
import json
from datetime import datetime
from typing import Optional, List, Dict, Tuple

from sqlalchemy.orm import Session
from sqlalchemy import func, and_

from fastapi import HTTPException

from app.modelos.reporte import Reporte
from app.modelos.registros_asistencia import RegistroAsistencia
from app.modelos.evidencias_fallo import EvidenciaFallo
from app.modelos.zona_modelo import Zona
from app.modelos.trabajador import Trabajador
from app.modelos.persona import Persona

# PDF
from reportlab.lib.pagesizes import A4, landscape
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors

# EXCEL
from openpyxl import Workbook
from openpyxl.styles import Font, Alignment
from openpyxl.utils import get_column_letter


# -----------------------------
# Helpers
# -----------------------------
def _parse_date(date_str: str) -> datetime:
    """
    Acepta 'YYYY-MM-DD' y lo convierte a datetime (00:00:00).
    """
    try:
        return datetime.strptime(date_str, "%Y-%m-%d")
    except Exception:
        raise HTTPException(status_code=400, detail=f"Fecha inválida: {date_str}. Use YYYY-MM-DD.")


def _end_of_day(dt: datetime) -> datetime:
    return dt.replace(hour=23, minute=59, second=59, microsecond=0)


def registrar_reporte(
    db: Session,
    tipo_reporte: str,
    formato: str,
    filtros: Optional[dict],
    generado_por: str,
    id_empresa: int,
    id_inspector: Optional[int] = None,
) -> Reporte:
    rep = Reporte(
        tipo_reporte=tipo_reporte,
        formato=formato,
        filtros=json.dumps(filtros, ensure_ascii=False) if filtros else None,
        generado_por=generado_por,
        id_empresa=id_empresa,
        id_inspector=id_inspector,
        borrado=True,
    )
    db.add(rep)
    db.commit()
    db.refresh(rep)
    return rep


# -----------------------------
# 3.1) ESTADÍSTICAS (BARRAS)
# -----------------------------
def barras_incumplimiento_por_zona(
    db: Session,
    id_inspector: int,
    id_empresa: int,
    fecha_desde: Optional[str] = None,
    fecha_hasta: Optional[str] = None,
) -> List[Tuple[str, int]]:
    """
    Incumplimientos = registros con evidencia_fallo asociada (tu modelo actual).
    """
    filters = [
        RegistroAsistencia.id_inspector == id_inspector,
        RegistroAsistencia.id_empresa == id_empresa,
    ]

    if fecha_desde:
        d = _parse_date(fecha_desde)
        filters.append(RegistroAsistencia.fecha_hora >= d)
    if fecha_hasta:
        h = _end_of_day(_parse_date(fecha_hasta))
        filters.append(RegistroAsistencia.fecha_hora <= h)

    q = (
        db.query(
            Zona.nombreZona.label("zona"),
            func.count(EvidenciaFallo.id_evidencia).label("incumplimientos"),
        )
        .join(RegistroAsistencia, RegistroAsistencia.id_zona == Zona.id_Zona)
        .join(EvidenciaFallo, EvidenciaFallo.id_registro == RegistroAsistencia.id_registro)
        .filter(and_(*filters))
        .group_by(Zona.nombreZona)
        .order_by(func.count(EvidenciaFallo.id_evidencia).desc())
    )

    return [(r.zona, int(r.incumplimientos)) for r in q.all()]


def barras_cumplimiento_por_zona(
    db: Session,
    id_inspector: int,
    id_empresa: int,
    fecha_desde: Optional[str] = None,
    fecha_hasta: Optional[str] = None,
) -> List[Tuple[str, int]]:
    """
    Cumplimientos = registros donde cumple_epp = True
    (independiente de evidencia).
    """
    filters = [
        RegistroAsistencia.id_inspector == id_inspector,
        RegistroAsistencia.id_empresa == id_empresa,
        RegistroAsistencia.cumple_epp == True,  # noqa: E712
    ]

    if fecha_desde:
        d = _parse_date(fecha_desde)
        filters.append(RegistroAsistencia.fecha_hora >= d)
    if fecha_hasta:
        h = _end_of_day(_parse_date(fecha_hasta))
        filters.append(RegistroAsistencia.fecha_hora <= h)

    q = (
        db.query(
            Zona.nombreZona.label("zona"),
            func.count(RegistroAsistencia.id_registro).label("cumplimientos"),
        )
        .join(RegistroAsistencia, RegistroAsistencia.id_zona == Zona.id_Zona)
        .filter(and_(*filters))
        .group_by(Zona.nombreZona)
        .order_by(func.count(RegistroAsistencia.id_registro).desc())
    )

    return [(r.zona, int(r.cumplimientos)) for r in q.all()]


# -----------------------------
# 3.2) ESTADÍSTICAS (PASTEL)
#     "EPP más cumplido"
# -----------------------------
EPP_LABELS = [
    ("Casco", ["casco", "helmet"]),
    ("Chaleco", ["chaleco", "vest"]),
    ("Gafas", ["gafas", "glasses", "goggles"]),
    ("Guantes", ["guantes", "gloves"]),
    ("Botas", ["botas", "boots"]),
]

def pastel_epp_mas_cumplido(
    db: Session,
    id_empresa: int,
    id_inspector: Optional[int] = None,
    id_zona: Optional[int] = None,
    fecha_desde: Optional[str] = None,
    fecha_hasta: Optional[str] = None,
) -> List[Tuple[str, int]]:
    """
    Lógica compatible con tu BD:
    - Total de registros en el filtro
    - Para cada EPP:
        "cumple EPP" (para ese implemento) = total_registros - registros donde evidencia.detalle_fallo contiene ese epp como faltante
    Asume que en detalle_fallo guardas algo tipo: "Falta Casco, Chaleco" o similar.
    """
    filters = [RegistroAsistencia.id_empresa == id_empresa]

    if id_inspector is not None:
        filters.append(RegistroAsistencia.id_inspector == id_inspector)
    if id_zona is not None:
        filters.append(RegistroAsistencia.id_zona == id_zona)
    if fecha_desde:
        d = _parse_date(fecha_desde)
        filters.append(RegistroAsistencia.fecha_hora >= d)
    if fecha_hasta:
        h = _end_of_day(_parse_date(fecha_hasta))
        filters.append(RegistroAsistencia.fecha_hora <= h)

    total_registros = (
        db.query(func.count(RegistroAsistencia.id_registro))
        .filter(and_(*filters))
        .scalar()
    ) or 0

    if total_registros == 0:
        return [(lbl, 0) for lbl, _ in EPP_LABELS]

    # Conteo de NO cumplimiento por EPP según texto en detalle_fallo
    resultados: List[Tuple[str, int]] = []

    for label, keywords in EPP_LABELS:
        # Subquery: registros con evidencia cuyo detalle contiene el keyword
        no_cumple_count = (
            db.query(func.count(func.distinct(RegistroAsistencia.id_registro)))
            .join(EvidenciaFallo, EvidenciaFallo.id_registro == RegistroAsistencia.id_registro)
            .filter(and_(*filters))
            .filter(
                or_(*[
                    func.lower(EvidenciaFallo.detalle_fallo).like(f"%{kw.lower()}%")
                    for kw in keywords
                ])
            )
            .scalar()
        ) or 0

        cumple = max(total_registros - int(no_cumple_count), 0)
        resultados.append((label, cumple))

    # Ordena de mayor a menor “cumplimiento”
    resultados.sort(key=lambda x: x[1], reverse=True)
    return resultados


# SQLAlchemy needs or_
from sqlalchemy import or_


# -----------------------------
# 3.3) PDF: Trabajadores por zona y rango
# -----------------------------
def generar_pdf_trabajadores_zona(
    db: Session,
    id_empresa: int,
    id_zona: int,
    fecha_desde: str,
    fecha_hasta: str,
) -> bytes:
    d = _parse_date(fecha_desde)
    h = _end_of_day(_parse_date(fecha_hasta))

    # Traemos registros con joins completos (trabajador -> persona, zona, evidencia)
    rows = (
        db.query(
            RegistroAsistencia.fecha_hora,
            RegistroAsistencia.cumple_epp,
            Zona.nombreZona,
            Trabajador.codigo_trabajador,
            Persona.cedula,
            Persona.nombre,
            Persona.apellido,
            Persona.correo,
            Persona.telefono,
            EvidenciaFallo.detalle_fallo,
            EvidenciaFallo.observaciones,
        )
        .join(Zona, Zona.id_Zona == RegistroAsistencia.id_zona)
        .join(Trabajador, Trabajador.id_trabajador == RegistroAsistencia.id_trabajador)
        .join(Persona, Persona.id_persona == Trabajador.id_persona_trabajador)
        .outerjoin(EvidenciaFallo, EvidenciaFallo.id_registro == RegistroAsistencia.id_registro)
        .filter(
            RegistroAsistencia.id_empresa == id_empresa,
            RegistroAsistencia.id_zona == id_zona,
            RegistroAsistencia.fecha_hora >= d,
            RegistroAsistencia.fecha_hora <= h,
        )
        .order_by(RegistroAsistencia.fecha_hora.desc())
        .all()
    )

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=landscape(A4), leftMargin=24, rightMargin=24, topMargin=18, bottomMargin=18)

    styles = getSampleStyleSheet()
    story = []

    title = f"Reporte PDF - Trabajadores por Zona (Zona ID: {id_zona})"
    subtitle = f"Rango: {fecha_desde} a {fecha_hasta}"
    story.append(Paragraph(title, styles["Title"]))
    story.append(Paragraph(subtitle, styles["Normal"]))
    story.append(Spacer(1, 10))

    data = [[
        "Fecha/Hora", "Zona", "Código", "Cédula", "Nombre", "Correo", "Teléfono",
        "Cumple", "Detalle", "Observaciones"
    ]]

    for r in rows:
        fecha_hora = r.fecha_hora.strftime("%Y-%m-%d %H:%M:%S") if r.fecha_hora else ""
        nombre_full = f"{r.nombre} {r.apellido}"
        cumple = "✅ Cumple" if r.cumple_epp else "❌ No cumple"
        detalle = r.detalle_fallo or ("Cumple EPP" if r.cumple_epp else "Incumplimiento")
        obs = r.observaciones or ""
        data.append([
            fecha_hora,
            r.nombreZona or "",
            r.codigo_trabajador or "",
            r.cedula or "",
            nombre_full,
            r.correo or "",
            r.telefono or "",
            cumple,
            detalle,
            obs
        ])

    table = Table(data, repeatRows=1)
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.black),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("ALIGN", (0, 0), (-1, 0), "CENTER"),
    ]))

    story.append(table)
    doc.build(story)

    return buffer.getvalue()


# -----------------------------
# 3.4) EXCEL: Asistencia por zona y rango
# -----------------------------
def generar_excel_asistencia(
    db: Session,
    id_empresa: int,
    id_zona: int,
    fecha_desde: str,
    fecha_hasta: str,
) -> bytes:
    d = _parse_date(fecha_desde)
    h = _end_of_day(_parse_date(fecha_hasta))

    rows = (
        db.query(
            RegistroAsistencia.fecha_hora,
            Zona.nombreZona,
            Trabajador.codigo_trabajador,
            Persona.cedula,
            Persona.nombre,
            Persona.apellido,
            RegistroAsistencia.cumple_epp,
            EvidenciaFallo.detalle_fallo,
        )
        .join(Zona, Zona.id_Zona == RegistroAsistencia.id_zona)
        .join(Trabajador, Trabajador.id_trabajador == RegistroAsistencia.id_trabajador)
        .join(Persona, Persona.id_persona == Trabajador.id_persona_trabajador)
        .outerjoin(EvidenciaFallo, EvidenciaFallo.id_registro == RegistroAsistencia.id_registro)
        .filter(
            RegistroAsistencia.id_empresa == id_empresa,
            RegistroAsistencia.id_zona == id_zona,
            RegistroAsistencia.fecha_hora >= d,
            RegistroAsistencia.fecha_hora <= h,
        )
        .order_by(RegistroAsistencia.fecha_hora.desc())
        .all()
    )

    wb = Workbook()
    ws = wb.active
    ws.title = "Asistencia"

    headers = ["Fecha/Hora", "Zona", "Código", "Cédula", "Trabajador", "Cumple EPP", "Detalle"]
    ws.append(headers)

    header_font = Font(bold=True)
    for col in range(1, len(headers) + 1):
        cell = ws.cell(row=1, column=col)
        cell.font = header_font
        cell.alignment = Alignment(horizontal="center")

    for r in rows:
        trabajador = f"{r.nombre} {r.apellido}"
        cumple = "CUMPLE" if r.cumple_epp else "NO CUMPLE"
        detalle = r.detalle_fallo or ("Cumple EPP" if r.cumple_epp else "Incumplimiento")
        ws.append([
            r.fecha_hora.strftime("%Y-%m-%d %H:%M:%S") if r.fecha_hora else "",
            r.nombreZona or "",
            r.codigo_trabajador or "",
            r.cedula or "",
            trabajador,
            cumple,
            detalle
        ])

    ws.freeze_panes = "A2"

    # Autosize columns
    for col in range(1, len(headers) + 1):
        max_len = 0
        col_letter = get_column_letter(col)
        for cell in ws[col_letter]:
            value = str(cell.value) if cell.value is not None else ""
            max_len = max(max_len, len(value))
        ws.column_dimensions[col_letter].width = min(max_len + 2, 45)

    stream = io.BytesIO()
    wb.save(stream)
    return stream.getvalue()

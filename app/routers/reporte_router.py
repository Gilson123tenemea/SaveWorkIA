# app/rutas/reporte_router.py
from fastapi import APIRouter, Depends, Query, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
import io
from app.modelos.inspector import Inspector
from app.config import get_db
from app.modelos.registros_asistencia import RegistroAsistencia 
from sqlalchemy import func


from app.esquemas.reporte_esquema import BarsResponse, BarItem, PieResponse, PieItem
from app.servicios.reporte_servicio import (
    registrar_reporte,
    barras_incumplimiento_por_zona,
    barras_cumplimiento_por_zona,
    pastel_epp_mas_cumplido,
    generar_pdf_trabajadores_zona,
    generar_excel_asistencia,
)

router = APIRouter(prefix="/reportes", tags=["Reportes"])


# -----------------------------
# 4.1) BARRAS: Incumplimientos por zona (Inspector)
# -----------------------------
@router.get("/estadisticas/zonas-incumplimiento", response_model=BarsResponse)
def estad_zonas_incumplimiento(
    id_inspector: int = Query(...),
    id_empresa: int = Query(...),
    fecha_desde: str | None = Query(None),
    fecha_hasta: str | None = Query(None),
    db: Session = Depends(get_db),
):
    items = barras_incumplimiento_por_zona(
        db=db,
        id_inspector=id_inspector,
        id_empresa=id_empresa,
        fecha_desde=fecha_desde,
        fecha_hasta=fecha_hasta,
    )

    registrar_reporte(
        db=db,
        tipo_reporte="estadistica_barras_incumplimiento_zona",
        formato="json",
        filtros={
            "id_inspector": id_inspector,
            "id_empresa": id_empresa,
            "fecha_desde": fecha_desde,
            "fecha_hasta": fecha_hasta,
        },
        generado_por="inspector",
        id_empresa=id_empresa,
        id_inspector=id_inspector,
    )

    resp_items = [BarItem(label=z, value=v) for z, v in items]
    total = sum(i.value for i in resp_items)
    return BarsResponse(total=total, items=resp_items)


# -----------------------------
# 4.2) BARRAS: Cumplimientos por zona (Inspector)
# -----------------------------
@router.get("/estadisticas/zonas-cumplimiento", response_model=BarsResponse)
def estad_zonas_cumplimiento(
    id_inspector: int = Query(...),
    id_empresa: int = Query(...),
    fecha_desde: str | None = Query(None),
    fecha_hasta: str | None = Query(None),
    db: Session = Depends(get_db),
):
    items = barras_cumplimiento_por_zona(
        db=db,
        id_inspector=id_inspector,
        id_empresa=id_empresa,
        fecha_desde=fecha_desde,
        fecha_hasta=fecha_hasta,
    )

    registrar_reporte(
        db=db,
        tipo_reporte="estadistica_barras_cumplimiento_zona",
        formato="json",
        filtros={
            "id_inspector": id_inspector,
            "id_empresa": id_empresa,
            "fecha_desde": fecha_desde,
            "fecha_hasta": fecha_hasta,
        },
        generado_por="inspector",
        id_empresa=id_empresa,
        id_inspector=id_inspector,
    )

    resp_items = [BarItem(label=z, value=v) for z, v in items]
    total = sum(i.value for i in resp_items)
    return BarsResponse(total=total, items=resp_items)


# -----------------------------
# 4.3) PASTEL: EPP más cumplido
# -----------------------------
@router.get("/estadisticas/epp-pastel", response_model=PieResponse)
def estad_epp_pastel(
    id_empresa: int = Query(...),
    id_inspector: int | None = Query(None),
    id_zona: int | None = Query(None),
    fecha_desde: str | None = Query(None),
    fecha_hasta: str | None = Query(None),
    db: Session = Depends(get_db),
):
    items = pastel_epp_mas_cumplido(
        db=db,
        id_empresa=id_empresa,
        id_inspector=id_inspector,
        id_zona=id_zona,
        fecha_desde=fecha_desde,
        fecha_hasta=fecha_hasta,
    )

    registrar_reporte(
        db=db,
        tipo_reporte="estadistica_pastel_epp_mas_cumplido",
        formato="json",
        filtros={
            "id_empresa": id_empresa,
            "id_inspector": id_inspector,
            "id_zona": id_zona,
            "fecha_desde": fecha_desde,
            "fecha_hasta": fecha_hasta,
        },
        generado_por="inspector" if id_inspector else "administrador",
        id_empresa=id_empresa,
        id_inspector=id_inspector,
    )

    resp_items = [PieItem(label=lbl, value=v) for lbl, v in items]
    total = sum(i.value for i in resp_items)
    return PieResponse(total=total, items=resp_items)

def obtener_empresa_por_inspector(db: Session, id_inspector: int) -> int:
    inspector = db.query(Inspector).filter(
        Inspector.id_inspector == id_inspector,
        Inspector.borrado == True
    ).first()

    if not inspector:
        raise HTTPException(
            status_code=404,
            detail="Inspector no encontrado"
        )

    return inspector.id_empresa_inspector
def obtener_id_empresa_desde_registros(
    db: Session,
    id_inspector: int,
    id_zona: int,
) -> int:
    # Busca la empresa asociada a registros de ese inspector en esa zona
    id_empresa = (
        db.query(func.max(RegistroAsistencia.id_empresa))
        .filter(
            RegistroAsistencia.id_inspector == id_inspector,
            RegistroAsistencia.id_zona == id_zona,
        )
        .scalar()
    )

    if not id_empresa:
        raise HTTPException(
            status_code=404,
            detail="No hay registros para ese inspector en esa zona (no se pudo determinar la empresa)."
        )

    return int(id_empresa)

# -----------------------------
# 4.4) PDF: Trabajadores por zona (con persona + zona + fechas + cumple/no)
# -----------------------------
@router.get("/pdf/trabajadores-zona")
def reporte_pdf_trabajadores_zona(
    id_inspector: int = Query(...),
    id_zona: int = Query(...),
    fecha_desde: str = Query(...),
    fecha_hasta: str = Query(...),
    db: Session = Depends(get_db),
):
    pdf_bytes = generar_pdf_trabajadores_zona(
        db=db,
        id_inspector=id_inspector,
        id_zona=id_zona,
        fecha_desde=fecha_desde,
        fecha_hasta=fecha_hasta,
    )

    # ✅ Obtener empresa de forma segura sin depender del modelo Inspector
    id_empresa = obtener_id_empresa_desde_registros(db, id_inspector, id_zona)

    registrar_reporte(
        db=db,
        tipo_reporte="pdf_trabajadores_zona",
        formato="pdf",
        filtros={
            "id_inspector": id_inspector,
            "id_zona": id_zona,
            "fecha_desde": fecha_desde,
            "fecha_hasta": fecha_hasta,
        },
        generado_por="inspector",
        id_empresa=id_empresa,      # ✅ ya no falla
        id_inspector=id_inspector,
    )

    filename = f"reporte_trabajadores_zona_{id_zona}_{fecha_desde}_a_{fecha_hasta}.pdf"
    return StreamingResponse(
        io.BytesIO(pdf_bytes),
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


# -----------------------------
# 4.5) EXCEL: Asistencia por zona y rango
# -----------------------------
@router.get("/excel/asistencia")
def reporte_excel_asistencia(
    id_inspector: int = Query(...),  
    id_zona: int = Query(...),
    fecha_desde: str = Query(...),
    fecha_hasta: str = Query(...),
    db: Session = Depends(get_db),
):
    xlsx_bytes = generar_excel_asistencia(
        db=db,
        id_inspector=id_inspector,
        id_zona=id_zona,
        fecha_desde=fecha_desde,
        fecha_hasta=fecha_hasta,
    )

    id_empresa = obtener_empresa_por_inspector(db, id_inspector)

    registrar_reporte(
        db=db,
        tipo_reporte="excel_asistencia",
        formato="excel",
        filtros={
            "id_inspector": id_inspector,
            "id_zona": id_zona,
            "fecha_desde": fecha_desde,
            "fecha_hasta": fecha_hasta,
        },
        generado_por="inspector",
        id_empresa=id_empresa,          # ✅ CLAVE
        id_inspector=id_inspector,
    )

    filename = f"asistencia_zona_{id_zona}_{fecha_desde}_a_{fecha_hasta}.xlsx"
    return StreamingResponse(
        io.BytesIO(xlsx_bytes),
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )

# app/modelos/reporte.py
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.config import Base


class Reporte(Base):
    __tablename__ = "reportes"

    id_reporte = Column(Integer, primary_key=True, index=True)

    # Ej: "estadistica_barras_incumplimiento_zona", "pdf_trabajadores_zona", "excel_asistencia"
    tipo_reporte = Column(String(80), nullable=False)

    # "pdf" | "excel" | "grafico" | "json"
    formato = Column(String(20), nullable=False)

    # JSON como texto: {"id_zona": 3, "desde": "...", "hasta": "..."}
    filtros = Column(Text, nullable=True)

    generado_por = Column(String(30), nullable=False)  # inspector | supervisor | administrador
    fecha_generacion = Column(DateTime, server_default=func.now(), nullable=False)

    # Asociaciones (auditoría)
    id_empresa = Column(Integer, ForeignKey("empresas.id_Empresa"), nullable=False)
    id_inspector = Column(Integer, ForeignKey("inspector.id_inspector"), nullable=True)

    borrado = Column(Boolean, default=True, nullable=False)

    empresa = relationship("Empresa", lazy="joined")
    inspector = relationship("Inspector", lazy="joined")

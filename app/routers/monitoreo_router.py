from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.config import SessionLocal

from app.esquemas.monitoreo_esquema import EmpresaZonasCamarasResponse
from app.servicios.monitoreo_servicio import obtener_zonas_y_camaras_por_empresa

router = APIRouter(prefix="/monitoreo", tags=["Monitoreo"])

# Dependency para DB
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ===============================
# 📌 Obtener zonas + cámaras por empresa
# ===============================
@router.get(
    "/empresa/{empresa_id}/zonas-camaras",
    response_model=EmpresaZonasCamarasResponse
)
def get_zonas_camaras_empresa(empresa_id: int, db: Session = Depends(get_db)):
    return obtener_zonas_y_camaras_por_empresa(db, empresa_id)

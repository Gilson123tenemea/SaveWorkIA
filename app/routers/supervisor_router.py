from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.config import SessionLocal
from app.esquemas.supervisor_esquema import SupervisorPerfilUpdate

from app.esquemas.supervisor_esquema import (
    SupervisorCreate,
    LoginSupervisor,
    SupervisorUpdate,
)
from app.esquemas.empresa_esquema import EmpresaResponse

from app.servicios.supervisor_servicio import (
    crear_supervisor,
    login_supervisor,
    listar_supervisores_activos,
    eliminar_supervisor,
    editar_supervisor,
    obtener_empresa_por_supervisor,
    obtener_perfil_supervisor,
    actualizar_perfil_supervisor
)

router = APIRouter(prefix="/supervisores", tags=["Supervisores"])


# ============================
# DEPENDENCIA BASE DE DATOS
# ============================
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ============================
# REGISTRO
# ============================
@router.post("/registrar")
def registrar_supervisor(request: SupervisorCreate, db: Session = Depends(get_db)):
    return crear_supervisor(db, request)


# ============================
# LOGIN
# ============================
@router.post("/login")
def login_supervisor_endpoint(request: LoginSupervisor, db: Session = Depends(get_db)):
    return login_supervisor(db, request)


# ============================
# LISTAR
# ============================
@router.get("/listar")
def listar_supervisores(db: Session = Depends(get_db)):
    return listar_supervisores_activos(db)


# ============================
# ELIMINAR (BORRADO LÓGICO)
# ============================
@router.delete("/eliminar/{id_supervisor}")
def eliminar_supervisor_endpoint(id_supervisor: int, db: Session = Depends(get_db)):
    return eliminar_supervisor(db, id_supervisor)


# ============================
# EDITAR SUPERVISOR (COMPLETO)
# ============================
@router.put("/editar/{id_supervisor}")
def actualizar_supervisor(id_supervisor: int, request: SupervisorUpdate, db: Session = Depends(get_db)):
    return editar_supervisor(db, id_supervisor, request)


# ============================
# OBTENER EMPRESA DEL SUPERVISOR
# ============================
@router.get("/empresa/{id_supervisor}", response_model=EmpresaResponse)
def obtener_empresa(id_supervisor: int, db: Session = Depends(get_db)):
    return obtener_empresa_por_supervisor(db, id_supervisor)


# ============================
# PERFIL COMPLETO DEL SUPERVISOR
# ============================
@router.get("/perfil/{id_supervisor}")
def obtener_perfil(id_supervisor: int, db: Session = Depends(get_db)):
    return obtener_perfil_supervisor(db, id_supervisor)


# ============================
# ACTUALIZAR PERFIL (NOMBRE, CORREO, TELÉFONO)
# ============================
@router.put("/perfil/{id_supervisor}")
async def actualizar_perfil(id_supervisor: int, request: dict, db: Session = Depends(get_db)):
    print("🚨 BODY RECIBIDO:", request)
    return {"ok": True}

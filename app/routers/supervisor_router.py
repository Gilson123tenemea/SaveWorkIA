from fastapi import APIRouter, Depends, Request, BackgroundTasks
from sqlalchemy.orm import Session
from app.config import SessionLocal
from app.esquemas.supervisor_esquema import SupervisorPerfilUpdate
from app.Validaciones.validacion_usuario import correo_disponible
from app.modelos.persona import Persona



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
# VALIDAR CÉDULA (EN TIEMPO REAL)
# ============================
@router.get("/validar-cedula/{cedula}")
def validar_cedula_supervisor(cedula: str, db: Session = Depends(get_db)):
    from app.servicios.supervisor_servicio import cedula_existe_activa
    
    existe = cedula_existe_activa(db, cedula)
    return {"existe": existe}


# ============================
# REGISTRO
# ============================
@router.post("/registrar")
def registrar_supervisor(request: SupervisorCreate, db: Session = Depends(get_db), background_tasks: BackgroundTasks = BackgroundTasks()):
    return crear_supervisor(db, request, background_tasks)


# ============================
# LOGIN
# ============================
@router.post("/login")
async def login_supervisor_endpoint(
    request: LoginSupervisor, 
    db: Session = Depends(get_db),
    http_request: Request = None
):
    # Obtener IP del cliente
    ip_address = http_request.client.host if http_request else None
    return await login_supervisor(db, request, ip_address)


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
def eliminar_supervisor_endpoint(id_supervisor: int, db: Session = Depends(get_db), background_tasks: BackgroundTasks = BackgroundTasks()):
    return eliminar_supervisor(db, id_supervisor, background_tasks)


# ============================
# EDITAR SUPERVISOR (COMPLETO)
# ============================
@router.put("/editar/{id_supervisor}")
def actualizar_supervisor(id_supervisor: int, request: SupervisorUpdate, db: Session = Depends(get_db), background_tasks: BackgroundTasks = BackgroundTasks()):
    return editar_supervisor(db, id_supervisor, request, background_tasks)


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
def actualizar_perfil(
    id_supervisor: int,
    request: SupervisorPerfilUpdate,
    db: Session = Depends(get_db),
    background_tasks: BackgroundTasks = BackgroundTasks()
):
    return actualizar_perfil_supervisor(db, id_supervisor, request, background_tasks)

@router.get("/empresas-disponibles", response_model=list[EmpresaResponse])
def obtener_empresas_sin_supervisor(db: Session = Depends(get_db)):
    from app.servicios.supervisor_servicio import listar_empresas_sin_supervisor
    return listar_empresas_sin_supervisor(db)


@router.get("/validar-correo")
def validar_correo_supervisor(correo: str, db: Session = Depends(get_db)):
    """
    Valida si un correo está disponible (no existe en usuarios ACTIVOS de cualquier rol)
    """
    existe = db.query(Persona).filter(
        Persona.correo == correo,
        Persona.borrado == True  # Solo usuarios activos
    ).first()

    return {
        "disponible": not bool(existe)
    }
# app/rutas/inspectores_ruta.py
from fastapi import APIRouter, Depends, Request, BackgroundTasks
from sqlalchemy.orm import Session
from app.config import SessionLocal
from app.esquemas.inspector_esquema import (
    InspectorCreate,
    LoginInspector,
    ZonaAsignadaInspector,
    InspectorPerfil,
    InspectorPerfilUpdate,
)
from app.servicios import inspector_servicio
from app.esquemas.fcm_token_esquema import FCMTokenRegistro, FCMTokenDelete
from app.servicios import fcm_token_servicio

router = APIRouter(prefix="/inspectores", tags=["Inspectores"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/validar-cedula/{cedula}")
def validar_cedula_supervisor(cedula: str, db: Session = Depends(get_db)):
    from app.servicios.inspector_servicio import cedula_existe_activa
    
    existe = cedula_existe_activa(db, cedula)
    return {"existe": existe}


@router.get("/validar-correo/{correo}")
def validar_correo_disponible(correo: str, db: Session = Depends(get_db)):
    """
    Valida si el correo está disponible (no existe en usuarios activos)
    Responde: {"disponible": true/false, "correo": "..."}
    """
    from app.servicios.inspector_servicio import correo_existe_activo
    existe = correo_existe_activo(db, correo)
    return {
        "disponible": not existe,
        "correo": correo,
        "mensaje": "Correo disponible" if not existe else "Correo ya registrado"
    }


# --- Registrar ---
@router.post("/registrar")
def registrar_inspector(
    request: InspectorCreate, 
    db: Session = Depends(get_db),
    background_tasks: BackgroundTasks = BackgroundTasks()
):
    return inspector_servicio.crear_inspector(db, request, background_tasks)

# --- Listar activos ---
@router.get("/")
def listar_inspectores(db: Session = Depends(get_db)):
    return inspector_servicio.listar_inspectores(db)

# --- Editar ---
@router.put("/{id_inspector}")
def editar_inspector(
    id_inspector: int, 
    request: InspectorCreate, 
    db: Session = Depends(get_db),
    background_tasks: BackgroundTasks = BackgroundTasks()
):
    return inspector_servicio.editar_inspector(db, id_inspector, request, background_tasks)

# --- Borrado lógico ---
@router.delete("/{id_inspector}")
def eliminar_inspector(
    id_inspector: int, 
    db: Session = Depends(get_db),
    background_tasks: BackgroundTasks = BackgroundTasks()
):
    return inspector_servicio.eliminar_inspector(db, id_inspector, background_tasks)

# --- Login ---
@router.post("/login")
async def login_inspector(
    request: LoginInspector, 
    db: Session = Depends(get_db),
    http_request: Request = None
):
    # Obtener IP del cliente
    ip_address = http_request.client.host if http_request else None
    return await inspector_servicio.login_inspector(db, request, ip_address)

@router.get("/supervisor/{id_supervisor}")
def listar_inspectores_por_supervisor(id_supervisor: int, db: Session = Depends(get_db)):
    return inspector_servicio.listar_inspectores_por_supervisor(db, id_supervisor)

@router.get("/zonas/{id_inspector}", response_model=list[ZonaAsignadaInspector])
def obtener_zonas_por_inspector(id_inspector: int, db: Session = Depends(get_db)):
    return inspector_servicio.obtener_zonas_por_inspector(db, id_inspector)

# --- PERFIL DEL INSPECTOR ---
@router.get("/perfil/{id_inspector}", response_model=InspectorPerfil)
def obtener_perfil_inspector(id_inspector: int, db: Session = Depends(get_db)):
    return inspector_servicio.obtener_perfil_inspector(db, id_inspector)


@router.put("/perfil/{id_inspector}")
def actualizar_perfil_inspector(
    id_inspector: int,
    request: InspectorPerfilUpdate,
    db: Session = Depends(get_db),
    background_tasks: BackgroundTasks = BackgroundTasks()
):
    return inspector_servicio.actualizar_perfil_inspector(db, id_inspector, request, background_tasks)

# --- FCM TOKENS ---

@router.post("/{id_inspector}/fcm-token")
def registrar_token_fcm(
    id_inspector: int,
    request: FCMTokenRegistro,
    db: Session = Depends(get_db)
):
 
    return fcm_token_servicio.registrar_token_fcm(db, id_inspector, request)

@router.get("/{id_inspector}/fcm-tokens")
def obtener_tokens_inspector(
    id_inspector: int,
    db: Session = Depends(get_db)
):
  
    return fcm_token_servicio.obtener_tokens_inspector(db, id_inspector)

@router.delete("/{id_inspector}/fcm-token")
def eliminar_token_fcm(
    id_inspector: int,
    request: FCMTokenDelete,
    db: Session = Depends(get_db)
):
 
    return fcm_token_servicio.eliminar_token_fcm(db, id_inspector, request.token_fcm)

@router.post("/{id_inspector}/test-notificacion")
def test_enviar_notificacion(
    id_inspector: int,
    db: Session = Depends(get_db)
):
    """
    🧪 Prueba enviando una notificación
    
    POST /inspectores/1/test-notificacion
    """
    from app.servicios.notificaciones_fcm_servicio import NotificacionesFCMServicio
    
    exito = NotificacionesFCMServicio.enviar_notificacion_inspector(
        db,
        id_inspector,
        titulo="⚠️ Prueba de Notificación",
        cuerpo="Esta es una notificación de prueba desde el backend",
        datos={"tipo": "prueba", "id_inspector": str(id_inspector)}
    )
    
    return {
        "mensaje": "Notificación enviada",
        "exito": exito,
        "id_inspector": id_inspector
    }
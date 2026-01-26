from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session
from app.config import SessionLocal

from app.esquemas.trabajador_esquema import (
    TrabajadorPersonaCreate,
    TrabajadorResponse
)
from app.servicios import trabajador_servicio
from app.esquemas.trabajador_esquema import LoginTrabajador
from app.servicios.trabajador_servicio import login_trabajador

router = APIRouter(prefix="/trabajadores", tags=["Trabajadores"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def obtener_ip_cliente(request: Request) -> str:
    """Extrae la IP del cliente desde el request"""
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0].strip()
    
    real_ip = request.headers.get("X-Real-IP")
    if real_ip:
        return real_ip
    
    return request.client.host if request.client else "unknown"


@router.get("/validar-codigo/{codigo}/empresa/{id_empresa}")
def validar_codigo(codigo: str, id_empresa: int, db: Session = Depends(get_db)):
    from app.servicios.trabajador_servicio import codigo_existe_activo

    existe = codigo_existe_activo(db, codigo, id_empresa)
    return {"existe": existe}


@router.get("/validar-correo/{correo}")
def validar_correo_disponible(correo: str, db: Session = Depends(get_db)):
    from app.servicios.inspector_servicio import correo_existe_activo
    existe = correo_existe_activo(db, correo)
    return {
        "disponible": not existe, 
        "correo": correo,
        "mensaje": "Correo disponible" if not existe else "Correo ya registrado"
    }


@router.post("/", response_model=TrabajadorResponse)
async def crear_trabajador(
    data: TrabajadorPersonaCreate, 
    request: Request,
    db: Session = Depends(get_db)
):
    ip_address = obtener_ip_cliente(request)
    return await trabajador_servicio.crear_trabajador_completo(db, data, ip_address)


@router.get("/validar-correo/{correo}")
def validar_correo_trabajador(correo: str, db: Session = Depends(get_db)):
    from app.servicios.trabajador_servicio import correo_existe_activo

    existe = correo_existe_activo(db, correo)
    return {"existe": existe}


@router.get("/validar-cedula/{cedula}")
def validar_cedula_supervisor(cedula: str, db: Session = Depends(get_db)):
    from app.servicios.trabajador_servicio import cedula_existe_activa
    
    existe = cedula_existe_activa(db, cedula)
    return {"existe": existe}


@router.get("/", response_model=list[TrabajadorResponse])
def listar_trabajadores(db: Session = Depends(get_db)):
    return trabajador_servicio.obtener_trabajadores_completos(db)


@router.post("/login")
async def login(
    data: LoginTrabajador, 
    request: Request,
    db: Session = Depends(get_db)
):
    ip_address = obtener_ip_cliente(request)
    return await login_trabajador(db, data.correo, data.contrasena, ip_address)


@router.get("/{id_trabajador}", response_model=TrabajadorResponse)
def obtener_trabajador(id_trabajador: int, db: Session = Depends(get_db)):
    return trabajador_servicio.obtener_trabajador_completo(db, id_trabajador)


@router.put("/{id_trabajador}", response_model=TrabajadorResponse)
async def editar_trabajador(
    id_trabajador: int, 
    data: TrabajadorPersonaCreate, 
    request: Request,
    db: Session = Depends(get_db)
):
    ip_address = obtener_ip_cliente(request)
    return await trabajador_servicio.editar_trabajador_completo(db, id_trabajador, data, ip_address)


@router.put("/borrar/{id_trabajador}")
async def borrar_trabajador(
    id_trabajador: int, 
    request: Request,
    db: Session = Depends(get_db)
):
    ip_address = obtener_ip_cliente(request)
    return await trabajador_servicio.borrado_logico_trabajador(db, id_trabajador, ip_address)


@router.get("/supervisor/{id_supervisor}", response_model=list[TrabajadorResponse])
def listar_trabajadores_por_supervisor(id_supervisor: int, db: Session = Depends(get_db)):
    return trabajador_servicio.obtener_trabajadores_por_supervisor(db, id_supervisor)


@router.get("/supervisor/{id_supervisor}/no-asignados", response_model=list[TrabajadorResponse])
def listar_trabajadores_no_asignados(id_supervisor: int, db: Session = Depends(get_db)):
    return trabajador_servicio.obtener_trabajadores_no_asignados(db, id_supervisor)


@router.get("/extraer/entrada/camara/{codigo}/empresa/{id_empresa}")
def obtener_trabajador_con_empresa(codigo: str, id_empresa: int, db: Session = Depends(get_db)):
    from app.servicios.trabajador_servicio import extraer_trabajador_codigo_con_camara
    return extraer_trabajador_codigo_con_camara(db, codigo, id_empresa)
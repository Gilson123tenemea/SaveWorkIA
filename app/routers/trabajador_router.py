from fastapi import APIRouter, Depends
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

@router.get("/validar-codigo/{codigo}")
def validar_codigo(codigo: str, db: Session = Depends(get_db)):
    from app.servicios.trabajador_servicio import codigo_existe_activo

    existe = codigo_existe_activo(db, codigo)
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

# --------------------------------------------------
# CREAR PERSONA + TRABAJADOR
# --------------------------------------------------
@router.post("/", response_model=TrabajadorResponse)
def crear_trabajador(data: TrabajadorPersonaCreate, db: Session = Depends(get_db)):
    return trabajador_servicio.crear_trabajador_completo(db, data)

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

# --------------------------------------------------
# LISTAR
# --------------------------------------------------
@router.get("/", response_model=list[TrabajadorResponse])
def listar_trabajadores(db: Session = Depends(get_db)):
    return trabajador_servicio.obtener_trabajadores_completos(db)

@router.post("/login")
def login(data: LoginTrabajador, db: Session = Depends(get_db)):
    return login_trabajador(db, data.correo, data.contrasena)

# --------------------------------------------------
# OBTENER POR ID
# --------------------------------------------------
@router.get("/{id_trabajador}", response_model=TrabajadorResponse)
def obtener_trabajador(id_trabajador: int, db: Session = Depends(get_db)):
    return trabajador_servicio.obtener_trabajador_completo(db, id_trabajador)


# --------------------------------------------------
# EDITAR PERSONA + TRABAJADOR
# --------------------------------------------------
@router.put("/{id_trabajador}", response_model=TrabajadorResponse)
def editar_trabajador(id_trabajador: int, data: TrabajadorPersonaCreate, db: Session = Depends(get_db)):
    return trabajador_servicio.editar_trabajador_completo(db, id_trabajador, data)


# --------------------------------------------------
# BORRADO LÓGICO
# --------------------------------------------------
@router.put("/borrar/{id_trabajador}")
def borrar_trabajador(id_trabajador: int, db: Session = Depends(get_db)):
    return trabajador_servicio.borrado_logico_trabajador(db, id_trabajador)

# --------------------------------------------------
# LISTAR TRABAJADORES DE UN SUPERVISOR
# --------------------------------------------------
@router.get("/supervisor/{id_supervisor}", response_model=list[TrabajadorResponse])
def listar_trabajadores_por_supervisor(id_supervisor: int, db: Session = Depends(get_db)):
    return trabajador_servicio.obtener_trabajadores_por_supervisor(db, id_supervisor)

# --------------------------------------------------
# LISTAR TRABAJADORES DE UN SUPERVISOR NO ASIGNADOS
# --------------------------------------------------
@router.get("/supervisor/{id_supervisor}/no-asignados", response_model=list[TrabajadorResponse])
def listar_trabajadores_no_asignados(id_supervisor: int, db: Session = Depends(get_db)):
    return trabajador_servicio.obtener_trabajadores_no_asignados(db, id_supervisor)

@router.get("/extraer/entrada/camara/{codigo}/empresa/{id_empresa}")
def obtener_trabajador_con_empresa(codigo: str, id_empresa: int, db: Session = Depends(get_db)):
    from app.servicios.trabajador_servicio import extraer_trabajador_codigo_con_camara
    return extraer_trabajador_codigo_con_camara(db, codigo, id_empresa)

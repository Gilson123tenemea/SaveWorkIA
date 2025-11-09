from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.config import SessionLocal
from app.esquemas.camara_esquema import CamaraCreate, CamaraResponse, CamaraUpdate
from app.servicios import camara_servicio

router = APIRouter(prefix="/camaras", tags=["Cámaras"])

# Dependencia para obtener la sesión de BD
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/", response_model=CamaraResponse, status_code=201)
def crear_camara(camara: CamaraCreate, db: Session = Depends(get_db)):
    """
    Crea una nueva cámara en el sistema
    """
    return camara_servicio.crear_camara(db, camara)

@router.get("/", response_model=list[CamaraResponse])
def listar_camaras(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """
    Lista todas las cámaras activas (no eliminadas)
    """
    return camara_servicio.obtener_camaras(db, skip, limit)

@router.get("/zona/{zona_id}", response_model=list[CamaraResponse])
def listar_camaras_por_zona(
    zona_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """
    Lista todas las cámaras de una zona específica
    """
    return camara_servicio.obtener_camaras_por_zona(db, zona_id, skip, limit)

@router.get("/administrador/{administrador_id}", response_model=list[CamaraResponse])
def listar_camaras_por_administrador(
    administrador_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """
    Lista todas las cámaras asignadas a un administrador
    """
    return camara_servicio.obtener_camaras_por_administrador(db, administrador_id, skip, limit)

@router.get("/estado/{estado}", response_model=list[CamaraResponse])
def listar_camaras_por_estado(
    estado: str,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """
    Lista todas las cámaras con un estado específico
    Ejemplos: activa, inactiva, mantenimiento, desconectada
    """
    return camara_servicio.obtener_camaras_por_estado(db, estado, skip, limit)

@router.get("/{camara_id}", response_model=CamaraResponse)
def obtener_camara(camara_id: int, db: Session = Depends(get_db)):
    """
    Obtiene una cámara específica por su ID
    """
    return camara_servicio.obtener_camara_por_id(db, camara_id)

@router.get("/codigo/{codigo}", response_model=CamaraResponse)
def obtener_camara_por_codigo(codigo: str, db: Session = Depends(get_db)):
    """
    Obtiene una cámara específica por su código
    """
    return camara_servicio.obtener_camara_por_codigo(db, codigo)

@router.put("/{camara_id}", response_model=CamaraResponse)
def actualizar_camara(
    camara_id: int,
    camara_update: CamaraUpdate,
    db: Session = Depends(get_db)
):
    """
    Actualiza los datos de una cámara
    """
    return camara_servicio.actualizar_camara(db, camara_id, camara_update)

@router.patch("/{camara_id}/transmision", response_model=CamaraResponse)
def actualizar_ultima_transmision(camara_id: int, db: Session = Depends(get_db)):
    """
    Actualiza la fecha de última transmisión de una cámara a la fecha actual
    """
    return camara_servicio.actualizar_ultima_transmision(db, camara_id)

@router.patch("/{camara_id}/revision", response_model=CamaraResponse)
def actualizar_ultima_revision(camara_id: int, db: Session = Depends(get_db)):
    """
    Actualiza la fecha de última revisión de una cámara a la fecha actual
    """
    return camara_servicio.actualizar_ultima_revision(db, camara_id)

@router.patch("/{camara_id}/estado", response_model=CamaraResponse)
def cambiar_estado_camara(
    camara_id: int,
    nuevo_estado: str = Query(..., description="Nuevo estado de la cámara"),
    db: Session = Depends(get_db)
):
    """
    Cambia el estado de una cámara
    Ejemplos: activa, inactiva, mantenimiento, desconectada
    """
    return camara_servicio.cambiar_estado_camara(db, camara_id, nuevo_estado)

@router.delete("/{camara_id}")
def eliminar_camara(camara_id: int, db: Session = Depends(get_db)):
    """
    Elimina lógicamente una cámara (marca como borrado)
    """
    return camara_servicio.eliminar_camara(db, camara_id)

@router.delete("/{camara_id}/permanente")
def eliminar_camara_permanente(camara_id: int, db: Session = Depends(get_db)):
    """
    Elimina físicamente una cámara de la base de datos
    ⚠️ Esta acción es irreversible
    """
    return camara_servicio.eliminar_camara_permanente(db, camara_id)
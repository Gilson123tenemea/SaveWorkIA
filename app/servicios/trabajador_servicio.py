from sqlalchemy.orm import Session
from app.modelos.trabajador import Trabajador
from app.modelos.persona import Persona
from app.esquemas.trabajador_esquema import TrabajadorPersonaCreate
from fastapi import HTTPException
from app.seguridad.hash_contrasena import encriptar_contrasena, verificar_contrasena
from sqlalchemy.orm import joinedload
from app.modelos.trabajador_zona import TrabajadorZona


# -----------------------------------------------
# CREAR PERSONA + TRABAJADOR
# -----------------------------------------------
def crear_trabajador_completo(db: Session, data: TrabajadorPersonaCreate):

    if db.query(Persona).filter(Persona.cedula == data.persona.cedula).first():
        raise HTTPException(status_code=400, detail="La cédula ya está registrada")

    if db.query(Persona).filter(Persona.correo == data.persona.correo).first():
        raise HTTPException(status_code=400, detail="El correo ya está registrado")

    # Encriptar contraseña
    contrasena_encriptada = encriptar_contrasena(data.persona.contrasena)

    # Crear persona
    persona = Persona(
        cedula=data.persona.cedula,
        nombre=data.persona.nombre,
        apellido=data.persona.apellido,
        telefono=data.persona.telefono,
        correo=data.persona.correo,
        direccion=data.persona.direccion,
        genero=data.persona.genero,
        fecha_nacimiento=data.persona.fecha_nacimiento,
        contrasena=contrasena_encriptada,
        rol="trabajador",
        borrado=True
    )

    db.add(persona)
    db.commit()
    db.refresh(persona)

    # Crear trabajador
    trabajador = Trabajador(
        cargo=data.trabajador.cargo,
        area_trabajo=data.trabajador.area_trabajo,
        implementos_requeridos=data.trabajador.implementos_requeridos,
        estado=data.trabajador.estado,
        codigo_trabajador=data.trabajador.codigo_trabajador,
        id_empresa=data.trabajador.id_empresa,
        id_supervisor_trabajador=data.trabajador.id_supervisor_trabajador,
        id_persona_trabajador=persona.id_persona,
        borrado=True
    )

    db.add(trabajador)
    db.commit()
    db.refresh(trabajador)

    return {
        "id_trabajador": trabajador.id_trabajador,
        "cargo": trabajador.cargo,
        "area_trabajo": trabajador.area_trabajo,
        "implementos_requeridos": trabajador.implementos_requeridos,
        "estado": trabajador.estado,
        "fecharegistro": trabajador.fecharegistro,
        "codigo_trabajador": trabajador.codigo_trabajador,
        "id_empresa": trabajador.id_empresa,
        "id_supervisor_trabajador": trabajador.id_supervisor_trabajador,

        "persona": {
            "id_persona": persona.id_persona,
            "cedula": persona.cedula,
            "nombre": persona.nombre,
            "apellido": persona.apellido,
            "telefono": persona.telefono,
            "correo": persona.correo,
            "direccion": persona.direccion,
            "genero": persona.genero,
            "fecha_nacimiento": persona.fecha_nacimiento,
            "contrasena": persona.contrasena,
            "rol": persona.rol,
            "borrado": persona.borrado
        }
    }


# -----------------------------------------------
# LISTAR TODOS LOS TRABAJADORES
# -----------------------------------------------
def obtener_trabajadores_completos(db: Session):
    return db.query(Trabajador).join(Persona).all()


# -----------------------------------------------
# OBTENER TRABAJADOR POR ID
# -----------------------------------------------
def obtener_trabajador_completo(db: Session, id_trabajador: int):
    return (
        db.query(Trabajador)
        .join(Persona)
        .filter(Trabajador.id_trabajador == id_trabajador)
        .first()
    )


# -----------------------------------------------
# EDITAR PERSONA + TRABAJADOR
# -----------------------------------------------
def editar_trabajador_completo(db: Session, id_trabajador: int, data: TrabajadorPersonaCreate):

    trabajador = db.query(Trabajador).filter(
        Trabajador.id_trabajador == id_trabajador,
        Trabajador.borrado == True
    ).first()

    if not trabajador:
        raise HTTPException(status_code=404, detail="Trabajador no encontrado")

    persona = db.query(Persona).filter(
        Persona.id_persona == trabajador.id_persona_trabajador,
        Persona.borrado == True
    ).first()

    if not persona:
        raise HTTPException(status_code=404, detail="Persona asociada no encontrada")

    # 🔒 Re-encriptar si llega nueva contraseña
    if data.persona.contrasena:
        persona.contrasena = encriptar_contrasena(data.persona.contrasena)

    # --- actualizar persona ---
    persona.cedula = data.persona.cedula
    persona.nombre = data.persona.nombre
    persona.apellido = data.persona.apellido
    persona.telefono = data.persona.telefono
    persona.correo = data.persona.correo
    persona.direccion = data.persona.direccion
    persona.genero = data.persona.genero
    persona.fecha_nacimiento = data.persona.fecha_nacimiento

    # --- actualizar trabajador ---
    trabajador.cargo = data.trabajador.cargo
    trabajador.area_trabajo = data.trabajador.area_trabajo
    trabajador.implementos_requeridos = data.trabajador.implementos_requeridos
    trabajador.estado = data.trabajador.estado
    trabajador.codigo_trabajador = data.trabajador.codigo_trabajador

    db.commit()
    db.refresh(trabajador)
    return trabajador


# -----------------------------------------------
# BORRADO LÓGICO
# -----------------------------------------------
def borrado_logico_trabajador(db: Session, id_trabajador: int):

    trabajador = db.query(Trabajador).filter(Trabajador.id_trabajador == id_trabajador).first()
    if not trabajador:
        raise HTTPException(status_code=404, detail="Trabajador no encontrado")

    persona = db.query(Persona).filter(Persona.id_persona == trabajador.id_persona_trabajador).first()

    trabajador.borrado = False
    if persona:
        persona.borrado = False

    db.commit()

    return {"mensaje": "Trabajador eliminado correctamente"}


# ---------------------------------------------------------
# LISTAR TRABAJADORES POR SUPERVISOR
# ---------------------------------------------------------
def obtener_trabajadores_por_supervisor(db: Session, id_supervisor: int):
    trabajadores = (
        db.query(Trabajador)
        .options(joinedload(Trabajador.persona))
        .filter(
            Trabajador.id_supervisor_trabajador == id_supervisor,
            Trabajador.borrado == True
        )
        .all()
    )
    return trabajadores

# ---------------------------------------------------------
# LISTAR TRABAJADORES POR SUPERVISOR **NO ASIGNADOS A ZONA**
# ---------------------------------------------------------
def obtener_trabajadores_no_asignados(db: Session, id_supervisor: int):

    # Subconsulta → trabajadores YA asignados a zona
    subquery_asignados = (
        db.query(TrabajadorZona.id_trabajador_trabajadorzona)
        .filter(TrabajadorZona.borrado == True)
        .subquery()
    )

    # Consulta principal → trabajadores del supervisor que NO estén en la subconsulta
    trabajadores = (
        db.query(Trabajador)
        .options(joinedload(Trabajador.persona))
        .filter(
            Trabajador.id_supervisor_trabajador == id_supervisor,
            Trabajador.borrado == True,
            ~Trabajador.id_trabajador.in_(subquery_asignados)   # EXCLUIR asignados
        )
        .all()
    )

    return trabajadores

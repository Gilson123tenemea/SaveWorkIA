from sqlalchemy.orm import Session
from app.modelos.trabajador import Trabajador
from app.modelos.persona import Persona
from app.esquemas.trabajador_esquema import TrabajadorPersonaCreate
from fastapi import HTTPException
from app.seguridad.hash_contrasena import encriptar_contrasena, verificar_contrasena
from sqlalchemy.orm import joinedload
from app.modelos.trabajador_zona import TrabajadorZona

from app.Validaciones.validacion_usuario import (
    validar_cedula_ecuatoriana,
    validar_cedula_unica,
    validar_nombre,
    validar_apellido,
    validar_telefono,
    validar_correo_unico,
    validar_direccion,
    validar_genero,
    validar_fecha_nacimiento,
    validar_contrasena,
    validar_cargo,
    validar_area_trabajo,
    validar_implementos,
    validar_estado_trabajador,
    validar_codigo_trabajador,
    validar_correo_formato

)

def codigo_existe_activo(db: Session, codigo: str):
    trabajador = db.query(Trabajador).filter(
        Trabajador.codigo_trabajador == codigo
    ).first()

    return trabajador is not None


def cedula_existe_activa(db: Session, cedula: str):
    persona = db.query(Persona).filter(Persona.cedula == cedula).first()

    if not persona:
        return False  
    if persona.borrado is False:
        return False  
    return True  


def crear_trabajador_completo(db: Session, data: TrabajadorPersonaCreate):

    # =====================================================
    # 1️⃣ VALIDAR FORMATO DE CÉDULA
    # =====================================================
    validar_cedula_ecuatoriana(data.persona.cedula)

    # Buscar persona por cédula
    persona_existente = db.query(Persona).filter(
        Persona.cedula == data.persona.cedula
    ).first()

    # =====================================================
    # 2️⃣ CASO A: PERSONA EXISTE Y ESTÁ ACTIVA (borrado=True)
    # → NO SE PUEDE CREAR DE NUEVO
    # =====================================================
    if persona_existente and persona_existente.borrado is True:
        raise HTTPException(
            status_code=400,
            detail="Ya existe un trabajador activo con esta cédula"
        )

    # =====================================================
    # 3️⃣ CASO B: PERSONA EXISTE PERO ESTÁ INACTIVA (borrado=False)
    # → SE REACTIVA Y SE ACTUALIZAN SUS DATOS
    # =====================================================
    if persona_existente and persona_existente.borrado is False:

        persona = persona_existente

        # --- Validaciones completas ---
        validar_correo_formato(data.persona.correo)
        validar_nombre(data.persona.nombre)
        validar_apellido(data.persona.apellido)
        validar_telefono(data.persona.telefono)
        validar_direccion(data.persona.direccion)
        validar_genero(data.persona.genero)
        validar_fecha_nacimiento(data.persona.fecha_nacimiento)
        validar_contrasena(data.persona.contrasena)

        validar_cargo(data.trabajador.cargo)
        validar_area_trabajo(data.trabajador.area_trabajo)
        validar_implementos(data.trabajador.implementos_requeridos)
        validar_estado_trabajador(data.trabajador.estado)
        validar_codigo_trabajador(data.trabajador.codigo_trabajador)
        validar_codigo_unico(db, data.trabajador.codigo_trabajador)

        # --- Reactivar persona ---
        persona.nombre = data.persona.nombre
        persona.apellido = data.persona.apellido
        persona.telefono = data.persona.telefono
        persona.correo = data.persona.correo
        persona.direccion = data.persona.direccion
        persona.genero = data.persona.genero
        persona.fecha_nacimiento = data.persona.fecha_nacimiento
        persona.contrasena = encriptar_contrasena(data.persona.contrasena)
        persona.rol = "trabajador"
        persona.borrado = True  # <-- REACTIVADO

        # Buscar trabajador asociado
        trabajador = db.query(Trabajador).filter(
            Trabajador.id_persona_trabajador == persona.id_persona
        ).first()

        # Si trabajador existía → reactivarlo y actualizarlo
        if trabajador:
            trabajador.cargo = data.trabajador.cargo
            trabajador.area_trabajo = data.trabajador.area_trabajo
            trabajador.implementos_requeridos = data.trabajador.implementos_requeridos
            trabajador.estado = data.trabajador.estado
            trabajador.codigo_trabajador = data.trabajador.codigo_trabajador
            trabajador.id_empresa = data.trabajador.id_empresa
            trabajador.id_supervisor_trabajador = data.trabajador.id_supervisor_trabajador
            trabajador.borrado = True  # <-- REACTIVADO

        else:
            # Si NO existía → crear nuevo trabajador con misma persona
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

        return trabajador
           

    # =====================================================
    # 4️⃣ CASO C: PERSONA NO EXISTE → CREAR REGISTRO NUEVO
    # =====================================================

    # Validaciones persona NUEVA
    validar_cedula_unica(db, data.persona.cedula)
    validar_correo_unico(db, data.persona.correo)
    validar_nombre(data.persona.nombre)
    validar_apellido(data.persona.apellido)
    validar_telefono(data.persona.telefono)
    validar_direccion(data.persona.direccion)
    validar_genero(data.persona.genero)
    validar_fecha_nacimiento(data.persona.fecha_nacimiento)
    validar_contrasena(data.persona.contrasena)

    # Validaciones trabajador NUEVO
    validar_cargo(data.trabajador.cargo)
    validar_area_trabajo(data.trabajador.area_trabajo)
    validar_implementos(data.trabajador.implementos_requeridos)
    validar_estado_trabajador(data.trabajador.estado)
    validar_codigo_trabajador(data.trabajador.codigo_trabajador)
    validar_codigo_unico(db, data.trabajador.codigo_trabajador)

    # Crear persona nueva
    persona = Persona(
        cedula=data.persona.cedula,
        nombre=data.persona.nombre,
        apellido=data.persona.apellido,
        telefono=data.persona.telefono,
        correo=data.persona.correo,
        direccion=data.persona.direccion,
        genero=data.persona.genero,
        fecha_nacimiento=data.persona.fecha_nacimiento,
        contrasena=encriptar_contrasena(data.persona.contrasena),
        rol="trabajador",
        borrado=True
    )
    db.add(persona)
    db.commit()
    db.refresh(persona)

    # Crear trabajador nuevo
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

    return trabajador
# -----------------------------------------------
# LISTAR TODOS LOS TRABAJADORES
# -----------------------------------------------
def obtener_trabajadores_completos(db: Session):
    return db.query(Trabajador).join(Persona).all()

def validar_codigo_unico(db: Session, codigo: str):
    existe = db.query(Trabajador).filter(
        Trabajador.codigo_trabajador == codigo,
        Trabajador.borrado == True
    ).first()

    if existe:
        raise HTTPException(
            status_code=400,
            detail="Ya existe un trabajador activo con este código"
        )

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

    # ------------------------------
    # 1️⃣ Obtener trabajador + persona
    # ------------------------------
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

    # ------------------------------
    # 2️⃣ VALIDACIONES PERSONA
    # ------------------------------

    # Cedula NO se cambia → No validar unicidad
    validar_nombre(data.persona.nombre)
    validar_apellido(data.persona.apellido)
    validar_telefono(data.persona.telefono)
    validar_direccion(data.persona.direccion)
    validar_genero(data.persona.genero)
    validar_fecha_nacimiento(data.persona.fecha_nacimiento)

    # Validar correo único si cambió
    if data.persona.correo != persona.correo:
        validar_correo_formato(data.persona.correo)
        validar_correo_unico(db, data.persona.correo)

    # Validar contraseña solo si viene una nueva
    if data.persona.contrasena:
        persona.contrasena = encriptar_contrasena(data.persona.contrasena)

    # ------------------------------
    # 3️⃣ VALIDACIONES TRABAJADOR
    # ------------------------------
    validar_cargo(data.trabajador.cargo)
    validar_area_trabajo(data.trabajador.area_trabajo)
    validar_implementos(data.trabajador.implementos_requeridos)
    validar_estado_trabajador(data.trabajador.estado)

    # Validar código EMP-XXX solo si cambió
    if data.trabajador.codigo_trabajador != trabajador.codigo_trabajador:
        validar_codigo_trabajador(data.trabajador.codigo_trabajador)
        validar_codigo_unico(db, data.trabajador.codigo_trabajador)

    # ------------------------------
    # 4️⃣ Actualizar PERSONA
    # ------------------------------
    persona.nombre = data.persona.nombre
    persona.apellido = data.persona.apellido
    persona.telefono = data.persona.telefono
    persona.correo = data.persona.correo
    persona.direccion = data.persona.direccion
    persona.genero = data.persona.genero
    persona.fecha_nacimiento = data.persona.fecha_nacimiento

    # ------------------------------
    # 5️⃣ Actualizar TRABAJADOR
    # ------------------------------
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

def cedula_existe_activa(db: Session, cedula: str):
    persona = db.query(Persona).filter(Persona.cedula == cedula).first()

    if not persona:
        return False  # No existe → libre para usar

    # Existe pero está inactiva (borrado = False)
    if persona.borrado is False:
        return False  # Se puede volver a usar

    # Existe y está activa (borrado = True)
    return True  # No se puede usar

def correo_existe_activo(db: Session, correo: str):
    persona = db.query(Persona).filter(Persona.correo == correo).first()

    if not persona:
        return False  # No existe → libre para usar

    # Existe pero está INACTIVA (borrado=False) → se puede usar
    if persona.borrado is False:
        return False

    # Existe y está ACTIVA (borrado=True) → no se puede usar
    return True

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

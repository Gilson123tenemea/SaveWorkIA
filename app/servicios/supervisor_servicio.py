from sqlalchemy.orm import Session
from fastapi import HTTPException, status
import base64 
from datetime import date
from app.modelos.empresa_modelo import Empresa
from app.modelos.supervisor import Supervisor
from app.modelos.persona import Persona
from app.modelos.supervisor import Supervisor
from app.esquemas.supervisor_esquema import SupervisorCreate, LoginSupervisor, SupervisorUpdate
from app.seguridad.hash_contrasena import encriptar_contrasena, verificar_contrasena

from app.Validaciones.validacion_usuario import (
    validar_cedula_ecuatoriana,
    validar_cedula_unica,
    validar_nombre,
    validar_apellido,
    validar_telefono,
    validar_correo_formato,
    validar_correo_unico,
    validar_direccion,
    validar_genero,
    validar_fecha_nacimiento,
    validar_especialidad,
    validar_experiencia,
    validar_contrasena
)

def crear_supervisor(db: Session, datos: SupervisorCreate):

    # ========================================================
    # 1️⃣ VALIDAR QUE LA EMPRESA NO TENGA YA UN SUPERVISOR ACTIVO
    # ========================================================
    supervisor_existente = db.query(Supervisor).filter(
        Supervisor.id_empresa_supervisor == datos.id_empresa_supervisor,
        Supervisor.borrado == True
    ).first()

    if supervisor_existente:
        raise HTTPException(
            status_code=400,
            detail="Esta empresa ya tiene un supervisor asignado"
        )

    # ========================================================
    # 2️⃣ BUSCAR PERSONA POR CÉDULA (ACTIVA O INACTIVA)
    # ========================================================
    persona_existente = db.query(Persona).filter(
        Persona.cedula == datos.persona.cedula
    ).first()

    # ========================================================
    # 3️⃣ SI EXISTE Y ESTÁ ACTIVA → NO PERMITIR DUPLICADOS
    # ========================================================
    if persona_existente and persona_existente.borrado is True:
        raise HTTPException(
            status_code=400,
            detail="Ya existe una persona activa con esta cédula"
        )

    # ========================================================
    # 4️⃣ SI EXISTE Y ESTÁ INACTIVA → REACTIVAR
    # ========================================================
    if persona_existente and persona_existente.borrado is False:

        # 🔄 Reactivar PERSONA
        persona_existente.nombre = datos.persona.nombre
        persona_existente.apellido = datos.persona.apellido
        persona_existente.telefono = datos.persona.telefono
        persona_existente.correo = datos.persona.correo
        persona_existente.direccion = datos.persona.direccion
        persona_existente.genero = datos.persona.genero
        persona_existente.fecha_nacimiento = datos.persona.fecha_nacimiento
        persona_existente.contrasena = encriptar_contrasena(datos.persona.contrasena)
        persona_existente.rol = "supervisor"
        persona_existente.borrado = True  # ACTIVAR

        # 🔄 Reactivar SUPERVISOR (si existía)
        supervisor = db.query(Supervisor).filter(
            Supervisor.id_persona_supervisor == persona_existente.id_persona
        ).first()

        if supervisor:
            supervisor.especialidad_seguridad = datos.especialidad_seguridad
            supervisor.experiencia = datos.experiencia
            supervisor.id_empresa_supervisor = datos.id_empresa_supervisor
            supervisor.borrado = True
        else:
            # Si no tenía supervisor antes, se crea nuevo
            nuevo_supervisor = Supervisor(
                especialidad_seguridad=datos.especialidad_seguridad,
                experiencia=datos.experiencia,
                id_persona_supervisor=persona_existente.id_persona,
                id_empresa_supervisor=datos.id_empresa_supervisor,
                borrado=True
            )
            db.add(nuevo_supervisor)

        db.commit()

        return {
            "mensaje": "Supervisor reactivado correctamente",
            "id_persona": persona_existente.id_persona
        }

    # ========================================================
    # 5️⃣ SI NO EXISTE → CREAR NORMAL
    # ========================================================
    validar_cedula_ecuatoriana(datos.persona.cedula)
    validar_cedula_unica(db, datos.persona.cedula)
    validar_correo_formato(datos.persona.correo)
    validar_correo_unico(db, datos.persona.correo)

    contrasena_encriptada = encriptar_contrasena(datos.persona.contrasena)

    nueva_persona = Persona(
        cedula=datos.persona.cedula,
        nombre=datos.persona.nombre,
        apellido=datos.persona.apellido,
        telefono=datos.persona.telefono,
        correo=datos.persona.correo,
        direccion=datos.persona.direccion,
        genero=datos.persona.genero,
        fecha_nacimiento=datos.persona.fecha_nacimiento,
        contrasena=contrasena_encriptada,
        rol="supervisor",
        borrado=True
    )
    db.add(nueva_persona)
    db.commit()
    db.refresh(nueva_persona)

    nuevo_supervisor = Supervisor(
        especialidad_seguridad=datos.especialidad_seguridad,
        experiencia=datos.experiencia,
        id_persona_supervisor=nueva_persona.id_persona,
        id_empresa_supervisor=datos.id_empresa_supervisor,
        borrado=True
    )
    db.add(nuevo_supervisor)
    db.commit()
    db.refresh(nuevo_supervisor)

    return {
        "mensaje": "Supervisor registrado correctamente",
        "id_supervisor": nuevo_supervisor.id_supervisor,
        "id_persona": nueva_persona.id_persona
    }

# ======================================================
# 🔎 VALIDAR CÉDULA — CONSULTA SI EXISTE Y ESTÁ ACTIVA
# ======================================================
def cedula_existe_activa(db: Session, cedula: str):
    persona = db.query(Persona).filter(Persona.cedula == cedula).first()

    if not persona:
        return False  # No existe → libre para usar

    # Existe pero está inactiva (borrado = False)
    if persona.borrado is False:
        return False  # Se puede volver a usar

    # Existe y está activa (borrado = True)
    return True  # No se puede usar

# --- Listar supervisores activos (borrado=True) ---
def listar_supervisores_activos(db: Session):
    supervisores = (
        db.query(Supervisor, Persona)
        .join(Persona, Supervisor.id_persona_supervisor == Persona.id_persona)
        .filter(Supervisor.borrado == True, Persona.borrado == True)
        .all()
    )

    resultado = []
    for supervisor, persona in supervisores:
        resultado.append({
            "id_supervisor": supervisor.id_supervisor,
            "id_persona": persona.id_persona,
            "cedula": persona.cedula,
            "nombre": persona.nombre,
            "apellido": persona.apellido,
            "telefono": persona.telefono,
            "correo": persona.correo,
            "direccion": persona.direccion,
            "genero": persona.genero,
            "fecha_nacimiento": persona.fecha_nacimiento,
            "especialidad_seguridad": supervisor.especialidad_seguridad,
            "experiencia": supervisor.experiencia,
            "id_empresa_supervisor": supervisor.id_empresa_supervisor,
            "borrado": supervisor.borrado
        })
    return resultado


# --- Eliminado lógico de supervisor ---
def eliminar_supervisor(db: Session, id_supervisor: int):
    supervisor = db.query(Supervisor).filter(Supervisor.id_supervisor == id_supervisor).first()
    if not supervisor:
        raise HTTPException(status_code=404, detail="Supervisor no encontrado")

    persona = db.query(Persona).filter(Persona.id_persona == supervisor.id_persona_supervisor).first()

    supervisor.borrado = False
    if persona:
        persona.borrado = False

    db.commit()
    return {"mensaje": "Supervisor eliminado lógicamente con éxito"}

def login_supervisor(db: Session, datos: LoginSupervisor):
    # Buscar la persona
    persona = db.query(Persona).filter(Persona.correo == datos.correo).first()

    if not persona:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Correo o contraseña incorrectos"
        )

    if not persona.borrado:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Usuario inactivo o sin permisos"
        )

    # Validar contraseña
    if not verificar_contrasena(datos.contrasena, persona.contrasena):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Correo o contraseña incorrectos"
        )

    # Buscar supervisor activo
    supervisor = db.query(Supervisor).filter(
        Supervisor.id_persona_supervisor == persona.id_persona,
        Supervisor.borrado == True
    ).first()

    if not supervisor:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="El usuario no es supervisor"
        )

    # ✔️ SALIDA CORRECTA CON EMPRESA
    return {
        "mensaje": "Inicio de sesión exitoso",
        "id_supervisor": supervisor.id_supervisor,
        "id_empresa_supervisor": supervisor.id_empresa_supervisor,  # 👈 NECESARIO
        "nombre": persona.nombre,
        "correo": persona.correo,
        "rol": persona.rol
    }


def editar_supervisor(db: Session, id_supervisor: int, datos: SupervisorUpdate):

    supervisor = db.query(Supervisor).filter(
        Supervisor.id_supervisor == id_supervisor,
        Supervisor.borrado == True
    ).first()

    if not supervisor:
        raise HTTPException(status_code=404, detail="Supervisor no encontrado o inactivo")

    persona = db.query(Persona).filter(
        Persona.id_persona == supervisor.id_persona_supervisor,
        Persona.borrado == True
    ).first()

    if not persona:
        raise HTTPException(status_code=404, detail="Persona asociada no encontrada o inactiva")

    # --- VALIDACIONES PERSONA ---
    validar_cedula_ecuatoriana(datos.persona.cedula)

    # Evitar que su propia cédula marque duplicado
    if datos.persona.cedula != persona.cedula:
        validar_cedula_unica(db, datos.persona.cedula)

    validar_nombre(datos.persona.nombre)
    validar_apellido(datos.persona.apellido)
    validar_telefono(datos.persona.telefono)

    validar_correo_formato(datos.persona.correo)

    if datos.persona.correo != persona.correo:
        validar_correo_unico(db, datos.persona.correo)

    validar_direccion(datos.persona.direccion)
    validar_genero(datos.persona.genero)
    validar_fecha_nacimiento(datos.persona.fecha_nacimiento)

    # --- VALIDACIONES SUPERVISOR ---
    validar_especialidad(datos.especialidad_seguridad)
    validar_experiencia(datos.experiencia)

    # --- VALIDACIÓN DE CONTRASEÑA SOLO SI SE ENVÍA ---
    if datos.persona.contrasena and datos.persona.contrasena.strip() != "":
        validar_contrasena(datos.persona.contrasena)
        persona.contrasena = encriptar_contrasena(datos.persona.contrasena)

    # --- Actualizar datos de persona ---
    persona.cedula = datos.persona.cedula
    persona.nombre = datos.persona.nombre
    persona.apellido = datos.persona.apellido
    persona.telefono = datos.persona.telefono
    persona.correo = datos.persona.correo
    persona.direccion = datos.persona.direccion
    persona.genero = datos.persona.genero
    persona.fecha_nacimiento = datos.persona.fecha_nacimiento

    # --- Actualizar datos de supervisor ---
    supervisor.especialidad_seguridad = datos.especialidad_seguridad
    supervisor.experiencia = datos.experiencia

    db.commit()
    db.refresh(supervisor)
    db.refresh(persona)

    return {
        "mensaje": "Supervisor actualizado correctamente",
        "id_supervisor": supervisor.id_supervisor,
        "nombre": persona.nombre,
        "apellido": persona.apellido,
        "correo": persona.correo,
        "especialidad_seguridad": supervisor.especialidad_seguridad,
        "experiencia": supervisor.experiencia
    }

def obtener_empresa_por_supervisor(db: Session, id_supervisor: int):
    # Buscar supervisor
    supervisor = db.query(Supervisor).filter(
        Supervisor.id_supervisor == id_supervisor,
        Supervisor.borrado == True
    ).first()

    if not supervisor:
        raise HTTPException(status_code=404, detail="Supervisor no encontrado o inactivo")

    # Buscar empresa asociada
    empresa = db.query(Empresa).filter(
        Empresa.id_Empresa == supervisor.id_empresa_supervisor,
        Empresa.borrado == True
    ).first()

    if not empresa:
        raise HTTPException(status_code=404, detail="Empresa no encontrada o inactiva")

    return empresa

def obtener_perfil_supervisor(db: Session, id_supervisor: int):
    supervisor = db.query(Supervisor).filter(
        Supervisor.id_supervisor == id_supervisor,
        Supervisor.borrado == True
    ).first()

    if not supervisor:
        raise HTTPException(404, "Supervisor no encontrado")

    persona = db.query(Persona).filter(
        Persona.id_persona == supervisor.id_persona_supervisor
    ).first()

    if not persona:
        raise HTTPException(404, "Persona no encontrada")

    empresa = db.query(Empresa).filter(
        Empresa.id_Empresa == supervisor.id_empresa_supervisor
    ).first()

    return {
        "id_supervisor": supervisor.id_supervisor,
        "id_persona": persona.id_persona,
        "nombre": persona.nombre,
        "apellido": persona.apellido,
        "telefono": persona.telefono,
        "correo": persona.correo,
        "direccion": persona.direccion,
        "genero": persona.genero,
        "fecha_nacimiento": persona.fecha_nacimiento.isoformat(),
        "foto": base64.b64encode(persona.foto).decode() if persona.foto else None,
        "especialidad_seguridad": supervisor.especialidad_seguridad,
        "experiencia": supervisor.experiencia,
        "empresa": {
            "nombre": empresa.nombreEmpresa,
            "ruc": empresa.ruc,
            "direccion": empresa.direccion,
            "telefono": empresa.telefono,
        }
    }


def actualizar_perfil_supervisor(db: Session, id_supervisor: int, datos):
    supervisor = db.query(Supervisor).filter(
        Supervisor.id_supervisor == id_supervisor,
        Supervisor.borrado == True
    ).first()

    if not supervisor:
        raise HTTPException(status_code=404, detail="Supervisor no encontrado")

    persona = db.query(Persona).filter(
        Persona.id_persona == supervisor.id_persona_supervisor,
        Persona.borrado == True
    ).first()

    if not persona:
        raise HTTPException(status_code=404, detail="Persona no encontrada")

    # Validar correo repetido
    correo_existente = db.query(Persona).filter(
        Persona.correo == datos.correo,
        Persona.id_persona != persona.id_persona
    ).first()

    if correo_existente:
        raise HTTPException(400, "El correo ya está en uso")

    # Actualizar campos editables
    persona.nombre = datos.nombre
    persona.correo = datos.correo
    persona.telefono = datos.telefono

    db.commit()
    db.refresh(persona)

    return {
        "mensaje": "Perfil actualizado correctamente",
        "nombre": persona.nombre,
        "correo": persona.correo,
        "telefono": persona.telefono
    }

def listar_empresas_sin_supervisor(db: Session):
    # Empresas activas
    empresas = db.query(Empresa).filter(Empresa.borrado == True).all()

    empresas_disponibles = []

    for empresa in empresas:
        supervisor = db.query(Supervisor).filter(
            Supervisor.id_empresa_supervisor == empresa.id_Empresa,
            Supervisor.borrado == True
        ).first()

        if not supervisor:  # ⇦ ESTA empresa no tiene supervisor asignado
            empresas_disponibles.append(empresa)

    return empresas_disponibles

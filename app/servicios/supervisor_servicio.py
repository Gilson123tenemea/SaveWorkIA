from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from datetime import date

from app.modelos.persona import Persona
from app.modelos.supervisor import Supervisor
from app.esquemas.supervisor_esquema import SupervisorCreate, LoginSupervisor, SupervisorUpdate
from app.seguridad.hash_contrasena import encriptar_contrasena, verificar_contrasena


# --- Crear supervisor + persona ---
def crear_supervisor(db: Session, datos: SupervisorCreate):
    if db.query(Persona).filter(Persona.cedula == datos.persona.cedula).first():
        raise HTTPException(status_code=400, detail="La cédula ya está registrada")
    if db.query(Persona).filter(Persona.correo == datos.persona.correo).first():
        raise HTTPException(status_code=400, detail="El correo ya está registrado")

    # 🔒 Encriptar la contraseña
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
        "id_supervisor": nuevo_supervisor.id_supervisor,
        "id_persona": nueva_persona.id_persona,
        "nombre": nueva_persona.nombre,
        "apellido": nueva_persona.apellido,
        "correo": nueva_persona.correo,
        "especialidad_seguridad": nuevo_supervisor.especialidad_seguridad,
        "experiencia": nuevo_supervisor.experiencia,
        "borrado": nuevo_supervisor.borrado
    }

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
    # Buscar la persona activa
    persona = db.query(Persona).filter(Persona.correo == datos.correo).first()

    if not persona:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Correo o contraseña incorrectos"
        )

    # Validar si está activo
    if not persona.borrado:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Usuario inactivo o sin permisos"
        )

    # Validar la contraseña
    if not verificar_contrasena(datos.contrasena, persona.contrasena):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Correo o contraseña incorrectos"
        )

    # Validar si es supervisor activo
    supervisor = db.query(Supervisor).filter(
        Supervisor.id_persona_supervisor == persona.id_persona,
        Supervisor.borrado == True
    ).first()

    if not supervisor:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="El usuario no es supervisor"
        )

    # Respuesta exitosa
    return {
        "mensaje": "Inicio de sesión exitoso",
        "id_supervisor": supervisor.id_supervisor,
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

    # 🔒 Si se envía una nueva contraseña, encriptarla
    if datos.persona.contrasena:
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

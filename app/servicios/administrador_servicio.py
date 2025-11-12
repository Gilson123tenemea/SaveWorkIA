from sqlalchemy.orm import Session
from datetime import date
from fastapi import HTTPException, status

from app.modelos.persona import Persona
from app.modelos.administrador import Administrador
from app.esquemas.administrador_esquema import AdministradorCreate, LoginAdministrador
from app.seguridad.hash_contrasena import encriptar_contrasena, verificar_contrasena  # ✅ Importamos el helper

# --- Crear administrador + persona ---
def crear_administrador(db: Session, datos: AdministradorCreate):
    if db.query(Persona).filter(Persona.cedula == datos.persona.cedula).first():
        raise HTTPException(status_code=400, detail="La cédula ya está registrada")
    if db.query(Persona).filter(Persona.correo == datos.persona.correo).first():
        raise HTTPException(status_code=400, detail="El correo ya está registrado")

    # 🔒 Encriptar la contraseña antes de guardar
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
        contrasena=contrasena_encriptada,  # ✅ Se guarda encriptada
        rol="admin",
        borrado=True
    )
    db.add(nueva_persona)
    db.commit()
    db.refresh(nueva_persona)

    nuevo_admin = Administrador(
        ultima_conexion=datos.ultima_conexion,
        fechaRegistroSistema=date.today(),
        borrado=True,
        id_persona_administrador=nueva_persona.id_persona
    )
    db.add(nuevo_admin)
    db.commit()
    db.refresh(nuevo_admin)

    return {
        "id_administrador": nuevo_admin.id_administrador,
        "id_persona": nueva_persona.id_persona,
        "nombre": nueva_persona.nombre,
        "apellido": nueva_persona.apellido,
        "correo": nueva_persona.correo,
        "fechaRegistroSistema": nuevo_admin.fechaRegistroSistema,
        "borrado": nuevo_admin.borrado
    }

def login_administrador(db: Session, datos: LoginAdministrador):
    # 🔍 Buscar persona por correo
    persona = db.query(Persona).filter(Persona.correo == datos.correo).first()

    if not persona:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Correo o contraseña incorrectos"
        )

    # ⚠️ Verificar si está activa
    if not persona.borrado:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Usuario inactivo o sin permisos"
        )

    # 🔒 Verificar contraseña
    if not verificar_contrasena(datos.contrasena, persona.contrasena):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Correo o contraseña incorrectos"
        )

    # 🧩 Verificar si la persona tiene registro como administrador
    admin = db.query(Administrador).filter(
        Administrador.id_persona_administrador == persona.id_persona,
        Administrador.borrado == True
    ).first()

    if not admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="El usuario no es administrador"
        )

    # 🕒 Actualizar fecha de última conexión
    admin.ultima_conexion = date.today()
    db.commit()

    # ✅ Login exitoso
    return {
        "mensaje": "Inicio de sesión exitoso",
        "id_administrador": admin.id_administrador,
        "nombre": persona.nombre,
        "correo": persona.correo,
        "role": persona.rol,
        "ultima_conexion": admin.ultima_conexion
    }

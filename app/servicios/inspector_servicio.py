from sqlalchemy.orm import Session
from datetime import date
from fastapi import HTTPException, status

from app.modelos.persona import Persona
from app.modelos.inspector import Inspector
from app.modelos.registrosupervisorinspector import RegistroSupervisorInspector
from app.esquemas.inspector_esquema import InspectorCreate, LoginInspector
from app.seguridad.hash_contrasena import encriptar_contrasena, verificar_contrasena

# --- Crear Inspector (Persona + Inspector + RegistroSupervisorInspector) ---
def crear_inspector(db: Session, datos: InspectorCreate):
    # Validar duplicados
    if db.query(Persona).filter(Persona.cedula == datos.persona.cedula).first():
        raise HTTPException(status_code=400, detail="La cédula ya está registrada")
    if db.query(Persona).filter(Persona.correo == datos.persona.correo).first():
        raise HTTPException(status_code=400, detail="El correo ya está registrado")

    # Encriptar contraseña
    contrasena_encriptada = encriptar_contrasena(datos.persona.contrasena)

    # Crear Persona
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
        rol="inspector",
        borrado=True
    )
    db.add(nueva_persona)
    db.commit()
    db.refresh(nueva_persona)

    # Crear Inspector
    nuevo_inspector = Inspector(
        zona_asignada=datos.zona_asignada,
        frecuenciaVisita=datos.frecuenciaVisita,
        id_persona_inspector=nueva_persona.id_persona,
        borrado=True
    )
    db.add(nuevo_inspector)
    db.commit()
    db.refresh(nuevo_inspector)

    # Crear RegistroSupervisorInspector
    nuevo_registro = RegistroSupervisorInspector(
        id_supervisor_registro=datos.id_supervisor_registro,
        id_inspector_registro=nuevo_inspector.id_inspector,
        fecha_asignacion=date.today(),
        borrado=True
    )
    db.add(nuevo_registro)
    db.commit()
    db.refresh(nuevo_registro)

    return {
        "id_inspector": nuevo_inspector.id_inspector,
        "id_persona": nueva_persona.id_persona,
        "nombre": nueva_persona.nombre,
        "apellido": nueva_persona.apellido,
        "correo": nueva_persona.correo,
        "zona_asignada": nuevo_inspector.zona_asignada,
        "frecuenciaVisita": nuevo_inspector.frecuenciaVisita,
        "fecha_asignacion": nuevo_registro.fecha_asignacion,
        "borrado": nuevo_inspector.borrado
    }

# --- Listar solo activos ---
def listar_inspectores(db: Session):
    inspectores = (
        db.query(Inspector, Persona)
        .join(Persona, Persona.id_persona == Inspector.id_persona_inspector)
        .filter(Inspector.borrado == True)
        .all()
    )

    resultado = []
    for inspector, persona in inspectores:
        resultado.append({
            "id_inspector": inspector.id_inspector,
            "id_persona": persona.id_persona,
            "cedula": persona.cedula,
            "nombre": persona.nombre,
            "apellido": persona.apellido,
            "telefono": persona.telefono,
            "correo": persona.correo,
            "direccion": persona.direccion,        # ➜ AGREGADO
            "genero": persona.genero,              # ➜ AGREGADO
            "fecha_nacimiento": persona.fecha_nacimiento.isoformat(),  # ➜ AGREGADO
            "zona_asignada": inspector.zona_asignada,
            "frecuenciaVisita": inspector.frecuenciaVisita,
            "borrado": inspector.borrado,
        })

    return resultado



def editar_inspector(db: Session, id_inspector: int, datos: InspectorCreate):
    inspector = db.query(Inspector).filter(Inspector.id_inspector == id_inspector).first()
    if not inspector:
        raise HTTPException(status_code=404, detail="Inspector no encontrado")

    persona = db.query(Persona).filter(Persona.id_persona == inspector.id_persona_inspector).first()
    if not persona:
        raise HTTPException(status_code=404, detail="Persona asociada no encontrada")

    # --- Validar duplicados (menos el mismo registro) ---
    correo_existente = db.query(Persona).filter(
        Persona.correo == datos.persona.correo,
        Persona.id_persona != persona.id_persona
    ).first()

    if correo_existente:
        raise HTTPException(status_code=400, detail="El correo ya está registrado por otra persona")

    cedula_existente = db.query(Persona).filter(
        Persona.cedula == datos.persona.cedula,
        Persona.id_persona != persona.id_persona
    ).first()

    if cedula_existente:
        raise HTTPException(status_code=400, detail="La cédula ya está registrada por otra persona")

    # --- Actualizar Persona ---
    persona.cedula = datos.persona.cedula
    persona.nombre = datos.persona.nombre
    persona.apellido = datos.persona.apellido
    persona.telefono = datos.persona.telefono
    persona.correo = datos.persona.correo
    persona.direccion = datos.persona.direccion
    persona.genero = datos.persona.genero
    persona.fecha_nacimiento = datos.persona.fecha_nacimiento

    # --- Actualizar Inspector ---
    inspector.zona_asignada = datos.zona_asignada
    inspector.frecuenciaVisita = datos.frecuenciaVisita

    # --- Actualizar Registro Supervisor Inspector ---
    registro = db.query(RegistroSupervisorInspector).filter(
        RegistroSupervisorInspector.id_inspector_registro == id_inspector
    ).first()

    if registro:
        registro.id_supervisor_registro = datos.id_supervisor_registro

    db.commit()

    return {"mensaje": "Inspector actualizado correctamente"}


def eliminar_inspector(db: Session, id_inspector: int):
    inspector = db.query(Inspector).filter(Inspector.id_inspector == id_inspector).first()
    if not inspector:
        raise HTTPException(status_code=404, detail="Inspector no encontrado")

    # --- Desactivar Inspector ---
    inspector.borrado = False

    # --- Desactivar Persona ---
    persona = db.query(Persona).filter(Persona.id_persona == inspector.id_persona_inspector).first()
    if persona:
        persona.borrado = False

    # --- Desactivar RegistroSupervisorInspector ---
    registro = db.query(RegistroSupervisorInspector).filter(
        RegistroSupervisorInspector.id_inspector_registro == id_inspector
    ).first()

    if registro:
        registro.borrado = False

    db.commit()
    return {"mensaje": "Inspector eliminado (borrado lógico en 3 tablas)"}


# --- Login ---
def login_inspector(db: Session, datos: LoginInspector):
    persona = db.query(Persona).filter(Persona.correo == datos.correo).first()

    if not persona or persona.rol != "inspector":
        raise HTTPException(status_code=401, detail="Usuario o contraseña incorrectos")

    if not verificar_contrasena(datos.contrasena, persona.contrasena):
        raise HTTPException(status_code=401, detail="Usuario o contraseña incorrectos")

    inspector = db.query(Inspector).filter(
        Inspector.id_persona_inspector == persona.id_persona,
        Inspector.borrado == True
    ).first()

    if not inspector:
        raise HTTPException(status_code=403, detail="El usuario no es inspector activo")

    return {
        "mensaje": "Inicio de sesión exitoso",
        "id_inspector": inspector.id_inspector,
        "nombre": persona.nombre,
        "correo": persona.correo,
        "role": persona.rol
    }

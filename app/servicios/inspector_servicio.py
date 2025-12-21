# app/servicios/inspector_servicio.py
from sqlalchemy.orm import Session
from datetime import date
from fastapi import HTTPException, status
import base64  # 👈 NUEVO

from app.modelos.persona import Persona
from app.modelos.inspector import Inspector
from app.modelos.registrosupervisorinspector import RegistroSupervisorInspector
from app.esquemas.inspector_esquema import InspectorCreate, LoginInspector
from app.seguridad.hash_contrasena import encriptar_contrasena, verificar_contrasena
from app.modelos.inspector_zona import InspectorZona
from app.modelos.zona_modelo import Zona
from app.modelos.trabajador_zona import TrabajadorZona
from app.modelos.trabajador import Trabajador
from app.modelos.camara_modelo import Camara

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
    validar_contrasena,
    validar_zona_asignada,
    validar_frecuencia_visita,
)


def crear_inspector(db: Session, datos: InspectorCreate):

    # ========================================================
    # 1️⃣ VALIDAR QUE LA CÉDULA SEA CORRECTA
    # ========================================================
    validar_cedula_ecuatoriana(datos.persona.cedula)

    # ========================================================
    # 2️⃣ BUSCAR PERSONA POR CÉDULA
    # ========================================================
    persona_existente = db.query(Persona).filter(
        Persona.cedula == datos.persona.cedula
    ).first()

    # ========================================================
    # 3️⃣ SI EXISTE Y ESTÁ ACTIVA → NO PERMITIR DUPLICAR
    # ========================================================
    if persona_existente and persona_existente.borrado is True:
        raise HTTPException(
            status_code=400,
            detail="Ya existe un inspector activo con esta cédula"
        )

    # ========================================================
    # 4️⃣ SI EXISTE Y ESTÁ INACTIVA → REACTIVAR
    # ========================================================
    if persona_existente and persona_existente.borrado is False:

        # --- Reactivar Persona ---
        persona_existente.nombre = datos.persona.nombre
        persona_existente.apellido = datos.persona.apellido
        persona_existente.telefono = datos.persona.telefono
        persona_existente.correo = datos.persona.correo
        persona_existente.direccion = datos.persona.direccion
        persona_existente.genero = datos.persona.genero
        persona_existente.fecha_nacimiento = datos.persona.fecha_nacimiento
        persona_existente.contrasena = encriptar_contrasena(datos.persona.contrasena)
        persona_existente.rol = "inspector"
        persona_existente.borrado = True  # ACTIVAR

        # --- Reactivar Inspector ---
        inspector = db.query(Inspector).filter(
            Inspector.id_persona_inspector == persona_existente.id_persona
        ).first()

        if inspector:
            inspector.zona_asignada = datos.zona_asignada
            inspector.frecuenciaVisita = datos.frecuenciaVisita
            inspector.borrado = True
        else:
            inspector = Inspector(
                zona_asignada=datos.zona_asignada,
                frecuenciaVisita=datos.frecuenciaVisita,
                id_persona_inspector=persona_existente.id_persona,
                borrado=True
            )
            db.add(inspector)

        db.commit()

        # --- Reactivar o crear RegistroSupervisorInspector ---
        registro = db.query(RegistroSupervisorInspector).filter(
            RegistroSupervisorInspector.id_inspector_registro == inspector.id_inspector
        ).first()

        if registro:
            registro.id_supervisor_registro = datos.id_supervisor_registro
            registro.fecha_asignacion = date.today()
            registro.borrado = True
        else:
            nuevo_registro = RegistroSupervisorInspector(
                id_supervisor_registro=datos.id_supervisor_registro,
                id_inspector_registro=inspector.id_inspector,
                fecha_asignacion=date.today(),
                borrado=True
            )
            db.add(nuevo_registro)

        db.commit()

        return {
            "mensaje": "Inspector reactivado correctamente",
            "id_inspector": inspector.id_inspector,
            "id_persona": persona_existente.id_persona,
        }

    # ========================================================
    # 5️⃣ SI NO EXISTE → CREAR NUEVA PERSONA + INSPECTOR
    # ========================================================

    validar_cedula_unica(db, datos.persona.cedula)
    validar_nombre(datos.persona.nombre)
    validar_apellido(datos.persona.apellido)
    validar_telefono(datos.persona.telefono)
    validar_correo_formato(datos.persona.correo)
    validar_correo_unico(db, datos.persona.correo)
    validar_direccion(datos.persona.direccion)
    validar_genero(datos.persona.genero)
    validar_fecha_nacimiento(datos.persona.fecha_nacimiento)
    validar_contrasena(datos.persona.contrasena)

    validar_zona_asignada(datos.zona_asignada)
    validar_frecuencia_visita(datos.frecuenciaVisita)

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
        "mensaje": "Inspector creado correctamente",
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
            "direccion": persona.direccion,
            "genero": persona.genero,
            "fecha_nacimiento": persona.fecha_nacimiento.isoformat(),
            "zona_asignada": inspector.zona_asignada,
            "frecuenciaVisita": inspector.frecuenciaVisita,
            "borrado": inspector.borrado,
        })

    return resultado


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


def editar_inspector(db: Session, id_inspector: int, datos: InspectorCreate):
    inspector = db.query(Inspector).filter(Inspector.id_inspector == id_inspector).first()
    if not inspector:
        raise HTTPException(status_code=404, detail="Inspector no encontrado")

    persona = db.query(Persona).filter(Persona.id_persona == inspector.id_persona_inspector).first()
    if not persona:
        raise HTTPException(status_code=404, detail="Persona asociada no encontrada")

    # --- VALIDAR PERSONA ---
    validar_cedula_ecuatoriana(datos.persona.cedula)

    cedula_existente = db.query(Persona).filter(
        Persona.cedula == datos.persona.cedula,
        Persona.id_persona != persona.id_persona
    ).first()
    if cedula_existente:
        raise HTTPException(status_code=400, detail="La cédula ya está registrada por otra persona")

    validar_nombre(datos.persona.nombre)
    validar_apellido(datos.persona.apellido)
    validar_telefono(datos.persona.telefono)
    validar_correo_formato(datos.persona.correo)

    correo_existente = db.query(Persona).filter(
        Persona.correo == datos.persona.correo,
        Persona.id_persona != persona.id_persona
    ).first()
    if correo_existente:
        raise HTTPException(status_code=400, detail="El correo ya está registrado por otra persona")

    validar_direccion(datos.persona.direccion)
    validar_genero(datos.persona.genero)
    validar_fecha_nacimiento(datos.persona.fecha_nacimiento)

    # --- VALIDAR CAMPOS DEL INSPECTOR ---
    validar_zona_asignada(datos.zona_asignada)
    validar_frecuencia_visita(datos.frecuenciaVisita)

    # Actualización (sin modificar contraseña)
    persona.cedula = datos.persona.cedula
    persona.nombre = datos.persona.nombre
    persona.apellido = datos.persona.apellido
    persona.telefono = datos.persona.telefono
    persona.correo = datos.persona.correo
    persona.direccion = datos.persona.direccion
    persona.genero = datos.persona.genero
    persona.fecha_nacimiento = datos.persona.fecha_nacimiento

    inspector.zona_asignada = datos.zona_asignada
    inspector.frecuenciaVisita = datos.frecuenciaVisita

    registro = db.query(RegistroSupervisorInspector).filter(
        RegistroSupervisorInspector.id_inspector_registro == id_inspector
    ).first()

    if registro:
        registro.id_supervisor_registro = datos.id_supervisor_registro

    db.commit()

    return {"mensaje": "Inspector actualizado correctamente"}


def eliminar_inspector(db: Session, id_inspector: int):
    inspector = db.query(Inspector).filter(
        Inspector.id_inspector == id_inspector,
        Inspector.borrado == True
    ).first()

    if not inspector:
        raise HTTPException(status_code=404, detail="Inspector no encontrado o inactivo")

    asignacion_activa = db.query(InspectorZona).filter(
        InspectorZona.id_inspector_inspectorzona == id_inspector,
        InspectorZona.borrado == True   # solo relaciones activas
    ).first()

    if asignacion_activa:
        raise HTTPException(
            status_code=400,
            detail=(
                "No se puede eliminar el inspector porque tiene zonas asignadas. "
                "Elimine o reasigne esas zonas primero."
            ),
        )

    inspector.borrado = False

    persona = db.query(Persona).filter(
        Persona.id_persona == inspector.id_persona_inspector
    ).first()
    if persona:
        persona.borrado = False

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


def listar_inspectores_por_supervisor(db: Session, id_supervisor: int):
    registros = (
        db.query(RegistroSupervisorInspector, Inspector, Persona)
        .join(Inspector, RegistroSupervisorInspector.id_inspector_registro == Inspector.id_inspector)
        .join(Persona, Inspector.id_persona_inspector == Persona.id_persona)
        .filter(
            RegistroSupervisorInspector.id_supervisor_registro == id_supervisor,
            Inspector.borrado == True
        )
        .all()
    )

    resultado = []
    for registro, inspector, persona in registros:
        resultado.append({
            "id_inspector": inspector.id_inspector,
            "nombre": persona.nombre,
            "apellido": persona.apellido,
            "correo": persona.correo,
            "telefono": persona.telefono,
            "cedula": persona.cedula,
            "direccion": persona.direccion,
            "genero": persona.genero,
            "fecha_nacimiento": persona.fecha_nacimiento.isoformat(),
            "zona_asignada": inspector.zona_asignada,
            "frecuenciaVisita": inspector.frecuenciaVisita,
            "borrado": inspector.borrado,
            "fecha_asignacion": registro.fecha_asignacion
        })

    return resultado


def obtener_zonas_por_inspector(db: Session, id_inspector: int):
    zonas = (
        db.query(InspectorZona, Zona)
        .join(Zona, InspectorZona.id_zona_inspectorzona == Zona.id_Zona)
        .filter(
            InspectorZona.id_inspector_inspectorzona == id_inspector,
            InspectorZona.borrado == True
        )
        .all()
    )

    resultado = []
    for asignacion, zona in zonas:

        # ➤ Contar trabajadores en la zona
        total_trabajadores = (
            db.query(TrabajadorZona)
            .filter(
                TrabajadorZona.id_zona_trabajadorzona == zona.id_Zona,
                TrabajadorZona.borrado == True
            )
            .count()
        )

        # ➤ Contar cámaras activas en la zona
        total_camaras = (
            db.query(Camara)
            .filter(
                Camara.id_zona == zona.id_Zona,
                Camara.borrado == True
            )
            .count()
        )

        resultado.append({
            "id_Zona": zona.id_Zona,
            "nombreZona": zona.nombreZona,
            "latitud": zona.latitud,
            "longitud": zona.longitud,
            "fecha_asignacion": asignacion.fecha_asignacion.isoformat(),
            "total_trabajadores": total_trabajadores,
            "total_camaras": total_camaras
        })

    return resultado

def correo_existe_activo(db: Session, correo: str) -> bool:
    """
    Verifica si un correo existe en un usuario ACTIVO
    Retorna True si existe, False si no existe
    """
    persona = db.query(Persona).filter(
        Persona.correo == correo,
        Persona.borrado == True  
    ).first()
    return persona is not None

def obtener_perfil_inspector(db: Session, id_inspector: int):

    inspector = db.query(Inspector).filter(
        Inspector.id_inspector == id_inspector,
        Inspector.borrado == True
    ).first()

    if not inspector:
        raise HTTPException(status_code=404, detail="Inspector no encontrado")

    persona = db.query(Persona).filter(
        Persona.id_persona == inspector.id_persona_inspector
    ).first()

    if not persona:
        raise HTTPException(status_code=404, detail="Persona asociada no encontrada")

    # 🔹 TODAS las zonas asignadas al inspector
    zonas = (
        db.query(InspectorZona, Zona)
        .join(Zona, Zona.id_Zona == InspectorZona.id_zona_inspectorzona)
        .filter(
            InspectorZona.id_inspector_inspectorzona == inspector.id_inspector,
            InspectorZona.borrado == True,
            Zona.borrado == True
        )
        .all()
    )

    zonas_asignadas = []
    for iz, zona in zonas:
        zonas_asignadas.append({
            "id_Zona": zona.id_Zona,
            "nombreZona": zona.nombreZona,
            "fecha_asignacion": iz.fecha_asignacion.date()
            if iz.fecha_asignacion else None
        })

    # 🔹 FOTO
    foto_base64 = None
    if persona.foto:
        try:
            foto_base64 = base64.b64encode(persona.foto).decode("utf-8")
        except Exception:
            foto_base64 = None

    return {
        "id_inspector": inspector.id_inspector,
        "id_persona": persona.id_persona,
        "cedula": persona.cedula,
        "nombre": persona.nombre,
        "apellido": persona.apellido,
        "telefono": persona.telefono,
        "correo": persona.correo,
        "direccion": persona.direccion,
        "genero": persona.genero,
        "fecha_nacimiento": persona.fecha_nacimiento,
        "frecuenciaVisita": inspector.frecuenciaVisita,
        "zonas_asignadas": zonas_asignadas,  # ✅ LISTA REAL
        "fotoBase64": foto_base64,
    }


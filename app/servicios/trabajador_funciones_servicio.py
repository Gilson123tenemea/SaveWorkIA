from sqlalchemy.orm import Session, joinedload
from fastapi import HTTPException
from passlib.context import CryptContext
from sqlalchemy import func, case
from app.modelos.trabajador import Trabajador
from app.modelos.persona import Persona
from app.modelos.empresa_modelo import Empresa
from app.modelos.trabajador_zona import TrabajadorZona
from app.modelos.zona_modelo import Zona
from app.modelos.registros_asistencia import RegistroAsistencia
from app.modelos.evidencias_fallo import EvidenciaFallo
from app.modelos.camara_modelo import Camara
import base64
from app.modelos.zona_epp import ZonaEpp
from sqlalchemy.orm import Session, joinedload
from fastapi import HTTPException
from sqlalchemy import func, case, extract
from datetime import datetime
from app.modelos.trabajador import Trabajador
from app.modelos.persona import Persona
from app.modelos.registros_asistencia import RegistroAsistencia
from app.modelos.camara_modelo import Camara
from app.modelos.zona_modelo import Zona
from app.modelos.inspector import Inspector
from typing import Optional

from app.modelos.trabajador import Trabajador
from app.modelos.persona import Persona
from app.Validaciones.validacion_usuario import (
    validar_nombre,
    validar_apellido,
    validar_correo_formato,
    validar_correo_unico,
    validar_telefono,
    validar_cargo,
)


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def login_trabajador(db: Session, correo: str, contrasena: str):
    persona = (
        db.query(Persona)
        .filter(
            Persona.correo == correo,
            Persona.borrado == True,
            Persona.rol == "TRABAJADOR"
        )
        .first()
    )

    if not persona:
        raise HTTPException(status_code=401, detail="Credenciales incorrectas")

    if not pwd_context.verify(contrasena, persona.contrasena):
        raise HTTPException(status_code=401, detail="Credenciales incorrectas")

    trabajador = (
        db.query(Trabajador)
        .filter(
            Trabajador.id_persona_trabajador == persona.id_persona,
            Trabajador.borrado == True,
            Trabajador.estado == True
        )
        .first()
    )

    if not trabajador:
        raise HTTPException(status_code=403, detail="Trabajador no activo")

    return {
        "id_trabajador": trabajador.id_trabajador,
        "nombre": persona.nombre,
        "apellido": persona.apellido,
        "correo": persona.correo,
        "rol": persona.rol,
        "id_empresa": trabajador.id_empresa
    }

def obtener_perfil_trabajador(db: Session, id_trabajador: int):
    trabajador = (
        db.query(Trabajador)
        .filter(
            Trabajador.id_trabajador == id_trabajador,
            Trabajador.borrado == True
        )
        .first()
    )

    if not trabajador:
        raise HTTPException(status_code=404, detail="Trabajador no encontrado")

    persona = (
        db.query(Persona)
        .filter(
            Persona.id_persona == trabajador.id_persona_trabajador,
            Persona.borrado == True
        )
        .first()
    )

    empresa = (
        db.query(Empresa)
        .filter(
            Empresa.id_Empresa == trabajador.id_empresa,
            Empresa.borrado == True
        )
        .first()
    )

    asignacion = (
        db.query(TrabajadorZona, Zona)
        .join(Zona, Zona.id_Zona == TrabajadorZona.id_zona_trabajadorzona)
        .filter(
            TrabajadorZona.id_trabajador_trabajadorzona == trabajador.id_trabajador,
            TrabajadorZona.borrado == True,
            Zona.borrado == True
        )
        .first()
    )

    zona_data = None
    if asignacion:
        tz, zona = asignacion
        zona_data = {
            "id_zona": zona.id_Zona,
            "nombreZona": zona.nombreZona,
            "latitud": zona.latitud,
            "longitud": zona.longitud
        }

    # 🔥 CONVERTIR FOTO A BASE64
    foto_base64 = None
    if persona.foto:
        foto_base64 = base64.b64encode(persona.foto).decode("utf-8")

    return {
        "id_trabajador": trabajador.id_trabajador,
        "cedula": persona.cedula,
        "nombre": persona.nombre,
        "apellido": persona.apellido,
        "correo": persona.correo,
        "telefono": persona.telefono,
        "cargo": trabajador.cargo,
        "foto_base64": foto_base64,  
        "empresa": {
            "id_empresa": empresa.id_Empresa,
            "nombreEmpresa": empresa.nombreEmpresa,
            "ruc": empresa.ruc,
            "sector": empresa.sector
        },
        "zona_asignada": zona_data
    }

def obtener_epp_humanos_por_zona(db: Session, id_zona: int) -> list[str]:
    """
    Devuelve los EPP obligatorios y activos de una zona
    SIN duplicados
    Ej: ["casco", "gafas"]
    """

    epps = (
        db.query(ZonaEpp.tipo_epp)
        .filter(
            ZonaEpp.id_zona == id_zona,
            ZonaEpp.activo == True,
            ZonaEpp.obligatorio == True
        )
        .distinct()
        .all()
    )

    # Convierte de [(casco,), (gafas,)] → ["casco", "gafas"]
    return [epp[0] for epp in epps]


def obtener_estadisticas_trabajador(db: Session, id_trabajador: int):
    # ---------------------------
    # 📌 ASISTENCIA
    # ---------------------------
    total_registros = (
        db.query(func.count(RegistroAsistencia.id_registro))
        .filter(RegistroAsistencia.id_trabajador == id_trabajador)
        .scalar()
    )

    cumple_epp = (
        db.query(func.count(RegistroAsistencia.id_registro))
        .filter(
            RegistroAsistencia.id_trabajador == id_trabajador,
            RegistroAsistencia.cumple_epp == True
        )
        .scalar()
    )

    no_cumple_epp = (
        db.query(func.count(RegistroAsistencia.id_registro))
        .filter(
            RegistroAsistencia.id_trabajador == id_trabajador,
            RegistroAsistencia.cumple_epp == False
        )
        .scalar()
    )

    tasa_cumplimiento = 0.0
    if total_registros > 0:
        tasa_cumplimiento = round((cumple_epp / total_registros) * 100, 2)

    # ---------------------------
    # 📌 INCUMPLIMIENTOS (EVIDENCIAS)
    # ---------------------------
    total_fallos = (
        db.query(func.count(EvidenciaFallo.id_evidencia))
        .join(
            RegistroAsistencia,
            RegistroAsistencia.id_registro == EvidenciaFallo.id_registro
        )
        .filter(
            RegistroAsistencia.id_trabajador == id_trabajador,
            EvidenciaFallo.borrado == True
        )
        .scalar()
    )

    revisados = (
        db.query(func.count(EvidenciaFallo.id_evidencia))
        .join(
            RegistroAsistencia,
            RegistroAsistencia.id_registro == EvidenciaFallo.id_registro
        )
        .filter(
            RegistroAsistencia.id_trabajador == id_trabajador,
            EvidenciaFallo.estado == True,
            EvidenciaFallo.borrado == True
        )
        .scalar()
    )

    pendientes = (
        db.query(func.count(EvidenciaFallo.id_evidencia))
        .join(
            RegistroAsistencia,
            RegistroAsistencia.id_registro == EvidenciaFallo.id_registro
        )
        .filter(
            RegistroAsistencia.id_trabajador == id_trabajador,
            EvidenciaFallo.estado == None,
            EvidenciaFallo.borrado == True
        )
        .scalar()
    )

    # ---------------------------
    # 🔥 DETECCIONES YOLO (CLASES DETECTADAS)
    # ---------------------------
    registros_con_fallos = (
        db.query(RegistroAsistencia)
        .join(EvidenciaFallo, EvidenciaFallo.id_registro == RegistroAsistencia.id_registro)
        .filter(
            RegistroAsistencia.id_trabajador == id_trabajador,
            RegistroAsistencia.cumple_epp == False
        )
        .all()
    )

    # Agregar detecciones únicas
    detecciones_totales = {}
    epps_por_zona = {}

    for reg in registros_con_fallos:
        evidencia = (
            db.query(EvidenciaFallo)
            .filter(EvidenciaFallo.id_registro == reg.id_registro)
            .first()
        )

        # Extraer clases detectadas
        if evidencia and evidencia.detalle_fallo:
            clases = [c.strip() for c in evidencia.detalle_fallo.split(",") if c.strip()]
            for clase in clases:
                detecciones_totales[clase] = detecciones_totales.get(clase, 0) + 1

        # Obtener EPPs obligatorios de la zona
        if reg.camara and reg.camara.zona:
            zona_id = reg.camara.zona.id_Zona
            if zona_id not in epps_por_zona:
                epps_por_zona[zona_id] = {
                    "zona": reg.camara.zona.nombreZona,
                    "epps": obtener_epp_humanos_por_zona(db, zona_id)
                }

    return {
        "id_trabajador": id_trabajador,
        "asistencia": {
            "total_registros": total_registros,
            "cumple_epp": cumple_epp,
            "no_cumple_epp": no_cumple_epp,
            "tasa_cumplimiento": tasa_cumplimiento
        },
        "incumplimientos": {
            "total_fallos": total_fallos,
            "revisados": revisados,
            "pendientes": pendientes
        },
        # 🔥 NUEVAS CLAVES
        "detecciones": detecciones_totales,  # {"casco": 3, "chaleco": 2, ...}
        "epps_por_zona": epps_por_zona  # {1: {"zona": "Zona A", "epps": [...]}, ...}
    }

def obtener_incumplimientos_por_trabajador(
    db: Session,
    id_trabajador: int
):
    # ===========================
    # 1️⃣ BUSCAR TRABAJADOR
    # ===========================
    trabajador = (
        db.query(Trabajador)
        .join(Persona)
        .filter(
            Trabajador.id_trabajador == id_trabajador,
            Trabajador.borrado == True
        )
        .first()
    )

    if not trabajador:
        raise HTTPException(status_code=404, detail="Trabajador no encontrado")

    persona = trabajador.persona

    # ===========================
    # 2️⃣ ESTADÍSTICAS GENERALES
    # ===========================
    todos = (
        db.query(RegistroAsistencia)
        .filter(RegistroAsistencia.id_trabajador == trabajador.id_trabajador)
        .all()
    )

    total = len(todos)
    cumple = len([r for r in todos if r.cumple_epp is True])
    incumple = total - cumple
    tasa = (cumple / total * 100) if total > 0 else 0

    # ===========================
    # 3️⃣ HISTORIAL DE INCUMPLIMIENTOS
    # ===========================
    registros = (
        db.query(RegistroAsistencia)
        .join(EvidenciaFallo, EvidenciaFallo.id_registro == RegistroAsistencia.id_registro)
        .options(
            joinedload(RegistroAsistencia.camara)
            .joinedload(Camara.zona)
        )
        .filter(
            RegistroAsistencia.id_trabajador == trabajador.id_trabajador,
            RegistroAsistencia.cumple_epp == False,
            EvidenciaFallo.borrado == True
        )
        .order_by(RegistroAsistencia.fecha_hora.desc())
        .all()
    )

    historial = []

    for reg in registros:
        evidencia = (
            db.query(EvidenciaFallo)
            .filter(EvidenciaFallo.id_registro == reg.id_registro)
            .first()
        )

        foto_base64 = None
        if evidencia and evidencia.foto_data:
            foto_base64 = base64.b64encode(evidencia.foto_data).decode("utf-8")

        # 🔥 CLASES YOLO DETECTADAS
        clases_detectadas = []
        if evidencia and evidencia.detalle_fallo:
            clases_detectadas = [
                c.strip() for c in evidencia.detalle_fallo.split(",") if c.strip()
            ]

        # 🔥 EPP OBLIGATORIOS DE LA ZONA
        epps_zona = []
        if reg.camara and reg.camara.zona:
            epps_zona = obtener_epp_humanos_por_zona(db, reg.camara.zona.id_Zona)

        historial.append({
            "trabajador": {
                "nombre": persona.nombre,
                "apellido": persona.apellido,
                "cedula": persona.cedula
            },
            "camara": {
                "codigo": reg.camara.codigo,
                "zona": reg.camara.zona.nombreZona
            },
            "evidencia": {
                "id_evidencia": evidencia.id_evidencia,
                "detalle": evidencia.detalle_fallo,
                "foto_base64": foto_base64,
                "fecha": evidencia.fecha_captura,
                "estado": evidencia.estado,
                "observaciones": evidencia.observaciones
            },
            # 🔥 NUEVAS CLAVES
            "detecciones": clases_detectadas,
            "epps_zona": epps_zona,
            "fecha_registro": reg.fecha_hora
        })

    # ===========================
    # 4️⃣ RESPUESTA FINAL
    # ===========================
    return {
        "estadisticas": {
            "total": total,
            "cumple": cumple,
            "incumple": incumple,
            "tasa": round(tasa, 2)
        },
        "historial": historial
    }

def obtener_historial_asistencias(
    db: Session,
    id_trabajador: int,
    mes: Optional[int] = None,
    año: Optional[int] = None
):
    """
    Obtiene el historial de asistencias de un trabajador con filtros opcionales.
    
    Args:
        db: Session de SQLAlchemy
        id_trabajador: ID del trabajador
        mes: Mes (1-12) opcional para filtrar
        año: Año opcional para filtrar
    
    Returns:
        Dict con total de registros y lista de asistencias
    """
    
    # ===========================
    # 1️⃣ VALIDAR TRABAJADOR
    # ===========================
    trabajador = (
        db.query(Trabajador)
        .filter(
            Trabajador.id_trabajador == id_trabajador,
            Trabajador.borrado == True
        )
        .first()
    )

    if not trabajador:
        raise HTTPException(status_code=404, detail="Trabajador no encontrado")

    persona = (
        db.query(Persona)
        .filter(
            Persona.id_persona == trabajador.id_persona_trabajador,
            Persona.borrado == True
        )
        .first()
    )

    # ===========================
    # 2️⃣ CONSTRUIR QUERY
    # ===========================
    query = (
        db.query(RegistroAsistencia)
        .join(Camara, Camara.id_camara == RegistroAsistencia.id_camara)
        .join(Zona, Zona.id_Zona == Camara.id_zona)
        .options(
            joinedload(RegistroAsistencia.camara)
            .joinedload(Camara.zona)
        )
        .filter(
            RegistroAsistencia.id_trabajador == id_trabajador
        )
    )

    # ===========================
    # 3️⃣ APLICAR FILTROS
    # ===========================
    if mes is not None and año is not None:
        query = query.filter(
            extract('month', RegistroAsistencia.fecha_hora) == mes,
            extract('year', RegistroAsistencia.fecha_hora) == año
        )
    elif año is not None:
        query = query.filter(
            extract('year', RegistroAsistencia.fecha_hora) == año
        )

    # ===========================
    # 4️⃣ ORDENAR Y EJECUTAR
    # ===========================
    registros = query.order_by(
        RegistroAsistencia.fecha_hora.desc()
    ).all()

    # ===========================
    # 5️⃣ PROCESAR RESULTADOS
    # ===========================
    total_cumple = sum(1 for r in registros if r.cumple_epp is True)
    total_no_cumple = sum(1 for r in registros if r.cumple_epp is False)

    historial = []

    for reg in registros:
        inspector_data = None
        if reg.camara and reg.camara.zona:

            zona = reg.camara.zona
            
            # Si tienes una relación directa entre zona e inspector
            # descomenta y ajusta según tu modelo:
            # inspector = db.query(Inspector).filter(
            #     Inspector.id_zona == zona.id_Zona
            # ).first()

            # Si no, puedes obtenerlo desde el supervisor del trabajador
            inspector = (
                db.query(Inspector)
                .join(Persona, Persona.id_persona == Inspector.id_persona_inspector)
                .filter(
                    Inspector.borrado == True
                )
                .first()
            )

            if inspector:
                inspector_persona = (
                    db.query(Persona)
                    .filter(Persona.id_persona == inspector.id_persona_inspector)
                    .first()
                )
                if inspector_persona:
                    inspector_data = {
                        "nombre": inspector_persona.nombre,
                        "apellido": inspector_persona.apellido,
                        "cedula": inspector_persona.cedula
                    }

        # Extraer fecha y hora
        fecha_registro = reg.fecha_hora
        hora_str = fecha_registro.strftime("%H:%M:%S") if fecha_registro else "N/A"

        historial.append({
            "id_registro": reg.id_registro,
            "fecha": fecha_registro.date() if fecha_registro else None,
            "hora": hora_str,
            "codigo_trabajador": trabajador.codigo_trabajador,
            "cedula": persona.cedula,
            "nombre": persona.nombre,
            "apellido": persona.apellido,
            "nombre_zona": reg.camara.zona.nombreZona if reg.camara and reg.camara.zona else "N/A",
            "nombre_inspector": inspector_data["nombre"] if inspector_data else "N/A",
            "apellido_inspector": inspector_data["apellido"] if inspector_data else "N/A",
            "codigo_camara": reg.camara.codigo if reg.camara else "N/A",
            "cumple_epp": reg.cumple_epp
        })

    # ===========================
    # 6️⃣ RETORNAR RESPUESTA
    # ===========================
    return {
        "total_registros": len(registros),
        "total_cumple": total_cumple,
        "total_no_cumple": total_no_cumple,
        "mes": mes,
        "año": año,
        "registros": historial
    }


def actualizar_trabajador(
    db: Session,
    id_trabajador: int,
    nombre: str = None,
    apellido: str = None,
    correo: str = None,
    telefono: str = None,
    cargo: str = None,
):
    """
    Actualiza los datos del trabajador.
    
    Campos editables:
    - nombre
    - apellido
    - correo
    - telefono
    - cargo
    
    Args:
        db: Session de SQLAlchemy
        id_trabajador: ID del trabajador a actualizar
        nombre: Nuevo nombre (opcional)
        apellido: Nuevo apellido (opcional)
        correo: Nuevo correo (opcional)
        telefono: Nuevo teléfono (opcional)
        cargo: Nuevo cargo (opcional)
    
    Returns:
        Dict con los datos actualizados del trabajador
    """
    
    # ===========================
    # 1️⃣ VALIDAR QUE TRABAJADOR EXISTA
    # ===========================
    trabajador = (
        db.query(Trabajador)
        .filter(
            Trabajador.id_trabajador == id_trabajador,
            Trabajador.borrado == True
        )
        .first()
    )

    if not trabajador:
        raise HTTPException(status_code=404, detail="Trabajador no encontrado")

    # ===========================
    # 2️⃣ OBTENER PERSONA ASOCIADA
    # ===========================
    persona = (
        db.query(Persona)
        .filter(
            Persona.id_persona == trabajador.id_persona_trabajador,
            Persona.borrado == True
        )
        .first()
    )

    if not persona:
        raise HTTPException(status_code=404, detail="Persona asociada no encontrada")

    # ===========================
    # 3️⃣ VALIDACIONES Y ACTUALIZACIÓN DE NOMBRE
    # ===========================
    if nombre is not None:
        nombre_limpio = nombre.strip() if isinstance(nombre, str) else None
        if nombre_limpio:
            validar_nombre(nombre_limpio)
            persona.nombre = nombre_limpio

    # ===========================
    # 4️⃣ VALIDACIONES Y ACTUALIZACIÓN DE APELLIDO
    # ===========================
    if apellido is not None:
        apellido_limpio = apellido.strip() if isinstance(apellido, str) else None
        if apellido_limpio:
            validar_apellido(apellido_limpio)
            persona.apellido = apellido_limpio

    # ===========================
    # 5️⃣ VALIDACIONES Y ACTUALIZACIÓN DE CORREO
    # ===========================
    if correo is not None:
        correo_limpio = correo.strip() if isinstance(correo, str) else None
        if correo_limpio:
            validar_correo_formato(correo_limpio)
            
            # Validar que el correo sea único (excluir el correo actual)
            correo_existente = (
                db.query(Persona)
                .filter(
                    Persona.correo == correo_limpio,
                    Persona.id_persona != persona.id_persona,
                    Persona.borrado == True
                )
                .first()
            )
            
            if correo_existente:
                raise HTTPException(
                    status_code=400,
                    detail="Ya existe un usuario activo con este correo"
                )
            
            persona.correo = correo_limpio

    # ===========================
    # 6️⃣ VALIDACIONES Y ACTUALIZACIÓN DE TELÉFONO
    # ===========================
    if telefono is not None:
        telefono_limpio = telefono.strip() if isinstance(telefono, str) else None
        if telefono_limpio:
            validar_telefono(telefono_limpio)
            persona.telefono = telefono_limpio

    # ===========================
    # 7️⃣ VALIDACIONES Y ACTUALIZACIÓN DE CARGO
    # ===========================
    if cargo is not None:
        cargo_limpio = cargo.strip() if isinstance(cargo, str) else None
        if cargo_limpio:
            validar_cargo(cargo_limpio)
            trabajador.cargo = cargo_limpio

    # ===========================
    # 8️⃣ GUARDAR CAMBIOS
    # ===========================
    try:
        db.add(persona)
        db.add(trabajador)
        db.commit()
        db.refresh(trabajador)
        db.refresh(persona)
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Error al guardar los cambios: {str(e)}"
        )

    # ===========================
    # 9️⃣ RETORNAR DATOS ACTUALIZADOS
    # ===========================
    return {
        "id_trabajador": trabajador.id_trabajador,
        "cedula": persona.cedula,
        "nombre": persona.nombre,
        "apellido": persona.apellido,
        "correo": persona.correo,
        "telefono": persona.telefono,
        "cargo": trabajador.cargo,
        "mensaje": "Trabajador actualizado exitosamente"
    }
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
            Trabajador.borrado == True   # ✅ ACTIVO SEGÚN TU DISEÑO
        )
        .first()
    )

    if not trabajador:
        raise HTTPException(status_code=404, detail="Trabajador no encontrado")

    persona = (
        db.query(Persona)
        .filter(
            Persona.id_persona == trabajador.id_persona_trabajador,
            Persona.borrado == True     # ✅
        )
        .first()
    )

    empresa = (
        db.query(Empresa)
        .filter(
            Empresa.id_Empresa == trabajador.id_empresa,
            Empresa.borrado == True     # ✅
        )
        .first()
    )

    asignacion = (
        db.query(TrabajadorZona, Zona)
        .join(Zona, Zona.id_Zona == TrabajadorZona.id_zona_trabajadorzona)
        .filter(
            TrabajadorZona.id_trabajador_trabajadorzona == trabajador.id_trabajador,
            TrabajadorZona.borrado == True,   # ✅
            Zona.borrado == True               # ✅
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

    return {
        "id_trabajador": trabajador.id_trabajador,
        "cedula": persona.cedula,
        "nombre": persona.nombre,
        "apellido": persona.apellido,
        "correo": persona.correo,
        "telefono": persona.telefono,
        "cargo": trabajador.cargo,
        "area_trabajo": trabajador.area_trabajo,
        "empresa": {
            "id_empresa": empresa.id_Empresa,
            "nombreEmpresa": empresa.nombreEmpresa,
            "ruc": empresa.ruc,
            "sector": empresa.sector
        },
        "zona_asignada": zona_data
    }

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
        }
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
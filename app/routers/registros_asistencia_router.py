"""
Router para registro de asistencia y verificación de EPP
Orquesta: obtener frame → analizar EPP → filtrar por zona → crear registros
"""

from fastapi import APIRouter, Depends, HTTPException, Query, Body
from sqlalchemy.orm import Session

from app.config import get_db
from app.modelos.camara_modelo import Camara

from app.esquemas.registros_asistencia_esquema import (
    RegistroAsistenciaCreate,
    RegistroAsistenciaResponse
)
from app.esquemas.evidencias_fallo_esquema import EvidenciaFalloCreate

from app.servicios.registros_asistencia_servicio import (
    crear_registro_asistencia,
    obtener_epp_activos_por_zona
)
from app.servicios.evidencias_fallo_servicio import guardar_evidencia_fallo
from app.servicios.analisis_epp_servicio import analizar_frame_epp
from app.servicios.camara_buffer_servicio import obtener_ultimo_frame_camara


router = APIRouter(
    prefix="/registros-asistencia",
    tags=["Registros de Asistencia"]
)

# ==========================================================
# REGISTRAR ASISTENCIA (SIN IA)
# ==========================================================
@router.post("/registrar", response_model=RegistroAsistenciaResponse)
def registrar_asistencia(
    asistencia: RegistroAsistenciaCreate,
    db: Session = Depends(get_db)
):
    try:
        return crear_registro_asistencia(db, asistencia)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"❌ Error al registrar asistencia: {str(e)}"
        )

# ==========================================================
# VERIFICAR EPP (IA + ZONA)
# ==========================================================

@router.post("/verificar-epp/{id_camara}")
def verificar_epp(
    id_camara: int,
    codigo_trabajador: str = Query(...),
    request_body: dict = Body(...),
    db: Session = Depends(get_db)
):
    try:
        trabajador_data = request_body if isinstance(request_body, dict) else {}

        print("\n" + "=" * 80)
        print(f"🔍 Verificando EPP | Cámara: {id_camara} | Trabajador: {codigo_trabajador}")
        print("=" * 80)

        # 🆕 DEBUG: VER QUÉ RECIBE EL BACKEND
        print(f"\n📦 DATOS RECIBIDOS:")
        print(f"   Type trabajador_data: {type(trabajador_data)}")
        print(f"   Contenido completo: {trabajador_data}")
        if isinstance(trabajador_data, dict):
            print(f"   Keys disponibles: {list(trabajador_data.keys())}")
        print()

        # ==================================================
        # 🆕 0️⃣ VALIDAR TRABAJADOR EN LA EMPRESA
        # ==================================================
        from app.modelos.trabajador import Trabajador
        
        id_empresa = trabajador_data.get("id_empresa")
        id_trabajador = trabajador_data.get("id_trabajador")

        print(f"🔎 VALORES EXTRAÍDOS:")
        print(f"   id_empresa: {id_empresa} (tipo: {type(id_empresa)})")
        print(f"   id_trabajador: {id_trabajador} (tipo: {type(id_trabajador)})")
        print()

        if not id_empresa or not id_trabajador:
            print(f"❌ VALIDACIÓN FALLIDA - Faltan datos obligatorios")
            raise HTTPException(
                status_code=400,
                detail="❌ Faltan datos: id_empresa o id_trabajador"
            )

        print(f"✅ Datos básicos validados\n")

       # 🆕 BÚSQUEDA CORRECTA: borrado = True = Activo (en tu BD)
        print(f"🔍 BUSCANDO EN BD:")
        print(f"   Buscando: codigo={codigo_trabajador}, id_empresa={id_empresa}, borrado=True (activo)")
        
        trabajador_bd = db.query(Trabajador).filter(
            Trabajador.codigo_trabajador == codigo_trabajador,
            Trabajador.id_empresa == id_empresa,
            Trabajador.borrado == True  # ← CAMBIO: True en lugar de False
        ).first()

        if not trabajador_bd:
            print(f"❌ TRABAJADOR NO ENCONTRADO EN BD")
            raise HTTPException(
                status_code=404,
                detail=f"❌ Trabajador {codigo_trabajador} no existe en la empresa {id_empresa}"
            )

        print(f"✅ Trabajador validado: {trabajador_bd.persona.nombre}")
        print(f"   ID real en BD: {trabajador_bd.id_trabajador}")
        print("=" * 80 + "\n")
        
        # 🆕 ACTUALIZAR id_trabajador con el valor real de BD
        id_trabajador = trabajador_bd.id_trabajador
        trabajador_data["id_trabajador"] = id_trabajador

        # ==================================================
        # 1️⃣ CÁMARA Y ZONA
        # ==================================================
        camara = db.query(Camara).filter(
            Camara.id_camara == id_camara,
            Camara.borrado == True
        ).first()

        if not camara:
            raise HTTPException(404, "❌ Cámara no encontrada")

        zona = camara.zona
        if not zona:
            raise HTTPException(400, "❌ La cámara no tiene zona asignada")

        # ==================================================
        # 2️⃣ EPP ACTIVOS DE LA ZONA
        # ==================================================
        epp_zona = obtener_epp_activos_por_zona(db, zona.id_Zona)

        if not epp_zona:
            raise HTTPException(400, "❌ La zona no tiene EPP configurado")

        # ==================================================
        # 3️⃣ FRAME
        # ==================================================
        frame = obtener_ultimo_frame_camara(id_camara)
        if frame is None:
            raise HTTPException(400, "❌ No hay stream activo")

        # ==================================================
        # 4️⃣ ANALISIS YOLO (MODELO MANDA)
        # ==================================================
        analisis = analizar_frame_epp(frame)
        if not analisis:
            raise HTTPException(500, "❌ Error analizando frame")

        detecciones_modelo = analisis.get("detecciones", {})

        print("🎯 Detecciones modelo:", detecciones_modelo)

        # ==================================================
        # 🔥 5️⃣ FILTRAR SEGÚN EPP DE LA ZONA (SIN YOLO AQUÍ)
        # ==================================================
        detecciones_filtradas = {}
        faltantes = []

        for epp in epp_zona:  # ej: "gafas", "casco"
            estado = detecciones_modelo.get(epp)

            detectado = bool(estado and estado.get("detectado") is True)

            detecciones_filtradas[epp] = detectado

            if not detectado:
                faltantes.append(epp)

        cumple_epp = len(faltantes) == 0

        detalle_fallo = (
            "Cumple EPP"
            if cumple_epp
            else "Falta " + ", ".join(faltantes)
        )

        # ==================================================
        # 6️⃣ REGISTRO ASISTENCIA
        # ==================================================
        asistencia = RegistroAsistenciaCreate(
            cumple_epp=cumple_epp,
            codigo_ingresado=codigo_trabajador,
            id_trabajador=trabajador_data["id_trabajador"],
            id_empresa=trabajador_data["id_empresa"],
            id_zona=zona.id_Zona,
            id_supervisor=trabajador_data["id_supervisor_trabajador"],
            id_camara=id_camara,
            id_inspector=trabajador_data.get("id_inspector"),
            detalle_fallo=detalle_fallo
        )

        registro = crear_registro_asistencia(db, asistencia)
        print(f"✅ Registro creado | ID: {registro.id_registro}")

        # ==================================================
        # 7️⃣ EVIDENCIA (SI FALLA)
        # ==================================================
        evidencia_base64 = None

        if not cumple_epp:
            evidencia = EvidenciaFalloCreate(
                foto_base64=analisis.get("foto_base64"),
                detalle_fallo=detalle_fallo,
                id_registro=registro.id_registro
            )
            guardar_evidencia_fallo(db, evidencia)
            evidencia_base64 = analisis.get("foto_base64")

        # ==================================================
        # 8️⃣ RESPUESTA FINAL
        # ==================================================
        return {
            "status": "✅ CUMPLE EPP" if cumple_epp else "❌ NO CUMPLE EPP",
            "mensaje": detalle_fallo,
            "registro": {
                "id_registro": registro.id_registro,
                "trabajador": {
                    "id": trabajador_data["id_trabajador"],
                    "codigo": codigo_trabajador,
                    "nombre": f"{trabajador_data['persona']['nombre']} {trabajador_data['persona']['apellido']}"
                },
                "cumple_epp": cumple_epp,
                "fecha_hora": registro.fecha_hora.isoformat()
            },
            "zona": {
                "id": zona.id_Zona,
                "nombre": zona.nombreZona
            },
            "epp_requeridos": epp_zona,
            "detecciones": detecciones_filtradas,
            "evidencia": {
                "tiene_fallo": not cumple_epp,
                "foto_base64": evidencia_base64,
                "detalle": detalle_fallo
            }
        }

    except HTTPException:
        raise

    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(500, f"❌ {str(e)}")
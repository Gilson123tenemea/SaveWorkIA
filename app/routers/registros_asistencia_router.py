# app/routers/registros_asistencia.py
"""
Router para registro de asistencia y verificación de EPP
Orquesta: obtener frame → analizar EPP → crear registros
"""

from fastapi import APIRouter, Depends, HTTPException,Query
from sqlalchemy.orm import Session
from app.config import get_db   
from app.modelos.trabajador import Trabajador
from app.esquemas.registros_asistencia_esquema import (
    RegistroAsistenciaCreate,
    RegistroAsistenciaResponse
)
from app.esquemas.evidencias_fallo_esquema import EvidenciaFalloCreate
from app.servicios.registros_asistencia_servicio import crear_registro_asistencia
from app.servicios.evidencias_fallo_servicio import guardar_evidencia_fallo
from app.servicios.analisis_epp_servicio import analizar_frame_epp
from app.servicios.camara_buffer_servicio import obtener_ultimo_frame_camara
from app.servicios.almacenamiento_fotos_servicio import guardar_foto_desde_base64
from fastapi import Body
from typing import Dict, Any

router = APIRouter(prefix="/registros-asistencia", tags=["Registros de Asistencia"])


@router.post("/registrar", response_model=RegistroAsistenciaResponse)
def registrar_asistencia(
    asistencia: RegistroAsistenciaCreate,
    db: Session = Depends(get_db)
):
    """
    Registra asistencia de trabajador (sin análisis EPP)
    Se usa cuando ya se hizo análisis previo
    
    Args:
        asistencia: datos de asistencia
        db: sesión de BD
    
    Returns:
        RegistroAsistencia creado
    """
    try:
        # Crear asistencia normal
        registro = crear_registro_asistencia(db, asistencia)
        
        # 🔥 Si no cumple EPP → Crear evidencia automáticamente
        if not registro.cumple_epp:
            evidencia = EvidenciaFalloCreate(
                foto_url="pendiente",  # Se actualiza luego
                detalle_fallo=getattr(asistencia, 'detalle_fallo', "Incumplimiento EPP"),
                id_registro=registro.id_registro,
            )
            guardar_evidencia_fallo(db, evidencia)
        
        return registro
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"❌ Error al registrar asistencia: {str(e)}"
        )

@router.post("/verificar-epp/{id_camara}")
def verificar_epp(
    id_camara: int,
    codigo_trabajador: str = Query(...),
    request_body: dict = Body(...),
    db: Session = Depends(get_db)
):
    """
    🔥 VERIFICA EPP Y CREA REGISTROS
    """
    try:
        # Obtener trabajador_data del body
        trabajador_data = request_body if isinstance(request_body, dict) else {}
        
        print(f"\n{'='*60}")
        print(f"🔍 Verificando EPP: {codigo_trabajador}")
        print(f"📋 Datos recibidos: {trabajador_data.get('id_trabajador')}")
        print(f"{'='*60}\n")
        
        # 1️⃣ OBTENER FRAME
        frame = obtener_ultimo_frame_camara(id_camara)
        if frame is None:
            raise HTTPException(
                status_code=400,
                detail=f"❌ No hay stream activo"
            )
        
        # 2️⃣ ANALIZAR EPP
        analisis = analizar_frame_epp(frame)
        if analisis is None:
            raise HTTPException(
                status_code=500,
                detail="❌ Error analizando frame"
            )
        
        # 3️⃣ CREAR REGISTRO
        asistencia = RegistroAsistenciaCreate(
            cumple_epp=analisis['cumple_epp'],
            codigo_ingresado=codigo_trabajador,
            id_trabajador=trabajador_data['id_trabajador'],
            id_empresa=trabajador_data['id_empresa'],
            id_zona=trabajador_data['id_zona'],
            id_supervisor=trabajador_data['id_supervisor_trabajador'],
            id_camara=id_camara,
            id_inspector=trabajador_data.get('id_inspector'),
            detalle_fallo=analisis['detalle_fallo']
        )
        
        registro = crear_registro_asistencia(db, asistencia)
        print(f"✅ Registro creado: ID {registro.id_registro}")
        
        # 4️⃣ CREAR EVIDENCIA SI FALLA
        foto_url = None
        if not registro.cumple_epp:
            foto_url = guardar_foto_desde_base64(
                base64_str=analisis['foto_base64'],
                id_trabajador=trabajador_data['id_trabajador'],
                id_registro=registro.id_registro,
                usar_temporal=False
            )
            
            evidencia = EvidenciaFalloCreate(
                foto_url=foto_url or "pendiente",
                detalle_fallo=analisis['detalle_fallo'],
                id_registro=registro.id_registro,
            )
            guardar_evidencia_fallo(db, evidencia)
        
        print(f"\n✅ {'CUMPLE EPP' if registro.cumple_epp else 'NO CUMPLE EPP'}\n")
        
        return {
            "status": "✅ CUMPLE EPP" if registro.cumple_epp else "❌ NO CUMPLE EPP",
            "mensaje": analisis['detalle_fallo'],
            "registro": {
                "id_registro": registro.id_registro,
                "trabajador": {
                    "id": trabajador_data['id_trabajador'],
                    "codigo": codigo_trabajador,
                    "nombre": f"{trabajador_data['persona']['nombre']} {trabajador_data['persona']['apellido']}"
                },
                "cumple_epp": registro.cumple_epp,
                "fecha_hora": registro.fecha_hora.isoformat()
            },
            "detecciones": {
                "casco": analisis['detecciones']['casco']['detectado'],
                "chaleco": analisis['detecciones']['chaleco']['detectado'],
                "guantes": analisis['detecciones']['guantes']['detectado'],
                "botas": analisis['detecciones']['botas']['detectado'],
                "lentes": analisis['detecciones']['lentes']['detectado']
            },
            "evidencia": {
                "tiene_fallo": not registro.cumple_epp,
                "foto_url": foto_url,
                "detalle": analisis['detalle_fallo']
            }
        }
    
    except HTTPException as e:
        print(f"❌ Error HTTP: {e.detail}\n")
        raise e
    except Exception as e:
        print(f"❌ Error: {str(e)}\n")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"❌ {str(e)}")
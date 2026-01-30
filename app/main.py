# app/main.py
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.exc import SQLAlchemyError
from app.servicios.notificaciones_fcm_servicio import NotificacionesFCMServicio
from app.config import Base, engine, SessionLocal
from sqlalchemy import text
from fastapi.responses import JSONResponse
import traceback
from sqlalchemy import text
from fastapi.responses import StreamingResponse
import httpx
# ----------------------------------------------------------------------
# 🔹 Importar todos los modelos antes de crear las tablas
# ----------------------------------------------------------------------
from app.modelos import persona
from app.modelos import administrador
from app.modelos import supervisor
from app.modelos import inspector
from app.modelos import trabajador
from app.modelos import empresa_modelo
from app.modelos import zona_modelo
from app.modelos import camara_modelo
from app.modelos import alerta_modelo
from app.modelos import evento_deteccion_modelo
from app.modelos import reporte
from app.modelos import revision_reporte_modelo
from app.modelos import registrosupervisorinspector
from app.modelos import inspector_reporte
from app.modelos import inspector_zona
from app.modelos import trabajador_zona
from app.modelos import registros_asistencia
from app.modelos import evidencias_fallo
from app.modelos import zona_epp
from app.modelos import token_reset_modelo
from app.modelos import fcm_token_modelo
from app.logs.mongodb import MongoDB

# DEPLEIEGE EN AZURE
# ----------------------------------------------------------------------
# 🔹 Crear tablas automáticamente (solo si no existen)
# ----------------------------------------------------------------------
try:
    Base.metadata.create_all(bind=engine)
    print("✅ Tablas creadas en MySQL")
except Exception as e:
    print(f"⚠️ Advertencia al crear tablas: {e}")

# ----------------------------------------------------------------------
# 🔹 Importar routers
# ----------------------------------------------------------------------
from app.routers import (
    persona_router,
    administrador_router,
    supervisor_router,
    inspector_router,
    registrosupervisorinspector_router,
    trabajador_router,
    empresa_router,
    zona_router,
    camara_router,
    alerta_router,
    evento_deteccion_router,
    revision_reporte_router,
    inspector_reporte_router,
    inspector_zona_router,
    trabajador_zona_router,
    monitoreo_router,
    camara_ia,
    registros_asistencia_router,
    evidencias_fallo_router,
    reporte_incumplimientos_router,
    dashboard_router,
    dashboard_supervisor,
    reporte_inspector_incumplimiento_router,
    inspector_notificaciones_router,
    dashboard_inspector,
    trabajador_funciones_router,
    reporte_router,
    zona_epp_router,
    auth_ruta,



)

# ----------------------------------------------------------------------
# 🔹 Instancia principal de FastAPI
# ----------------------------------------------------------------------
app = FastAPI(
    title="SaveWorkIA Backend",
    version="1.0",
    description="API REST del sistema SaveWorkIA para gestión y detección con IA.",
    debug=True
)


# ----------------------------------------------------------------------
# 🔹 Configuración de CORS (para permitir peticiones desde el frontend)
# ----------------------------------------------------------------------
origins = [
    "http://localhost:3000",       
    "http://127.0.0.1:3000",       
    "http://127.0.0.1:5173",         
    "http://104.45.177.193:3000",    
    "https://tudominio.com",  
    "https://nice-glacier-091162410.1.azurestaticapps.net",       
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,    
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================================
# 🔹 MIDDLEWARE PARA REDIRIGIR /proxy/* A HTTP
# ============================================================
@app.middleware("http")
async def proxy_middleware(request: Request, call_next):
    """
    Redirige peticiones a /proxy/* hacia cualquier URL HTTP
    Ejemplo: /proxy/http://ejemplo.com/ruta → http://ejemplo.com/ruta
    """
    if request.url.path.startswith("/proxy/"):
        target_url = request.url.path[7:]  # Quita "/proxy/"
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.request(
                    method=request.method,
                    url=target_url,
                    headers={k: v for k, v in request.headers.items() if k.lower() not in ["host"]},
                    content=await request.body(),
                )
                return StreamingResponse(
                    iter([response.content]),
                    status_code=response.status_code,
                    headers=dict(response.headers),
                    media_type=response.headers.get("content-type"),
                )
            except Exception as e:
                return JSONResponse({"error": str(e)}, status_code=500)
    
    return await call_next(request)

# ----------------------------------------------------------------------
# 🔹 Registrar Routers
# ----------------------------------------------------------------------
app.include_router(persona_router.router)
app.include_router(administrador_router.router)
app.include_router(supervisor_router.router)
app.include_router(inspector_router.router)
app.include_router(registrosupervisorinspector_router.router)
app.include_router(trabajador_router.router)
app.include_router(empresa_router.router)
app.include_router(zona_router.router)
app.include_router(camara_router.router)
app.include_router(alerta_router.router)
app.include_router(evento_deteccion_router.router)
app.include_router(revision_reporte_router.router)
app.include_router(inspector_reporte_router.router)
app.include_router(inspector_zona_router.router)
app.include_router(trabajador_zona_router.router)
app.include_router(monitoreo_router.router)
app.include_router(camara_ia.router)
app.include_router(registros_asistencia_router.router)
app.include_router(evidencias_fallo_router.router)
app.include_router(reporte_incumplimientos_router.router)
app.include_router(dashboard_router.router)
app.include_router(dashboard_supervisor.router)
app.include_router(reporte_inspector_incumplimiento_router.router)
app.include_router(inspector_notificaciones_router.router)
app.include_router(dashboard_inspector.router)
app.include_router(trabajador_funciones_router.router)
app.include_router(reporte_router.router)
app.include_router(zona_epp_router.router)
app.include_router(auth_ruta.router)
# ----------------------------------------------------------------------
# 🔹 Endpoint raíz de prueba
# ----------------------------------------------------------------------
@app.get("/")
def root():
    """Verifica el estado del backend y conexiones"""
    from app.config import verificar_conexion
    
    # Verificar SQL
    sql_ok = verificar_conexion()
    
    # Verificar MongoDB
    mongo_ok = False
    try:
        MongoDB.get_client()
        mongo_ok = True
    except:
        pass
    
    return {
        "message": "🚀 SaveWorkIA Backend",
        "status": "running",
        "connections": {
            "sql_server": "✅ Connected" if sql_ok else "❌ Disconnected",
            "mongodb": "✅ Connected" if mongo_ok else "❌ Disconnected"
        }
    }

@app.on_event("startup")
async def startup_event():
    """Se ejecuta cuando inicia la app"""
    print("\n" + "="*50)
    print("🚀 INICIANDO SAVEWORKIA BACKEND")
    print("="*50 + "\n")
    
    # 1. Verificar SQL Server
    from app.config import verificar_conexion
    if verificar_conexion():
        print("✅ SQL Server: Conectado\n")
    else:
        print("⚠️ SQL Server: Sin conexión (continuando...)\n")
    
    # 2. Inicializar Firebase
    try:
        NotificacionesFCMServicio.inicializar()
        print("✅ Firebase: Inicializado\n")
    except Exception as e:
        print(f"⚠️ Firebase: Error - {str(e)[:100]}\n")

    # 3. Conectar MongoDB
    try:
        MongoDB.get_client()
        print("✅ MongoDB: Conectado\n")
    except Exception as e:
        print(f"⚠️ MongoDB: Error - {str(e)[:100]}\n")
    
    print("="*50)
    print("✅ BACKEND LISTO")
    print("="*50 + "\n")

@app.on_event("shutdown")
async def shutdown_event():
    MongoDB.close_connection()
    print("🔒 Conexión a MongoDB cerrada")


@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    return JSONResponse(
        status_code=500,
        content={
            "error": str(exc),
            "trace": traceback.format_exc()
        }
    )


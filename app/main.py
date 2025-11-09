# app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.exc import SQLAlchemyError

from app.config import Base, engine, SessionLocal

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

# ----------------------------------------------------------------------
# 🔹 Crear tablas automáticamente (solo si no existen)
# ----------------------------------------------------------------------
Base.metadata.create_all(bind=engine)

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
    revision_reporte_router
)

# ----------------------------------------------------------------------
# 🔹 Instancia principal de FastAPI
# ----------------------------------------------------------------------
app = FastAPI(
    title="SaveWorkIA Backend",
    version="1.0",
    description="API REST del sistema SaveWorkIA para gestión y detección con IA."
)

# ----------------------------------------------------------------------
# 🔹 Configuración de CORS (para permitir peticiones desde el frontend)
# ----------------------------------------------------------------------
origins = [
    "http://localhost:5173",  # tu frontend React o Vite local
    "http://127.0.0.1:5173"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,      # puedes usar ["*"] si aún no tienes dominio
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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

# ----------------------------------------------------------------------
# 🔹 Endpoint raíz de prueba
# ----------------------------------------------------------------------
@app.get("/")
def root():
    """
    Verifica el estado del backend y la conexión a la base de datos.
    """
    try:
        db = SessionLocal()
        db.execute("SELECT 1")
        db.close()
        return {
            "message": "🚀 Proyecto SaveWorkIA funcionando correctamente",
            "db_status": "✅ Conexión a la base de datos exitosa"
        }
    except SQLAlchemyError as e:
        return {
            "message": "🚀 Proyecto SaveWorkIA funcionando",
            "db_status": f"❌ Error en la base de datos: {e}"
        }

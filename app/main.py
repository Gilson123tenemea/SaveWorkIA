# app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.exc import SQLAlchemyError

from app.config import Base, engine, SessionLocal
from app.routers import persona_router  # Importa tu nuevo router (puedes agregar más luego)

# ----------------------------------------------------------------------
# 🔹 Crear tablas automáticamente (solo si no existen)
# ----------------------------------------------------------------------
Base.metadata.create_all(bind=engine)

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
# Luego irás agregando más, por ejemplo:
# app.include_router(empresa_router.router)
# app.include_router(supervisor_router.router)
# app.include_router(deteccion_router.router)   ← para la IA

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

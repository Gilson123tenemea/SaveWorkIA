# app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.exc import SQLAlchemyError
from app.config import SessionLocal, Base, engine
from app.rutas import ejemplo

# Crear tablas (si no existen)
from app.modelos import ejemplo as modelo_ejemplo
Base.metadata.create_all(bind=engine)

app = FastAPI(title="SaveWorkIA")

# Configuración de CORS
origins = [
    "http://localhost:5173",  # tu frontend React
    "http://127.0.0.1:5173"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,       # o ["*"] para permitir todos
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Registrar router
app.include_router(ejemplo.router)

@app.get("/")
def root():
    try:
        db = SessionLocal()
        db.execute("SELECT 1")
        db.close()
        return {"message": "Proyecto SaveWorkIA funcionando",
                "db_status": "Conexión a la base de datos exitosa ✅"}
    except SQLAlchemyError as e:
        return {"message": "Proyecto SaveWorkIA funcionando",
                "db_status": f"No se pudo conectar a la base de datos: {e}"}

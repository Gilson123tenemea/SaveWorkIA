from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# --- Parámetros de conexión MySQL ---
DB_USER = "root"           # Usuario
DB_PASSWORD = ""           # Contraseña
DB_HOST = "localhost"      # Host
DB_NAME = "saveworkdb"     # Base de datos

# Construir la URL de conexión para MySQL
SQLALCHEMY_DATABASE_URL = f"mysql+mysqlconnector://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}"

# --- Conexión ---
try:
    engine = create_engine(SQLALCHEMY_DATABASE_URL)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base = declarative_base()
    print("Conexión a la base de datos exitosa ✅")  # Mensaje en consola
except Exception as e:
    print(f"No se pudo conectar a la base de datos: {e}")  # Mensaje en consola

# Función helper para obtener sesión
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

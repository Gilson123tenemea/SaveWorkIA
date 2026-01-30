import os
from sqlalchemy import create_engine, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

load_dotenv()

# ====================================0===00#
# ====== OBTENER VARIABLES DE ENTORNO ======
DB_USER = os.getenv("DB_USER", "root")
DB_PASSWORD = os.getenv("DB_PASSWORD", "1234")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "3306")
DB_NAME = os.getenv("DB_NAME", "saveworkdboriginal8")

# ====== CONSTRUIR URL DE CONEXIÓN ======
SQLALCHEMY_DATABASE_URL = f"mysql+mysqlconnector://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

print(f"🔌 Conectando a: {DB_HOST}:{DB_PORT}/{DB_NAME}")

# ====== CREAR ENGINE Y SESIÓN ======
try:
    engine = create_engine(
        SQLALCHEMY_DATABASE_URL,
        echo=False,
        pool_size=10,
        max_overflow=20,
        pool_recycle=3600,
        pool_pre_ping=True
    )
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base = declarative_base()
    print("✅ Conexión a MySQL exitosa")
except Exception as e:
    print(f"❌ Error en conexión a MySQL: {e}")
    raise

# ====== FUNCIÓN PARA OBTENER SESIÓN ======
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
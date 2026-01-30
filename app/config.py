import os
from sqlalchemy import create_engine, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

load_dotenv()
#===========================================#
# ====== OBTENER VARIABLES DE ENTORNO ======
DB_USER = os.getenv("DB_USER", "azureuser")
DB_PASSWORD = os.getenv("DB_PASSWORD", "datadase2026!Secure")
DB_HOST = os.getenv("DB_HOST", "saveworkia-sqlserver.database.windows.net")
DB_PORT = os.getenv("DB_PORT", "1433")
DB_NAME = os.getenv("DB_NAME", "saveworkdboriginal8")

# ====== CONSTRUIR URL DE CONEXIÓN PARA MSSQL ======
# Usar pyodbc driver para SQL Server en Azure
SQLALCHEMY_DATABASE_URL = f"mssql+pyodbc://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:1433/{DB_NAME}?driver=ODBC+Driver+17+for+SQL+Server"

print(f"🔌 Conectando a: {DB_HOST}:{DB_PORT}/{DB_NAME}")

# ====== CREAR ENGINE Y SESIÓN ======
try:
    engine = create_engine(
        SQLALCHEMY_DATABASE_URL,
        echo=False,
        pool_size=10,
        max_overflow=20,
        pool_recycle=3600,
        pool_pre_ping=True,
        connect_args={
            "check_same_thread": False,
            "timeout": 30
        }
    )
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base = declarative_base()
    print("✅ Conexión a SQL Server exitosa")
except Exception as e:
    print(f"❌ Error en conexión a SQL Server: {e}")
    raise

# ====== FUNCIÓN PARA OBTENER SESIÓN ======
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
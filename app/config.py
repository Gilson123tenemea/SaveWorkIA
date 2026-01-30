import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
from urllib.parse import quote_plus
from sqlalchemy import text

load_dotenv()

# ====== VARIABLES DE ENTORNO ======
DB_USER = os.getenv("DB_USER", "azureuser")
DB_PASSWORD = os.getenv("DB_PASSWORD", "datadase2026!Secure")
DB_HOST = os.getenv("DB_HOST", "saveworkia-sqlserver.database.windows.net")
DB_PORT = os.getenv("DB_PORT", "1433")
DB_NAME = os.getenv("DB_NAME", "saveworkdboriginal8")

# ====== CODIFICAR CONTRASEÑA ======
password_encoded = quote_plus(DB_PASSWORD)

# ====== URL DE CONEXIÓN ======
SQLALCHEMY_DATABASE_URL = (
    f"mssql+pyodbc://{DB_USER}:{password_encoded}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    f"?driver=ODBC+Driver+17+for+SQL+Server"
    f"&Encrypt=yes"
    f"&TrustServerCertificate=no"
    f"&Connection+Timeout=30"
)

print(f"🔌 Configuración DB: {DB_HOST}/{DB_NAME}")

# ====== CREAR ENGINE (SIN PROBAR CONEXIÓN AÚN) ======
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    echo=False,
    pool_size=5,
    max_overflow=10,
    pool_recycle=3600,
    pool_pre_ping=True,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

print("✅ Engine de SQLAlchemy creado")

# ====== FUNCIÓN PARA VERIFICAR CONEXIÓN ======
def verificar_conexion():
    """Verifica conexión a la base de datos"""
    try:
        with engine.connect() as conn:
            result = conn.execute(text("SELECT @@VERSION")) 
            version = result.fetchone()[0]
            print(f"✅ Conexión a Azure SQL exitosa")
            print(f"📌 {version[:80]}...")
            return True
    except Exception as e:
        print(f"⚠️ Error SQL Server: {str(e)[:150]}")
        return False

# ====== FUNCIÓN PARA OBTENER SESIÓN ======
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
import pyodbc
from sqlalchemy import create_engine, MetaData
from urllib.parse import quote_plus

# Configuración
server = 'saveworkia-sqlserver.database.windows.net'
database = 'saveworkdboriginal8'
username = 'azureuser'
password = 'datadase2026!Secure'

# 1. VERIFICAR TABLAS EXISTENTES
print("="*60)
print("🔍 VERIFICANDO TABLAS EXISTENTES")
print("="*60)

connection_string = (
    f"DRIVER={{ODBC Driver 17 for SQL Server}};"
    f"SERVER={server};"
    f"DATABASE={database};"
    f"UID={username};"
    f"PWD={password};"
    f"Encrypt=yes;"
    f"TrustServerCertificate=no;"
)

try:
    conn = pyodbc.connect(connection_string)
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT TABLE_NAME 
        FROM INFORMATION_SCHEMA.TABLES 
        WHERE TABLE_TYPE = 'BASE TABLE'
        ORDER BY TABLE_NAME
    """)
    
    tables = [row[0] for row in cursor.fetchall()]
    
    if tables:
        print(f"\n✅ Se encontraron {len(tables)} tablas:")
        for table in tables:
            print(f"   - {table}")
    else:
        print("\n⚠️ No se encontraron tablas en la base de datos")
    
    conn.close()
    
except Exception as e:
    print(f"\n❌ Error al conectar: {e}")
    exit(1)

# 2. CREAR TABLAS CON SQLALCHEMY
print("\n" + "="*60)
print("📋 CREANDO TABLAS CON SQLALCHEMY")
print("="*60)

try:
    # Importar modelos
    from app.config import Base, engine
    
    # Importar TODOS los modelos
    from app.modelos import (
        persona, administrador, supervisor, inspector, trabajador,
        empresa_modelo, zona_modelo, camara_modelo, alerta_modelo,
        evento_deteccion_modelo, reporte, revision_reporte_modelo,
        registrosupervisorinspector, inspector_reporte, inspector_zona,
        trabajador_zona, registros_asistencia, evidencias_fallo,
        zona_epp, token_reset_modelo, fcm_token_modelo
    )
    
    print("\n📦 Modelos importados correctamente")
    print(f"📊 Tablas a crear: {len(Base.metadata.tables)}")
    
    # Crear todas las tablas
    Base.metadata.create_all(bind=engine)
    
    print("\n✅ Tablas creadas exitosamente")
    
except Exception as e:
    print(f"\n❌ Error al crear tablas: {e}")
    import traceback
    traceback.print_exc()

# 3. VERIFICAR NUEVAMENTE
print("\n" + "="*60)
print("🔍 VERIFICACIÓN FINAL")
print("="*60)

try:
    conn = pyodbc.connect(connection_string)
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT TABLE_NAME 
        FROM INFORMATION_SCHEMA.TABLES 
        WHERE TABLE_TYPE = 'BASE TABLE'
        ORDER BY TABLE_NAME
    """)
    
    tables = [row[0] for row in cursor.fetchall()]
    
    print(f"\n✅ Total de tablas: {len(tables)}")
    for table in tables:
        print(f"   - {table}")
    
    conn.close()
    
except Exception as e:
    print(f"\n❌ Error: {e}")

print("\n" + "="*60)
print("✅ PROCESO COMPLETADO")
print("="*60)
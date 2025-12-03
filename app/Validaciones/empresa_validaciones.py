from fastapi import HTTPException
import re
from sqlalchemy.orm import Session
from app.modelos.empresa_modelo import Empresa
from app.modelos.zona_modelo import Zona


# =============================
# 📌 VALIDAR NOMBRE (LETRAS + LONGITUD)
# =============================
def validar_nombre_empresa(nombre: str):
    if not nombre or nombre.strip() == "":
        raise HTTPException(400, "El nombre de la empresa es obligatorio")

    if len(nombre) < 3:
        raise HTTPException(400, "El nombre debe tener al menos 3 caracteres")

    if len(nombre) > 50:
        raise HTTPException(400, "El nombre no puede superar los 50 caracteres")

    if not re.match(r"^[a-zA-ZÁÉÍÓÚáéíóúÑñ ]+$", nombre):
        raise HTTPException(400, "El nombre solo debe contener letras y espacios")


# =============================
# 📌 VALIDAR TELÉFONO (10 DÍGITOS – ECUADOR)
# =============================
def validar_telefono_empresa(telefono: str):
    if not re.match(r"^\d{10}$", telefono):
        raise HTTPException(400, "El teléfono debe tener exactamente 10 dígitos numéricos")

    if not telefono.startswith("09"):
        raise HTTPException(400, "El teléfono debe iniciar con 09 (Ecuador)")


# =============================
# 📌 VALIDAR RUC (13 DÍGITOS)
# =============================
def validar_ruc_empresa(ruc: str):
    if not re.match(r"^\d{13}$", ruc):
        raise HTTPException(400, "El RUC debe contener exactamente 13 números")

    if not ruc[0].isdigit():
        raise HTTPException(400, "El RUC no puede iniciar con caracteres no válidos")


# =============================
# 📌 VALIDAR CORREO FORMATO PROFESIONAL
# =============================
def validar_formato_correo(correo: str):
    pattern = r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$"

    if not re.match(pattern, correo):
        raise HTTPException(
            status_code=400,
            detail="El correo electrónico no tiene un formato válido"
        )


# =============================
# 📌 VALIDAR CORREO ÚNICO
# =============================
def validar_correo_unico(db: Session, correo: str, empresa_id: int = None):

    validar_formato_correo(correo)

    query = db.query(Empresa).filter(
        Empresa.correo == correo,
        Empresa.borrado == True
    )

    if empresa_id:
        query = query.filter(Empresa.id_Empresa != empresa_id)

    if query.first():
        raise HTTPException(400, "El correo ya está registrado")


# =============================
# 📌 VALIDAR RUC ÚNICO
# =============================
def validar_ruc_unico(db: Session, ruc: str, empresa_id: int = None):

    query = db.query(Empresa).filter(
        Empresa.ruc == ruc,
        Empresa.borrado == True
    )

    if empresa_id:
        query = query.filter(Empresa.id_Empresa != empresa_id)

    if query.first():
        raise HTTPException(400, "El RUC ya está registrado")


# =============================
# 📌 VALIDAR ELIMINACIÓN CON RELACIONES
# =============================
def validar_relaciones_empresa(db: Session, empresa_id: int):
    """Evita eliminar empresas con relaciones activas"""

    # 🔍 Verificar zonas asociadas
    zonas = db.query(Zona).filter(
        Zona.id_empresa_zona == empresa_id,
        Zona.borrado == True
    ).first()

    if zonas:
        raise HTTPException(
            400,
            "No se puede eliminar la empresa porque tiene zonas registradas"
        )

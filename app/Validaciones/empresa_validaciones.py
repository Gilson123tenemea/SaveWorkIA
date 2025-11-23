from fastapi import HTTPException
import re
from sqlalchemy.orm import Session
from app.modelos.empresa_modelo import Empresa


# =============================
# 📌 VALIDAR NOMBRE
# =============================
def validar_nombre_empresa(nombre: str):
    if not nombre or nombre.strip() == "":
        raise HTTPException(
            status_code=400,
            detail="El nombre de la empresa es obligatorio"
        )

    if not re.match(r"^[a-zA-ZÁÉÍÓÚáéíóúÑñ ]+$", nombre):
        raise HTTPException(
            status_code=400,
            detail="El nombre solo debe contener letras y espacios"
        )


# =============================
# 📌 VALIDAR TELÉFONO
# =============================
def validar_telefono_empresa(telefono: str):
    if not re.match(r"^\d{10}$", telefono):
        raise HTTPException(
            status_code=400,
            detail="El teléfono debe tener exactamente 10 dígitos numéricos"
        )


# =============================
# 📌 VALIDAR RUC
# =============================
def validar_ruc_empresa(ruc: str):
    if not re.match(r"^\d{13}$", ruc):
        raise HTTPException(
            status_code=400,
            detail="El RUC debe contener exactamente 13 números"
        )


# =============================
# 📌 VALIDAR CORREO ÚNICO (Crear y Editar)
# =============================
def validar_correo_unico(db: Session, correo: str, empresa_id: int = None):
    query = db.query(Empresa).filter(
        Empresa.correo == correo,
        Empresa.borrado == True
    )

    # Ignorar el correo de la empresa que se está editando
    if empresa_id:
        query = query.filter(Empresa.id_Empresa != empresa_id)

    empresa = query.first()

    if empresa:
        raise HTTPException(
            status_code=400,
            detail="El correo ya está registrado"
        )


# =============================
# 📌 VALIDAR RUC ÚNICO (Crear y Editar)
# =============================
def validar_ruc_unico(db: Session, ruc: str, empresa_id: int = None):
    query = db.query(Empresa).filter(
        Empresa.ruc == ruc,
        Empresa.borrado == True
    )

    # Ignorar el RUC de la misma empresa si está editando
    if empresa_id:
        query = query.filter(Empresa.id_Empresa != empresa_id)

    empresa = query.first()

    if empresa:
        raise HTTPException(
            status_code=400,
            detail="El RUC ya está registrado"
        )

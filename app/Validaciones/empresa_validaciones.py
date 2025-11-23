from fastapi import HTTPException, status
import re

# =============================
# 📌 VALIDAR NOMBRE (solo letras)
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
# 📌 VALIDAR TELÉFONO (solo números, 10 dígitos)
# =============================
def validar_telefono_empresa(telefono: str):
    if not re.match(r"^\d{10}$", telefono):
        raise HTTPException(
            status_code=400,
            detail="El teléfono debe tener exactamente 10 dígitos numéricos"
        )

# =============================
# 📌 VALIDAR RUC (solo números, 13 dígitos)
# =============================
def validar_ruc_empresa(ruc: str):
    if not re.match(r"^\d{13}$", ruc):
        raise HTTPException(
            status_code=400,
            detail="El RUC debe contener exactamente 13 números"
        )

# =============================
# 📌 VALIDAR CORREO ÚNICO
# =============================
def validar_correo_unico(db, correo: str):
    from app.modelos.empresa_modelo import Empresa

    empresa = db.query(Empresa).filter(
        Empresa.correo == correo,
        Empresa.borrado == True
    ).first()

    if empresa:
        raise HTTPException(
            status_code=400,
            detail="El correo ya está registrado"
        )

# =============================
# 📌 VALIDAR RUC ÚNICO CON BORRADO LÓGICO
# =============================
def validar_ruc_unico(db, ruc: str):
    from app.modelos.empresa_modelo import Empresa

    empresa = db.query(Empresa).filter(
        Empresa.ruc == ruc,
        Empresa.borrado == True
    ).first()

    if empresa:
        raise HTTPException(
            status_code=400,
            detail="El RUC ya está registrado"
        )

# app/validaciones/zona_validaciones.py

from fastapi import HTTPException, status
import re


# ================================
# ✔ VALIDAR NOMBRE DE ZONA
# ================================
def validar_nombre_zona(nombre: str):
    if not nombre or nombre.strip() == "":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El nombre de la zona es obligatorio"
        )

    # 🔹 Solo letras, números y espacios
    patron = r"^[A-Za-z0-9ÁÉÍÓÚáéíóúÑñ ]+$"

    if not re.match(patron, nombre):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El nombre solo puede contener letras, números y espacios"
        )

    if len(nombre.strip()) < 3:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El nombre de la zona debe tener mínimo 3 caracteres"
        )


# ================================
# ✔ VALIDAR COORDENADAS
# ================================
def validar_coordenada(valor: str, nombre_campo: str):
    if not valor or valor.strip() == "":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"La {nombre_campo} es obligatoria"
        )

    # 🔹 Validar si es número válido
    try:
        float(valor)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"La {nombre_campo} debe ser un número válido"
        )

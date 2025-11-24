# app/Validaciones/camara_validaciones.py
from fastapi import HTTPException, status
import re

def campo_obligatorio(valor: str | None, nombre: str):
    if valor is None or str(valor).strip() == "":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"El campo '{nombre}' es obligatorio"
        )

def validar_codigo_camara(codigo: str):
    campo_obligatorio(codigo, "Nombre o código de cámara")

    # Letras, números, guiones y guion bajo
    if not re.fullmatch(r"[A-Za-z0-9_\-]+", codigo):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El código de la cámara solo puede contener letras, números, guiones y guion bajo"
        )

    if len(codigo) > 10:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El código de la cámara no puede superar los 10 caracteres"
        )

def validar_ip(ip: str):
    campo_obligatorio(ip, "Dirección IP")

    patron = r"^(25[0-5]|2[0-4]\d|1?\d?\d)(\.(25[0-5]|2[0-4]\d|1?\d?\d)){3}$"
    if not re.fullmatch(patron, ip.strip()):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="La dirección IP no tiene un formato IPv4 válido"
        )

def validar_tipo_camara(tipo: str):
    campo_obligatorio(tipo, "Tipo de cámara")

    tipos_permitidos = {"IP", "Domo", "Bullet", "PTZ"}
    if tipo not in tipos_permitidos:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Tipo de cámara inválido. Valores permitidos: {', '.join(tipos_permitidos)}"
        )

def validar_estado_camara(estado: str):
    campo_obligatorio(estado, "Estado de la cámara")

    estados_permitidos = {"activa", "inactiva", "mantenimiento", "desconectada"}
    if estado not in estados_permitidos:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Estado de cámara inválido. Valores permitidos: {', '.join(estados_permitidos)}"
        )

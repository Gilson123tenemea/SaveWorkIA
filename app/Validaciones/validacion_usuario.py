import re
from datetime import date
from fastapi import HTTPException
from sqlalchemy.orm import Session
from app.modelos.persona import Persona


# ============================================================
# ✔ CAMPOS OBLIGATORIOS
# ============================================================
def campo_obligatorio(valor, nombre_campo):
    if valor is None or str(valor).strip() == "":
        raise HTTPException(400, f"El campo '{nombre_campo}' es obligatorio")


# ============================================================
# ✔ CÉDULA ECUATORIANA
# ============================================================
def validar_cedula_ecuatoriana(cedula: str):
    campo_obligatorio(cedula, "cédula")

    if not cedula.isdigit():
        raise HTTPException(400, "La cédula solo debe contener números")

    if len(cedula) != 10:
        raise HTTPException(400, "La cédula debe tener exactamente 10 dígitos")

    provincia = int(cedula[:2])
    if not (1 <= provincia <= 24):
        raise HTTPException(400, "La cédula no pertenece a una provincia válida")

    coef = [2,1,2,1,2,1,2,1,2]
    suma = 0
    for i in range(9):
        valor = int(cedula[i]) * coef[i]
        if valor > 9:
            valor -= 9
        suma += valor

    digito_valido = (10 - (suma % 10)) % 10

    if digito_valido != int(cedula[9]):
        raise HTTPException(400, "La cédula ecuatoriana no es válida")


# ============================================================
# ✔ CÉDULA ÚNICA (RESPETA BORRADO LÓGICO)
# ============================================================
def validar_cedula_unica(db: Session, cedula: str):
    existente = db.query(Persona).filter(
        Persona.cedula == cedula,
        Persona.borrado == True
    ).first()

    if existente:
        raise HTTPException(400, "Ya existe un usuario activo con esta cédula")


# ============================================================
# ✔ NOMBRE
# ============================================================
def validar_nombre(nombre: str):
    campo_obligatorio(nombre, "nombre")

    patron = r"^[A-Za-zÁÉÍÓÚáéíóúñÑ ]{2,50}$"
    if not re.match(patron, nombre):
        raise HTTPException(400, "El nombre solo puede contener letras y espacios (2–50 caracteres)")


# ============================================================
# ✔ APELLIDO
# ============================================================
def validar_apellido(apellido: str):
    campo_obligatorio(apellido, "apellido")

    patron = r"^[A-Za-zÁÉÍÓÚáéíóúñÑ ]{2,50}$"
    if not re.match(patron, apellido):
        raise HTTPException(400, "El apellido solo puede contener letras y espacios (2–50 caracteres)")


# ============================================================
# ✔ TELÉFONO
# ============================================================
def validar_telefono(telefono: str):
    campo_obligatorio(telefono, "teléfono")

    if not telefono.isdigit():
        raise HTTPException(400, "El teléfono solo debe contener números")

    if len(telefono) != 10:
        raise HTTPException(400, "El teléfono debe tener exactamente 10 dígitos")


# ============================================================
# ✔ CORREO
# ============================================================
def validar_correo_formato(correo: str):
    campo_obligatorio(correo, "correo")

    patron = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[A-Za-z]{2,}$"

    if not re.match(patron, correo):
        raise HTTPException(400, "El formato del correo electrónico no es válido")


def validar_correo_unico(db: Session, correo: str):
    existente = db.query(Persona).filter(
        Persona.correo == correo,
        Persona.borrado == True
    ).first()

    if existente:
        raise HTTPException(400, "Ya existe un usuario activo con este correo")


# ============================================================
# ✔ DIRECCIÓN
# ============================================================
def validar_direccion(direccion: str):
    campo_obligatorio(direccion, "dirección")

    patron = r"^[A-Za-z0-9ÁÉÍÓÚáéíóúñÑ #.,-]{5,100}$"

    if not re.match(patron, direccion):
        raise HTTPException(400, "La dirección contiene caracteres no permitidos o es demasiado corta")


# ============================================================
# ✔ GÉNERO
# ============================================================
def validar_genero(genero: str):
    campo_obligatorio(genero, "género")

    if genero not in ["Masculino", "Femenino"]:
        raise HTTPException(400, "Debe seleccionar un género válido")


# ============================================================
# ✔ FECHA NACIMIENTO (MAYOR 18)
# ============================================================
def validar_fecha_nacimiento(fecha_nacimiento: date):
    campo_obligatorio(fecha_nacimiento, "fecha de nacimiento")

    hoy = date.today()
    edad = hoy.year - fecha_nacimiento.year - (
        (hoy.month, hoy.day) < (fecha_nacimiento.month, fecha_nacimiento.day)
    )

    if edad < 18:
        raise HTTPException(400, "El usuario debe ser mayor de 18 años")


# ============================================================
# ✔ ESPECIALIDAD
# ============================================================
def validar_especialidad(especialidad: str):
    campo_obligatorio(especialidad, "especialidad")

    patron = r"^[A-Za-zÁÉÍÓÚáéíóúñÑ ()/-]{3,50}$"

    if not re.match(patron, especialidad):
        raise HTTPException(400, "La especialidad contiene caracteres no permitidos")


# ============================================================
# ✔ EXPERIENCIA
# ============================================================
def validar_experiencia(exp):
    campo_obligatorio(exp, "experiencia")

    try:
        exp = int(exp)
    except:
        raise HTTPException(400, "La experiencia debe ser un número entero")

    if exp < 1 or exp > 80:
        raise HTTPException(400, "La experiencia debe estar entre 1 y 80 años")


# ============================================================
# ✔ CONTRASEÑA SEGURA
# ============================================================
def validar_contrasena(contrasena: str):
    campo_obligatorio(contrasena, "contraseña")

    if len(contrasena) < 8:
        raise HTTPException(400, "La contraseña debe tener mínimo 8 caracteres")

    patron = r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*#?&]).+$"

    if not re.match(patron, contrasena):
        raise HTTPException(
            400,
            "La contraseña debe tener mayúsculas, minúsculas, números y caracteres especiales"
        )

# ============================
# VALIDAR ZONA ASIGNADA
# ============================
def validar_zona_asignada(zona: str):
    if zona is None or zona.strip() == "":
        raise HTTPException(status_code=400, detail="La zona asignada es obligatoria")

    if len(zona) < 3:
        raise HTTPException(status_code=400, detail="La zona asignada debe tener al menos 3 caracteres")

    if len(zona) > 50:
        raise HTTPException(status_code=400, detail="La zona asignada no puede superar los 50 caracteres")


# ============================
# VALIDAR FRECUENCIA DE VISITA
# ============================
def validar_frecuencia_visita(freq: str):
    if freq is None or freq.strip() == "":
        raise HTTPException(status_code=400, detail="La frecuencia de visita es obligatoria")

    if len(freq) < 3:
        raise HTTPException(status_code=400, detail="La frecuencia de visita debe tener al menos 3 caracteres")

    if len(freq) > 30:
        raise HTTPException(status_code=400, detail="La frecuencia de visita no puede superar los 30 caracteres")

def validar_cargo(cargo: str):
    campo_obligatorio(cargo, "cargo")

    patron = r"^[A-Za-zÁÉÍÓÚáéíóúñÑ ]{3,50}$"
    if not re.match(patron, cargo):
        raise HTTPException(400, "El cargo solo puede contener letras y espacios (3–50 caracteres)")

def validar_area_trabajo(area: str):
    campo_obligatorio(area, "área de trabajo")

    patron = r"^[A-Za-z0-9ÁÉÍÓÚáéíóúñÑ ]{3,50}$"
    if not re.match(patron, area):
        raise HTTPException(400, "El área de trabajo solo puede contener letras, números y espacios (3–50 caracteres)")

def validar_implementos(impl: str):
    campo_obligatorio(impl, "implementos de seguridad")

    if len(impl) < 3:
        raise HTTPException(400, "Los implementos deben tener mínimo 3 caracteres")

def validar_estado_trabajador(estado):
    # Si es booleano → convertirlo correctamente
    if isinstance(estado, bool):
        return  # válido (True/False)

    # Si llega string → validar como antes
    if estado not in ["activo", "inactivo"]:
        raise HTTPException(
            status_code=400,
            detail="El estado debe ser 'activo' o 'inactivo'"
        )


def validar_codigo_trabajador(codigo: str):
    campo_obligatorio(codigo, "código trabajador")

    patron = r"^TRA-\d{3}$"
    if not re.match(patron, codigo):
        raise HTTPException(
            400,
            "El código debe tener el formato TRA-001"
        )

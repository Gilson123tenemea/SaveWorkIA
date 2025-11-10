import bcrypt

# Generar hash
def encriptar_contrasena(contrasena: str) -> str:
    salt = bcrypt.gensalt()
    contrasena_hash = bcrypt.hashpw(contrasena.encode('utf-8'), salt)
    return contrasena_hash.decode('utf-8')

# Verificar contraseña
def verificar_contrasena(contrasena_plana: str, contrasena_hash: str) -> bool:
    return bcrypt.checkpw(contrasena_plana.encode('utf-8'), contrasena_hash.encode('utf-8'))

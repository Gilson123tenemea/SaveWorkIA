from sqlalchemy.orm import Session
from datetime import date
from typing import Optional
from fastapi import HTTPException, status
from app.modelos.persona import Persona
from app.modelos.administrador import Administrador
from app.esquemas.administrador_esquema import AdministradorCreate, LoginAdministrador
from app.seguridad.hash_contrasena import encriptar_contrasena, verificar_contrasena
from app.servicios.log_service import LogServicio

def crear_administrador(db: Session, datos: AdministradorCreate):
    """Crear administrador con log"""
    try:
        if db.query(Persona).filter(Persona.cedula == datos.persona.cedula).first():
            raise HTTPException(status_code=400, detail="La cédula ya está registrada")
        if db.query(Persona).filter(Persona.correo == datos.persona.correo).first():
            raise HTTPException(status_code=400, detail="El correo ya está registrado")

        contrasena_encriptada = encriptar_contrasena(datos.persona.contrasena)

        nueva_persona = Persona(
            cedula=datos.persona.cedula,
            nombre=datos.persona.nombre,
            apellido=datos.persona.apellido,
            telefono=datos.persona.telefono,
            correo=datos.persona.correo,
            direccion=datos.persona.direccion,
            genero=datos.persona.genero,
            fecha_nacimiento=datos.persona.fecha_nacimiento,
            contrasena=contrasena_encriptada,
            rol="admin",
            borrado=True
        )
        db.add(nueva_persona)
        db.commit()
        db.refresh(nueva_persona)

        nuevo_admin = Administrador(
            ultima_conexion=datos.ultima_conexion,
            fechaRegistroSistema=date.today(),
            borrado=True,
            id_persona_administrador=nueva_persona.id_persona
        )
        db.add(nuevo_admin)
        db.commit()
        db.refresh(nuevo_admin)

        # 📝 LOG: Registro exitoso
        import asyncio
        asyncio.create_task(
            LogServicio.registrar_accion_negocio(
                source="administrador_servicio",
                accion="registro_admin",
                user_id=nueva_persona.id_persona,
                user_role="admin",
                estado="success",
                mensaje=f"Administrador registrado: {nueva_persona.correo}",
                metadata={
                    "cedula": datos.persona.cedula,
                    "nombre": f"{datos.persona.nombre} {datos.persona.apellido}"
                }
            )
        )

        return {
            "id_administrador": nuevo_admin.id_administrador,
            "id_persona": nueva_persona.id_persona,
            "nombre": nueva_persona.nombre,
            "apellido": nueva_persona.apellido,
            "correo": nueva_persona.correo,
            "fechaRegistroSistema": nuevo_admin.fechaRegistroSistema,
            "borrado": nuevo_admin.borrado
        }
    
    except HTTPException as e:
        # 📝 LOG: Error conocido
        import asyncio
        asyncio.create_task(
            LogServicio.registrar_error(
                source="administrador_servicio",
                accion="registro_admin",
                error_message=str(e.detail),
                metadata={"cedula": datos.persona.cedula}
            )
        )
        raise
    except Exception as e:
        # 📝 LOG: Error inesperado
        import asyncio
        asyncio.create_task(
            LogServicio.registrar_error(
                source="administrador_servicio",
                accion="registro_admin",
                error_message=str(e)
            )
        )
        raise


async def login_administrador(db: Session, datos: LoginAdministrador, ip_address: Optional[str] = None):
    """Login administrador con log completo"""
    try:
        persona = db.query(Persona).filter(Persona.correo == datos.correo).first()

        if not persona:
            # 📝 LOG: Login fallido - correo no existe
            await LogServicio.registrar_autenticacion(
                source="administrador_servicio",
                accion="login_fallido",
                correo=datos.correo,
                estado="failed",
                ip_address=ip_address,
                error="Correo no registrado"
            )
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Correo o contraseña incorrectos"
            )

        if not persona.borrado:
            # 📝 LOG: Login fallido - usuario inactivo
            await LogServicio.registrar_autenticacion(
                source="administrador_servicio",
                accion="login_fallido",
                correo=datos.correo,
                estado="failed",
                user_id=persona.id_persona,
                ip_address=ip_address,
                error="Usuario inactivo"
            )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Usuario inactivo o sin permisos"
            )

        if not verificar_contrasena(datos.contrasena, persona.contrasena):
            # 📝 LOG: Login fallido - contraseña incorrecta
            await LogServicio.registrar_autenticacion(
                source="administrador_servicio",
                accion="login_fallido",
                correo=datos.correo,
                estado="failed",
                user_id=persona.id_persona,
                ip_address=ip_address,
                error="Contraseña incorrecta"
            )
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Correo o contraseña incorrectos"
            )

        admin = db.query(Administrador).filter(
            Administrador.id_persona_administrador == persona.id_persona,
            Administrador.borrado == True
        ).first()

        if not admin:
            # 📝 LOG: Login fallido - no es administrador
            await LogServicio.registrar_autenticacion(
                source="administrador_servicio",
                accion="login_fallido",
                correo=datos.correo,
                estado="failed",
                user_id=persona.id_persona,
                ip_address=ip_address,
                error="Usuario no es administrador"
            )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="El usuario no es administrador"
            )

        admin.ultima_conexion = date.today()
        db.commit()

        # 📝 LOG: Login exitoso
        await LogServicio.registrar_autenticacion(
            source="administrador_servicio",
            accion="login_exitoso",
            correo=datos.correo,
            estado="success",
            user_id=persona.id_persona,
            ip_address=ip_address,
            mensaje=f"Login exitoso para {datos.correo}",
            metadata={
                "id_administrador": admin.id_administrador,
                "nombre": persona.nombre
            }
        )

        return {
            "mensaje": "Inicio de sesión exitoso",
            "id_administrador": admin.id_administrador,
            "nombre": persona.nombre,
            "correo": persona.correo,
            "role": persona.rol,
            "ultima_conexion": admin.ultima_conexion
        }
    
    except HTTPException:
        raise
    except Exception as e:
        # 📝 LOG: Error inesperado durante login
        await LogServicio.registrar_error(
            source="administrador_servicio",
            accion="login",
            error_message=str(e),
            ip_address=ip_address
        )
        raise

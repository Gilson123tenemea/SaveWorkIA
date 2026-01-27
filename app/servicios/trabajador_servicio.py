from sqlalchemy.orm import Session
from app.modelos.trabajador import Trabajador
from app.modelos.persona import Persona
from app.esquemas.trabajador_esquema import TrabajadorPersonaCreate
from fastapi import HTTPException
from app.seguridad.hash_contrasena import encriptar_contrasena, verificar_contrasena
from sqlalchemy.orm import joinedload
from app.modelos.trabajador_zona import TrabajadorZona
from app.modelos.zona_modelo import Zona
from app.modelos.camara_modelo import Camara
from app.modelos.inspector_zona import InspectorZona
from app.modelos.inspector import Inspector
from datetime import date
from sqlalchemy import func

from app.Validaciones.validacion_usuario import (
    validar_cedula_ecuatoriana,
    validar_cedula_unica,
    validar_nombre,
    validar_apellido,
    validar_telefono,
    validar_correo_unico,
    validar_direccion,
    validar_genero,
    validar_fecha_nacimiento,
    validar_contrasena,
    validar_cargo,
    validar_implementos,
    validar_estado_trabajador,
    validar_codigo_trabajador,
    validar_correo_formato
)

# Importar servicio de logs
from app.servicios.log_service import LogServicio


def codigo_existe_activo(db: Session, codigo: str, id_empresa: int):
    trabajador = db.query(Trabajador).filter(
        Trabajador.codigo_trabajador == codigo,
        Trabajador.id_empresa == id_empresa,
        Trabajador.borrado == True
    ).first()
    return trabajador is not None


def cedula_existe_activa(db: Session, cedula: str):
    persona = db.query(Persona).filter(Persona.cedula == cedula).first()
    if not persona:
        return False  
    if persona.borrado is False:
        return False  
    return True  


def correo_existe_activo(db: Session, correo: str) -> bool:
    persona = db.query(Persona).filter(
        Persona.correo == correo,
        Persona.borrado == True  
    ).first()
    return persona is not None


async def crear_trabajador_completo(db: Session, data: TrabajadorPersonaCreate, ip_address: str = None):
    try:
        # Validar formato de cédula
        validar_cedula_ecuatoriana(data.persona.cedula)

        # Buscar persona por cédula
        persona_existente = db.query(Persona).filter(
            Persona.cedula == data.persona.cedula
        ).first()

        # CASO A: PERSONA EXISTE Y ESTÁ ACTIVA
        if persona_existente and persona_existente.borrado is True:
            await LogServicio.registrar_accion_negocio(
                source="trabajador_servicio.crear_trabajador_completo",
                accion="intento_crear_trabajador_duplicado",
                estado="failed",
                mensaje=f"Intento de crear trabajador con cédula duplicada: {data.persona.cedula}",
                ip_address=ip_address,
                metadata={
                    "cedula": data.persona.cedula,
                    "codigo_trabajador": data.trabajador.codigo_trabajador,
                    "id_empresa": data.trabajador.id_empresa
                }
            )
            raise HTTPException(
                status_code=400,
                detail="Ya existe un trabajador activo con esta cédula"
            )

        # CASO B: PERSONA EXISTE PERO ESTÁ INACTIVA - REACTIVACIÓN
        if persona_existente and persona_existente.borrado is False:
            persona = persona_existente

            # Validaciones completas
            validar_correo_formato(data.persona.correo)
            validar_nombre(data.persona.nombre)
            validar_apellido(data.persona.apellido)
            validar_telefono(data.persona.telefono)
            validar_direccion(data.persona.direccion)
            validar_genero(data.persona.genero)
            validar_fecha_nacimiento(data.persona.fecha_nacimiento)
            validar_contrasena(data.persona.contrasena)
            validar_cargo(data.trabajador.cargo)
            validar_implementos(data.trabajador.implementos_requeridos)
            validar_estado_trabajador(data.trabajador.estado)
            validar_codigo_trabajador(data.trabajador.codigo_trabajador)
            validar_codigo_unico(db, data.trabajador.codigo_trabajador, data.trabajador.id_empresa)

            # Reactivar persona
            persona.nombre = data.persona.nombre
            persona.apellido = data.persona.apellido
            persona.telefono = data.persona.telefono
            persona.correo = data.persona.correo
            persona.direccion = data.persona.direccion
            persona.genero = data.persona.genero
            persona.fecha_nacimiento = data.persona.fecha_nacimiento
            persona.contrasena = encriptar_contrasena(data.persona.contrasena)
            persona.rol = "trabajador"
            persona.borrado = True

            # Buscar trabajador asociado
            trabajador = db.query(Trabajador).filter(
                Trabajador.id_persona_trabajador == persona.id_persona
            ).first()

            if trabajador:
                trabajador.cargo = data.trabajador.cargo
                trabajador.implementos_requeridos = data.trabajador.implementos_requeridos
                trabajador.estado = data.trabajador.estado
                trabajador.codigo_trabajador = data.trabajador.codigo_trabajador
                trabajador.id_empresa = data.trabajador.id_empresa
                trabajador.id_supervisor_trabajador = data.trabajador.id_supervisor_trabajador
                trabajador.borrado = True
            else:
                trabajador = Trabajador(
                    cargo=data.trabajador.cargo,
                    implementos_requeridos=data.trabajador.implementos_requeridos,
                    estado=data.trabajador.estado,
                    codigo_trabajador=data.trabajador.codigo_trabajador,
                    id_empresa=data.trabajador.id_empresa,
                    id_supervisor_trabajador=data.trabajador.id_supervisor_trabajador,
                    id_persona_trabajador=persona.id_persona,
                    borrado=True
                )
                db.add(trabajador)

            db.commit()
            db.refresh(trabajador)

            # Log de reactivación exitosa
            await LogServicio.registrar_accion_negocio(
                source="trabajador_servicio.crear_trabajador_completo",
                accion="reactivar_trabajador",
                user_id=trabajador.id_trabajador,
                user_role="trabajador",
                estado="success",
                mensaje=f"Trabajador reactivado: {persona.nombre} {persona.apellido}",
                ip_address=ip_address,
                metadata={
                    "id_trabajador": trabajador.id_trabajador,
                    "cedula": persona.cedula,
                    "correo": persona.correo,
                    "codigo_trabajador": trabajador.codigo_trabajador,
                    "id_empresa": trabajador.id_empresa
                }
            )

            return trabajador

        # CASO C: PERSONA NO EXISTE - CREAR NUEVO
        validar_cedula_unica(db, data.persona.cedula)
        validar_correo_unico(db, data.persona.correo)
        validar_nombre(data.persona.nombre)
        validar_apellido(data.persona.apellido)
        validar_telefono(data.persona.telefono)
        validar_direccion(data.persona.direccion)
        validar_genero(data.persona.genero)
        validar_fecha_nacimiento(data.persona.fecha_nacimiento)
        validar_contrasena(data.persona.contrasena)
        validar_cargo(data.trabajador.cargo)
        validar_implementos(data.trabajador.implementos_requeridos)
        validar_estado_trabajador(data.trabajador.estado)
        validar_codigo_trabajador(data.trabajador.codigo_trabajador)
        validar_codigo_unico(db, data.trabajador.codigo_trabajador, data.trabajador.id_empresa)

        # Crear persona nueva
        persona = Persona(
            cedula=data.persona.cedula,
            nombre=data.persona.nombre,
            apellido=data.persona.apellido,
            telefono=data.persona.telefono,
            correo=data.persona.correo,
            direccion=data.persona.direccion,
            genero=data.persona.genero,
            fecha_nacimiento=data.persona.fecha_nacimiento,
            contrasena=encriptar_contrasena(data.persona.contrasena),
            rol="trabajador",
            borrado=True
        )
        db.add(persona)
        db.commit()
        db.refresh(persona)

        # Crear trabajador nuevo
        trabajador = Trabajador(
            cargo=data.trabajador.cargo,
            implementos_requeridos=data.trabajador.implementos_requeridos,
            estado=data.trabajador.estado,
            codigo_trabajador=data.trabajador.codigo_trabajador,
            id_empresa=data.trabajador.id_empresa,
            id_supervisor_trabajador=data.trabajador.id_supervisor_trabajador,
            id_persona_trabajador=persona.id_persona,
            borrado=True
        )

        db.add(trabajador)
        db.commit()
        db.refresh(trabajador)

        # Log de creación exitosa
        await LogServicio.registrar_accion_negocio(
            source="trabajador_servicio.crear_trabajador_completo",
            accion="crear_trabajador",
            user_id=trabajador.id_trabajador,
            user_role="trabajador",
            estado="success",
            mensaje=f"Nuevo trabajador creado: {persona.nombre} {persona.apellido}",
            ip_address=ip_address,
            metadata={
                "id_trabajador": trabajador.id_trabajador,
                "cedula": persona.cedula,
                "correo": persona.correo,
                "codigo_trabajador": trabajador.codigo_trabajador,
                "cargo": trabajador.cargo,
                "id_empresa": trabajador.id_empresa,
                "id_supervisor": trabajador.id_supervisor_trabajador
            }
        )

        return trabajador

    except HTTPException:
        raise
    except Exception as e:
        # Log de error
        await LogServicio.registrar_error(
            source="trabajador_servicio.crear_trabajador_completo",
            accion="crear_trabajador",
            error_message=str(e),
            ip_address=ip_address,
            metadata={
                "cedula": data.persona.cedula if data.persona else None,
                "correo": data.persona.correo if data.persona else None
            }
        )
        raise


def obtener_trabajadores_completos(db: Session):
    return db.query(Trabajador).join(Persona).all()


def validar_codigo_unico(db: Session, codigo: str, id_empresa: int):
    existe = db.query(Trabajador).filter(
        Trabajador.codigo_trabajador == codigo,
        Trabajador.id_empresa == id_empresa,
        Trabajador.borrado == True
    ).first()

    if existe:
        raise HTTPException(
            status_code=400,
            detail="Ya existe un trabajador activo con este código en esta empresa"
        )


def obtener_trabajador_completo(db: Session, id_trabajador: int):
    return (
        db.query(Trabajador)
        .join(Persona)
        .filter(Trabajador.id_trabajador == id_trabajador)
        .first()
    )


async def editar_trabajador_completo(db: Session, id_trabajador: int, data: TrabajadorPersonaCreate, ip_address: str = None):
    try:
        # Obtener trabajador + persona
        trabajador = db.query(Trabajador).filter(
            Trabajador.id_trabajador == id_trabajador,
            Trabajador.borrado == True
        ).first()

        if not trabajador:
            raise HTTPException(status_code=404, detail="Trabajador no encontrado")

        persona = db.query(Persona).filter(
            Persona.id_persona == trabajador.id_persona_trabajador,
            Persona.borrado == True
        ).first()

        if not persona:
            raise HTTPException(status_code=404, detail="Persona asociada no encontrada")

        # Guardar datos anteriores para el log
        datos_anteriores = {
            "nombre": persona.nombre,
            "apellido": persona.apellido,
            "correo": persona.correo,
            "cargo": trabajador.cargo,
            "codigo_trabajador": trabajador.codigo_trabajador
        }

        # VALIDACIONES PERSONA
        validar_nombre(data.persona.nombre)
        validar_apellido(data.persona.apellido)
        validar_telefono(data.persona.telefono)
        validar_direccion(data.persona.direccion)
        validar_genero(data.persona.genero)
        validar_fecha_nacimiento(data.persona.fecha_nacimiento)

        if data.persona.correo != persona.correo:
            validar_correo_formato(data.persona.correo)
            validar_correo_unico(db, data.persona.correo)

        if data.persona.contrasena:
            persona.contrasena = encriptar_contrasena(data.persona.contrasena)

        # VALIDACIONES TRABAJADOR
        validar_cargo(data.trabajador.cargo)
        validar_implementos(data.trabajador.implementos_requeridos)
        validar_estado_trabajador(data.trabajador.estado)

        if data.trabajador.codigo_trabajador != trabajador.codigo_trabajador:
            validar_codigo_trabajador(data.trabajador.codigo_trabajador)
            validar_codigo_unico(db, data.trabajador.codigo_trabajador, data.trabajador.id_empresa)

        if data.trabajador.id_empresa != trabajador.id_empresa:
            validar_codigo_unico(db, data.trabajador.codigo_trabajador, data.trabajador.id_empresa)

        # Actualizar PERSONA
        persona.nombre = data.persona.nombre
        persona.apellido = data.persona.apellido
        persona.telefono = data.persona.telefono
        persona.correo = data.persona.correo
        persona.direccion = data.persona.direccion
        persona.genero = data.persona.genero
        persona.fecha_nacimiento = data.persona.fecha_nacimiento

        # Actualizar TRABAJADOR
        trabajador.cargo = data.trabajador.cargo
        trabajador.implementos_requeridos = data.trabajador.implementos_requeridos
        trabajador.estado = data.trabajador.estado
        trabajador.codigo_trabajador = data.trabajador.codigo_trabajador

        db.commit()
        db.refresh(trabajador)

        # Log de edición exitosa
        await LogServicio.registrar_accion_negocio(
            source="trabajador_servicio.editar_trabajador_completo",
            accion="editar_trabajador",
            user_id=trabajador.id_trabajador,
            user_role="trabajador",
            estado="success",
            mensaje=f"Trabajador actualizado: {persona.nombre} {persona.apellido}",
            ip_address=ip_address,
            metadata={
                "id_trabajador": trabajador.id_trabajador,
                "cedula": persona.cedula,
                "correo_nuevo": persona.correo,
                "datos_anteriores": datos_anteriores,
                "datos_nuevos": {
                    "nombre": persona.nombre,
                    "apellido": persona.apellido,
                    "correo": persona.correo,
                    "cargo": trabajador.cargo,
                    "codigo_trabajador": trabajador.codigo_trabajador
                }
            }
        )

        return trabajador

    except HTTPException:
        raise
    except Exception as e:
        await LogServicio.registrar_error(
            source="trabajador_servicio.editar_trabajador_completo",
            accion="editar_trabajador",
            error_message=str(e),
            user_id=id_trabajador,
            ip_address=ip_address
        )
        raise


async def borrado_logico_trabajador(db: Session, id_trabajador: int, ip_address: str = None):
    try:
        trabajador = db.query(Trabajador).filter(
            Trabajador.id_trabajador == id_trabajador
        ).first()

        if not trabajador:
            raise HTTPException(
                status_code=404,
                detail="Trabajador no encontrado"
            )

        asignaciones = db.query(TrabajadorZona).filter(
            TrabajadorZona.id_trabajador_trabajadorzona == id_trabajador,
            TrabajadorZona.borrado == True
        ).count()

        if asignaciones > 0:
            await LogServicio.registrar_accion_negocio(
                source="trabajador_servicio.borrado_logico_trabajador",
                accion="intento_eliminar_trabajador_con_zonas",
                user_id=id_trabajador,
                estado="failed",
                mensaje=f"Intento de eliminar trabajador con {asignaciones} zonas asignadas",
                ip_address=ip_address,
                metadata={
                    "id_trabajador": id_trabajador,
                    "zonas_asignadas": asignaciones
                }
            )
            raise HTTPException(
                status_code=400,
                detail="No se puede eliminar el trabajador porque tiene zonas asignadas. "
                       "Debe eliminar o reasignar esas zonas primero."
            )

        # Obtener datos antes de eliminar
        persona = db.query(Persona).filter(
            Persona.id_persona == trabajador.id_persona_trabajador
        ).first()

        trabajador.borrado = False
        if persona:
            persona.borrado = False

        db.commit()

        # Log de eliminación exitosa
        await LogServicio.registrar_accion_negocio(
            source="trabajador_servicio.borrado_logico_trabajador",
            accion="eliminar_trabajador",
            user_id=id_trabajador,
            user_role="trabajador",
            estado="success",
            mensaje=f"Trabajador eliminado: {persona.nombre if persona else 'N/A'} {persona.apellido if persona else 'N/A'}",
            ip_address=ip_address,
            metadata={
                "id_trabajador": id_trabajador,
                "cedula": persona.cedula if persona else None,
                "correo": persona.correo if persona else None,
                "codigo_trabajador": trabajador.codigo_trabajador
            }
        )

        return {"mensaje": "Trabajador eliminado correctamente"}

    except HTTPException:
        raise
    except Exception as e:
        await LogServicio.registrar_error(
            source="trabajador_servicio.borrado_logico_trabajador",
            accion="eliminar_trabajador",
            error_message=str(e),
            user_id=id_trabajador,
            ip_address=ip_address
        )
        raise


def obtener_trabajadores_por_supervisor(db: Session, id_supervisor: int):
    trabajadores = (
        db.query(Trabajador)
        .options(joinedload(Trabajador.persona))
        .filter(
            Trabajador.id_supervisor_trabajador == id_supervisor,
            Trabajador.borrado == True
        )
        .all()
    )
    return trabajadores


def obtener_trabajadores_no_asignados(db: Session, id_supervisor: int):
    subquery_asignados = (
        db.query(TrabajadorZona.id_trabajador_trabajadorzona)
        .filter(TrabajadorZona.borrado == True)
        .subquery()
    )

    trabajadores = (
        db.query(Trabajador)
        .options(joinedload(Trabajador.persona))
        .filter(
            Trabajador.id_supervisor_trabajador == id_supervisor,
            Trabajador.estado == True,
            Trabajador.borrado == True,
            ~Trabajador.id_trabajador.in_(subquery_asignados)
        )
        .all()
    )

    return trabajadores

def validar_registro_unico_diario(db: Session, id_trabajador: int, id_empresa: int) -> dict:

    from app.modelos.registros_asistencia import RegistroAsistencia
    
    hoy = date.today()
    
    registro_hoy = db.query(RegistroAsistencia).filter(
        RegistroAsistencia.id_trabajador == id_trabajador,
        RegistroAsistencia.id_empresa == id_empresa,
        func.date(RegistroAsistencia.fecha_hora) == hoy  
    ).first()
    
    if registro_hoy:
        return {
            "existe": True,
            "id_registro": registro_hoy.id_registro,
            "fecha_hora": registro_hoy.fecha_hora,
            "cumple_epp": registro_hoy.cumple_epp,
            "codigo_ingresado": registro_hoy.codigo_ingresado
        }
    
    return None

def extraer_trabajador_codigo_con_camara(db: Session, codigo: str, id_empresa: int):
    trabajador = db.query(Trabajador).filter(
        Trabajador.codigo_trabajador == codigo,
        Trabajador.id_empresa == id_empresa,
        Trabajador.borrado == True
    ).first()

    if not trabajador:
       raise HTTPException(404, f"No existe trabajador con código {codigo} en esta empresa")

    if trabajador.id_empresa != id_empresa:
        raise HTTPException(
            status_code=400,
            detail=f"El trabajador {codigo} no pertenece a esta empresa"
        )

    registro_existente = validar_registro_unico_diario(db, trabajador.id_trabajador, id_empresa)
    
    if registro_existente:
        fecha_registro = registro_existente["fecha_hora"].strftime("%d/%m/%Y a las %H:%M:%S")
        estado_epp = "✅ CUMPLIÓ" if registro_existente["cumple_epp"] else "❌ NO CUMPLIÓ"
        
        raise HTTPException(
            status_code=400,
            detail=f"El trabajador {codigo} ya registró su asistencia hoy ({fecha_registro}). "
                   f"Estado EPP: {estado_epp}. Solo se permite un registro por día."
        )

    asignacion = db.query(TrabajadorZona).filter(
        TrabajadorZona.id_trabajador_trabajadorzona == trabajador.id_trabajador,
        TrabajadorZona.borrado == True
    ).first()

    if not asignacion:
        raise HTTPException(status_code=404, detail="El trabajador no tiene una zona asignada")

    id_zona = asignacion.id_zona_trabajadorzona

    camara = db.query(Camara).filter(
        Camara.id_zona == id_zona,
        Camara.borrado == True
    ).first()

    if not camara:
        raise HTTPException(status_code=404, detail="No existe cámara activa en la zona asignada")

    inspector_zona = db.query(InspectorZona).filter(
        InspectorZona.id_zona_inspectorzona == id_zona,
        InspectorZona.borrado == True
    ).first()

    id_inspector = None
    inspector_data = None

    if inspector_zona:
        id_inspector = inspector_zona.id_inspector_inspectorzona

        inspector = db.query(Inspector).filter(
            Inspector.id_inspector == id_inspector,
            Inspector.borrado == True
        ).first()

        if inspector:
            inspector_data = {
                "id_inspector": inspector.id_inspector,
                "frecuenciaVisita": inspector.frecuenciaVisita,
                "id_persona": inspector.id_persona_inspector
            }

    return {
        "id_trabajador": trabajador.id_trabajador,
        "cargo": trabajador.cargo,
        "implementos_requeridos": trabajador.implementos_requeridos,
        "estado": trabajador.estado,
        "codigo_trabajador": trabajador.codigo_trabajador,
        "id_empresa": trabajador.id_empresa,
        "id_supervisor_trabajador": trabajador.id_supervisor_trabajador,
        "fecharegistro": trabajador.fecharegistro,
        "id_zona": id_zona,
        "id_inspector": id_inspector,
        "camara": {
            "id_camara": camara.id_camara,
            "codigo": camara.codigo,
            "ipAddress": camara.ipAddress,
            "tipo": camara.tipo,
            "estado": camara.estado,
            "ultimaTransmision": camara.ultimaTransmision,
            "ultima_revision": camara.ultima_revision
        },
        "persona": {
            "id_persona": trabajador.persona.id_persona,
            "cedula": trabajador.persona.cedula,
            "nombre": trabajador.persona.nombre,
            "apellido": trabajador.persona.apellido,
            "telefono": trabajador.persona.telefono,
            "correo": trabajador.persona.correo,
            "direccion": trabajador.persona.direccion,
            "genero": trabajador.persona.genero,
            "fecha_nacimiento": trabajador.persona.fecha_nacimiento
        },
        "inspector": inspector_data
    }

async def login_trabajador(db: Session, correo: str, contrasena: str, ip_address: str = None):
    try:
        # Log de intento de login
        await LogServicio.registrar_autenticacion(
            source="trabajador_servicio.login_trabajador",
            accion="login_intento",
            correo=correo,
            estado="pending",
            ip_address=ip_address,
            mensaje=f"Intento de inicio de sesión para: {correo}"
        )

        # Buscar persona por correo
        persona = db.query(Persona).filter(
            Persona.correo == correo,
            Persona.borrado == True
        ).first()

        if not persona:
            await LogServicio.registrar_autenticacion(
                source="trabajador_servicio.login_trabajador",
                accion="login_fallido",
                correo=correo,
                estado="failed",
                ip_address=ip_address,
                mensaje="Correo no encontrado",
                error="Usuario no existe"
            )
            raise HTTPException(status_code=404, detail="Correo no encontrado")

        # Validar rol
        if persona.rol != "trabajador":
            await LogServicio.registrar_autenticacion(
                source="trabajador_servicio.login_trabajador",
                accion="login_fallido",
                correo=correo,
                estado="failed",
                ip_address=ip_address,
                user_id=persona.id_persona,
                mensaje="Intento de login con rol incorrecto",
                error=f"Rol esperado: trabajador, rol actual: {persona.rol}"
            )
            raise HTTPException(status_code=400, detail="El usuario no es trabajador")

        # Validar contraseña
        if not verificar_contrasena(contrasena, persona.contrasena):
            await LogServicio.registrar_autenticacion(
                source="trabajador_servicio.login_trabajador",
                accion="login_fallido",
                correo=correo,
                estado="failed",
                ip_address=ip_address,
                user_id=persona.id_persona,
                mensaje="Contraseña incorrecta",
                error="Credenciales inválidas"
            )
            raise HTTPException(status_code=400, detail="Contraseña incorrecta")

        # Buscar datos del trabajador
        trabajador = db.query(Trabajador).filter(
            Trabajador.id_persona_trabajador == persona.id_persona,
            Trabajador.borrado == True
        ).first()

        if not trabajador:
            await LogServicio.registrar_autenticacion(
                source="trabajador_servicio.login_trabajador",
                accion="login_fallido",
                correo=correo,
                estado="failed",
                ip_address=ip_address,
                user_id=persona.id_persona,
                mensaje="Registro de trabajador no encontrado",
                error="No existe registro del trabajador"
            )
            raise HTTPException(status_code=404, detail="No existe registro del trabajador")

        # Log de login exitoso
        await LogServicio.registrar_autenticacion(
            source="trabajador_servicio.login_trabajador",
            accion="login_exitoso",
            correo=correo,
            estado="success",
            ip_address=ip_address,
            user_id=trabajador.id_trabajador,
            mensaje=f"Inicio de sesión exitoso: {persona.nombre} {persona.apellido}",
            metadata={
                "id_trabajador": trabajador.id_trabajador,
                "id_persona": persona.id_persona,
                "id_empresa": trabajador.id_empresa,
                "codigo_trabajador": trabajador.codigo_trabajador
            }
        )

        return {
            "mensaje": "Inicio de sesión exitoso",
            "id_trabajador": trabajador.id_trabajador,
            "id_persona": persona.id_persona, 
            "id_supervisor": trabajador.id_supervisor_trabajador,
            "id_empresa_trabajador": trabajador.id_empresa,
            "nombre": persona.nombre,
            "correo": persona.correo,
            "rol": persona.rol
        }

    except HTTPException:
        raise
    except Exception as e:
        await LogServicio.registrar_error(
            source="trabajador_servicio.login_trabajador",
            accion="login_error",
            error_message=str(e),
            ip_address=ip_address,
            metadata={"correo": correo}
        )
        raise
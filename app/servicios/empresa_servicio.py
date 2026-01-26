from sqlalchemy.orm import Session
from fastapi import HTTPException

from app.modelos.empresa_modelo import Empresa
from app.esquemas.empresa_esquema import EmpresaCreate, EmpresaUpdate

from app.Validaciones.empresa_validaciones import (
    validar_nombre_empresa,
    validar_telefono_empresa,
    validar_ruc_empresa,
    validar_correo_unico,
    validar_ruc_unico,
    validar_formato_correo,
    validar_relaciones_empresa
)

from app.servicios.log_service import LogServicio


# =========================================================
# 📌 CREAR EMPRESA
# =========================================================
async def crear_empresa(db: Session, empresa: EmpresaCreate, user_id: int = None, user_role: str = None, ip_address: str = None):
    try:
        validar_nombre_empresa(empresa.nombreEmpresa)
        validar_telefono_empresa(empresa.telefono)
        validar_ruc_empresa(empresa.ruc)
        validar_formato_correo(empresa.correo)

        validar_ruc_unico(db, empresa.ruc)
        validar_correo_unico(db, empresa.correo)

        nueva_empresa = Empresa(
            nombreEmpresa=empresa.nombreEmpresa,
            ruc=empresa.ruc,
            direccion=empresa.direccion,
            telefono=empresa.telefono,
            correo=empresa.correo,
            sector=empresa.sector,
            id_administrador_empresa=empresa.id_administrador_empresa,
            borrado=True
        )

        db.add(nueva_empresa)
        db.commit()
        db.refresh(nueva_empresa)
        
        # ✅ Log de creación exitosa
        await LogServicio.registrar_accion_negocio(
            source="empresa_servicio.crear_empresa",
            accion="crear_empresa",
            user_id=user_id,
            user_role=user_role,
            estado="success",
            mensaje=f"Empresa '{nueva_empresa.nombreEmpresa}' creada exitosamente",
            ip_address=ip_address,
            metadata={
                "empresa_id": nueva_empresa.id_Empresa,
                "ruc": nueva_empresa.ruc,
                "nombre": nueva_empresa.nombreEmpresa,
                "correo": nueva_empresa.correo
            }
        )
        
        return nueva_empresa
        
    except HTTPException as e:
        # ⚠️ Log de error de validación
        await LogServicio.registrar_error(
            source="empresa_servicio.crear_empresa",
            accion="crear_empresa",
            error_message=f"Error de validación: {e.detail}",
            user_id=user_id,
            ip_address=ip_address,
            metadata={
                "ruc": empresa.ruc,
                "correo": empresa.correo,
                "status_code": e.status_code
            }
        )
        raise
    except Exception as e:
        # ❌ Log de error inesperado
        await LogServicio.registrar_error(
            source="empresa_servicio.crear_empresa",
            accion="crear_empresa",
            error_message=f"Error inesperado: {str(e)}",
            user_id=user_id,
            ip_address=ip_address,
            metadata={"ruc": empresa.ruc}
        )
        raise


# =========================================================
# 📌 OBTENER EMPRESAS ACTIVAS
# =========================================================
def obtener_empresas(db: Session, skip: int = 0, limit: int = 100):
    return (
        db.query(Empresa)
        .filter(Empresa.borrado == True)
        .offset(skip)
        .limit(limit)
        .all()
    )


# =========================================================
# 📌 OBTENER EMPRESA POR ID
# =========================================================
def obtener_empresa_por_id(db: Session, empresa_id: int):
    empresa = db.query(Empresa).filter(Empresa.id_Empresa == empresa_id).first()

    if not empresa:
        raise HTTPException(status_code=404, detail="Empresa no encontrada")

    return empresa


# =========================================================
# 📌 ACTUALIZAR EMPRESA
# =========================================================
async def actualizar_empresa(db: Session, empresa_id: int, empresa_update: EmpresaUpdate, user_id: int = None, user_role: str = None, ip_address: str = None):
    try:
        empresa = obtener_empresa_por_id(db, empresa_id)

        if empresa_update.nombreEmpresa:
            validar_nombre_empresa(empresa_update.nombreEmpresa)

        if empresa_update.telefono:
            validar_telefono_empresa(empresa_update.telefono)

        if empresa_update.correo:
            validar_formato_correo(empresa_update.correo)
            validar_correo_unico(db, empresa_update.correo, empresa_id)

        if empresa_update.ruc:
            raise HTTPException(
                status_code=400,
                detail="No se puede modificar el RUC de una empresa"
            )

        # Guardar valores anteriores para el log
        campos_modificados = {}
        for campo, valor in empresa_update.dict(exclude_unset=True).items():
            valor_anterior = getattr(empresa, campo, None)
            if valor_anterior != valor:
                campos_modificados[campo] = {
                    "anterior": valor_anterior,
                    "nuevo": valor
                }
            setattr(empresa, campo, valor)

        db.commit()
        db.refresh(empresa)
        
        # ✅ Log de actualización exitosa
        if campos_modificados:
            await LogServicio.registrar_accion_negocio(
                source="empresa_servicio.actualizar_empresa",
                accion="actualizar_empresa",
                user_id=user_id,
                user_role=user_role,
                estado="success",
                mensaje=f"Empresa '{empresa.nombreEmpresa}' actualizada exitosamente",
                ip_address=ip_address,
                metadata={
                    "empresa_id": empresa_id,
                    "campos_modificados": campos_modificados
                }
            )
        
        return empresa
        
    except HTTPException as e:
        # ⚠️ Log de error de validación
        await LogServicio.registrar_error(
            source="empresa_servicio.actualizar_empresa",
            accion="actualizar_empresa",
            error_message=f"Error al actualizar: {e.detail}",
            user_id=user_id,
            ip_address=ip_address,
            metadata={
                "empresa_id": empresa_id,
                "status_code": e.status_code
            }
        )
        raise
    except Exception as e:
        # ❌ Log de error inesperado
        await LogServicio.registrar_error(
            source="empresa_servicio.actualizar_empresa",
            accion="actualizar_empresa",
            error_message=f"Error inesperado: {str(e)}",
            user_id=user_id,
            ip_address=ip_address,
            metadata={"empresa_id": empresa_id}
        )
        raise


# =========================================================
# 📌 ELIMINAR EMPRESA (BORRADO LÓGICO)
# =========================================================
async def eliminar_empresa(db: Session, empresa_id: int, user_id: int = None, user_role: str = None, ip_address: str = None):
    try:
        empresa = obtener_empresa_por_id(db, empresa_id)

        validar_relaciones_empresa(db, empresa_id)

        nombre_empresa = empresa.nombreEmpresa
        ruc_empresa = empresa.ruc

        empresa.borrado = False
        db.commit()

        # ✅ Log de eliminación lógica exitosa
        await LogServicio.registrar_accion_negocio(
            source="empresa_servicio.eliminar_empresa",
            accion="eliminar_empresa_logico",
            user_id=user_id,
            user_role=user_role,
            estado="success",
            mensaje=f"Empresa '{nombre_empresa}' eliminada lógicamente",
            ip_address=ip_address,
            metadata={
                "empresa_id": empresa_id,
                "ruc": ruc_empresa,
                "tipo_eliminacion": "logico"
            }
        )

        return {"message": "Empresa eliminada correctamente"}
        
    except HTTPException as e:
        # ⚠️ Log de error de validación
        await LogServicio.registrar_error(
            source="empresa_servicio.eliminar_empresa",
            accion="eliminar_empresa_logico",
            error_message=f"Error al eliminar: {e.detail}",
            user_id=user_id,
            ip_address=ip_address,
            metadata={
                "empresa_id": empresa_id,
                "status_code": e.status_code
            }
        )
        raise
    except Exception as e:
        # ❌ Log de error inesperado
        await LogServicio.registrar_error(
            source="empresa_servicio.eliminar_empresa",
            accion="eliminar_empresa_logico",
            error_message=f"Error inesperado: {str(e)}",
            user_id=user_id,
            ip_address=ip_address,
            metadata={"empresa_id": empresa_id}
        )
        raise


# =========================================================
# 📌 ELIMINAR EMPRESA (PERMANENTE)
# =========================================================
async def eliminar_empresa_permanente(db: Session, empresa_id: int, user_id: int = None, user_role: str = None, ip_address: str = None):
    try:
        empresa = obtener_empresa_por_id(db, empresa_id)
        
        nombre_empresa = empresa.nombreEmpresa
        ruc_empresa = empresa.ruc
        
        db.delete(empresa)
        db.commit()
        
        # ⚠️ Log de eliminación permanente (WARNING por ser crítico)
        await LogServicio.registrar_accion_negocio(
            source="empresa_servicio.eliminar_empresa_permanente",
            accion="eliminar_empresa_permanente",
            user_id=user_id,
            user_role=user_role,
            estado="success",
            mensaje=f"Empresa '{nombre_empresa}' eliminada PERMANENTEMENTE",
            ip_address=ip_address,
            metadata={
                "empresa_id": empresa_id,
                "ruc": ruc_empresa,
                "tipo_eliminacion": "permanente",
                "advertencia": "Esta acción es irreversible"
            }
        )
        
        return {"message": "Empresa eliminada permanentemente"}
        
    except HTTPException as e:
        # ⚠️ Log de error
        await LogServicio.registrar_error(
            source="empresa_servicio.eliminar_empresa_permanente",
            accion="eliminar_empresa_permanente",
            error_message=f"Error al eliminar permanentemente: {e.detail}",
            user_id=user_id,
            ip_address=ip_address,
            metadata={
                "empresa_id": empresa_id,
                "status_code": e.status_code
            }
        )
        raise
    except Exception as e:
        # ❌ Log de error inesperado
        await LogServicio.registrar_error(
            source="empresa_servicio.eliminar_empresa_permanente",
            accion="eliminar_empresa_permanente",
            error_message=f"Error inesperado: {str(e)}",
            user_id=user_id,
            ip_address=ip_address,
            metadata={"empresa_id": empresa_id}
        )
        raise
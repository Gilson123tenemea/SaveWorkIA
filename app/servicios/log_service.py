from datetime import datetime
from typing import Optional, Dict, Any
from app.logs.mongodb import get_mongodb
from app.modelos.log_model import LogDocument, LogLevel, LogType

class LogServicio:
    _collection_name = "logs"
    
    @staticmethod
    async def registrar_autenticacion(
        source: str,
        accion: str,  # "login_intento", "login_exitoso", "login_fallido"
        correo: str,
        estado: str,  # "success", "failed"
        ip_address: Optional[str] = None,
        user_id: Optional[int] = None,
        mensaje: Optional[str] = None,
        error: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ):

        db = get_mongodb()
        collection = db[LogServicio._collection_name]
        
        log_doc = LogDocument(
            timestamp=datetime.utcnow(),
            level=LogLevel.INFO if estado == "success" else LogLevel.WARNING,
            type=LogType.AUTHENTICATION,
            source=source,
            action=accion,
            correo=correo,
            user_id=user_id,
            status=estado,
            ip_address=ip_address,
            message=mensaje,
            error_message=error,
            metadata=metadata or {}
        )
        
        collection.insert_one(log_doc.dict())
    
    @staticmethod
    async def registrar_accion_negocio(
        source: str,
        accion: str,  # "registro_admin", "eliminacion_usuario", etc
        user_id: Optional[int] = None,
        user_role: Optional[str] = None,
        estado: str = "success",
        mensaje: Optional[str] = None,
        ip_address: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ):

        db = get_mongodb()
        collection = db[LogServicio._collection_name]
        
        log_doc = LogDocument(
            timestamp=datetime.utcnow(),
            level=LogLevel.INFO,
            type=LogType.BUSINESS_LOGIC,
            source=source,
            action=accion,
            user_id=user_id,
            user_role=user_role,
            status=estado,
            message=mensaje,
            ip_address=ip_address,
            metadata=metadata or {}
        )
        
        collection.insert_one(log_doc.dict())
    
    @staticmethod
    async def registrar_error(
        source: str,
        accion: str,
        error_message: str,
        user_id: Optional[int] = None,
        ip_address: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ):

        db = get_mongodb()
        collection = db[LogServicio._collection_name]
        
        log_doc = LogDocument(
            timestamp=datetime.utcnow(),
            level=LogLevel.ERROR,
            type=LogType.SYSTEM,
            source=source,
            action=accion,
            user_id=user_id,
            ip_address=ip_address,
            error_message=error_message,
            status="failed",
            metadata=metadata or {}
        )
        
        collection.insert_one(log_doc.dict())
    
    @staticmethod
    def obtener_logs(
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        tipo: Optional[str] = None,
        user_id: Optional[int] = None,
        correo: Optional[str] = None,
        accion: Optional[str] = None,
        limit: int = 100
    ):
        db = get_mongodb()
        collection = db[LogServicio._collection_name]
        
        query = {}
        
        if start_date or end_date:
            query["timestamp"] = {}
            if start_date:
                query["timestamp"]["$gte"] = start_date
            if end_date:
                query["timestamp"]["$lte"] = end_date
        
        if tipo:
            query["type"] = tipo
        
        if user_id:
            query["user_id"] = user_id
        
        if correo:
            query["correo"] = correo
        
        if accion:
            query["action"] = accion
        
        return list(
            collection.find(query)
            .sort("timestamp", -1)
            .limit(limit)
        )
    
    @staticmethod
    def obtener_logs_por_correo(correo: str, dias: int = 30):

        db = get_mongodb()
        collection = db[LogServicio._collection_name]
        
        fecha_inicio = datetime.utcnow()
        # Resta dias días
        fecha_inicio = fecha_inicio.replace(day=fecha_inicio.day - dias)
        
        query = {
            "correo": correo,
            "timestamp": {"$gte": fecha_inicio}
        }
        
        return list(
            collection.find(query)
            .sort("timestamp", -1)
        )
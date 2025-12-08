from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, text
from sqlalchemy.orm import relationship
from app.config import Base
from sqlalchemy import LargeBinary

class EvidenciaFallo(Base):
    __tablename__ = "evidencias_fallo"

    id_evidencia = Column(Integer, primary_key=True, index=True)
    foto_data = Column(LargeBinary, nullable=True)
    detalle_fallo = Column(String(200), nullable=False)
    fecha_captura = Column(DateTime, server_default=text("CURRENT_TIMESTAMP"))
    borrado = Column(Boolean, default=False)

    id_registro = Column(Integer, ForeignKey("registros_asistencia.id_registro"), nullable=False)

    # Relación ORM
    registro = relationship("RegistroAsistencia", lazy="joined")

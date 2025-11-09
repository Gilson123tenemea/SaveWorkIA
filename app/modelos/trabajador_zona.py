# app/modelos/trabajador_zona.py
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from app.config import Base

class TrabajadorZona(Base):
    __tablename__ = "trabajador_zona"

    id_trabajador_zona = Column(Integer, primary_key=True, index=True)
    borrado = Column(Boolean, default=True)

    id_trabajador_trabajadorzona = Column(Integer, ForeignKey("trabajadores.id_trabajador"), nullable=False)
    id_zona_trabajadorzona = Column(Integer, ForeignKey("zonas.id_Zona"), nullable=False)
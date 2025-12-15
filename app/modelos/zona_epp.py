from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from app.config import Base

class ZonaEpp(Base):
    __tablename__ = "zona_epp"

    id = Column(Integer, primary_key=True, index=True)

    id_zona = Column(
        Integer,
        ForeignKey("zonas.id_Zona", ondelete="CASCADE"),
        nullable=False
    )

    # casco, gafas, guantes, chaleco, botas, mascarilla, etc.
    tipo_epp = Column(String(50), nullable=False)

    obligatorio = Column(Boolean, default=True)
    activo = Column(Boolean, default=True)

    zona = relationship("Zona", back_populates="epps")

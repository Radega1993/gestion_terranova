from sqlalchemy import Column, Integer, String, Boolean, Date, Float, ForeignKey
from sqlalchemy.orm import relationship
from app.database.base import Base

class Socio(Base):
    __tablename__ = 'socios'

    id = Column(Integer, primary_key=True)
    codigo_socio = Column(String(20), unique=True)
    nombre = Column(String(100))
    primer_apellido = Column(String(100))
    segundo_apellido = Column(String(100))
    dni = Column(String(20))
    fecha_nacimiento = Column(Date)
    telefono = Column(String(20))
    email = Column(String(100))
    direccion = Column(String(200))
    poblacion = Column(String(100))
    codigo_postal = Column(String(10))
    provincia = Column(String(100))
    foto_path = Column(String(500))
    es_principal = Column(Boolean, default=False)
    activo = Column(Boolean, default=True)
    rgpd = Column(Boolean, default=False)
    
    # Campos adicionales para socios principales
    telefono2 = Column(String(20))
    email2 = Column(String(100))
    cuota = Column(Float, default=0.0)
    num_pers = Column(Integer, default=0)
    adherits = Column(Integer, default=0)
    menor_3_anys = Column(Integer, default=0)
    
    # Relación con socio principal
    socio_principal_id = Column(Integer, ForeignKey('socios.id'))
    socio_principal = relationship("Socio", remote_side=[id])
    miembros_familia = relationship("Socio", back_populates="socio_principal") 
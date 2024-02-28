# Modelos de la base de datos (tablas, relaciones)

from sqlalchemy import create_engine, Column, Integer, String, Float, ForeignKey, Date
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from werkzeug.security import generate_password_hash

Base = declarative_base()

class Producto(Base):
    __tablename__ = 'productos'
    id = Column(Integer, primary_key=True)
    nombre = Column(String, nullable=False)
    precio = Column(Float, nullable=False)
    stock_actual = Column(Integer, nullable=False)

class Venta(Base):
    __tablename__ = 'ventas'
    id = Column(Integer, primary_key=True)
    fecha = Column(Date, nullable=False)
    total = Column(Float, nullable=False)
    detalles = relationship("DetalleVenta", backref="venta")

class DetalleVenta(Base):
    __tablename__ = 'detalles_venta'
    id = Column(Integer, primary_key=True)
    venta_id = Column(Integer, ForeignKey('ventas.id'), nullable=False)
    producto_id = Column(Integer, ForeignKey('productos.id'), nullable=False)
    cantidad = Column(Integer, nullable=False)
    precio = Column(Float, nullable=False)
    producto = relationship("Producto")

class Usuario(Base):
    __tablename__ = 'usuarios'
    id = Column(Integer, primary_key=True)
    nombre = Column(String, nullable=False)
    correo_electronico = Column(String, unique=True, nullable=False)
    tipo_usuario = Column(String, nullable=False)  # Ejemplo: 'trabajador' o 'cliente'
    contrasena_hash = Column(String, nullable=False)

    def set_password(self, password):
        self.contrasena_hash = generate_password_hash(password)
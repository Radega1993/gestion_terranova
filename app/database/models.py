# Modelos de la base de datos (tablas, relaciones)

from datetime import datetime, timezone
from sqlalchemy import Column, Integer, ForeignKey, Float, Date, Boolean, String, DateTime
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
    activo = Column(Boolean, default=True) 

class Venta(Base):
    __tablename__ = 'ventas'
    id = Column(Integer, primary_key=True)
    fecha = Column(Date, nullable=False, default=datetime.now(timezone.utc))
    total = Column(Float, nullable=False)
    socio_id = Column(Integer, ForeignKey('socios.id'), nullable=True)  # Puede ser nullable si no todas las ventas son a socios
    trabajador_id = Column(Integer, ForeignKey('usuarios.id'), nullable=False)
    pagada = Column(Boolean, default=True)  # Por defecto True, suponiendo que la mayoría de ventas se pagan al momento

    # Relaciones
    socio = relationship("app.database.models.Socio", backref="ventas")  # Permite acceder a las ventas desde el socio
    trabajador = relationship("app.database.models.Usuario", backref="ventas_realizadas")  # Permite acceder a las ventas realizadas por el trabajador
    detalles = relationship("app.database.models.DetalleVenta", backref="venta")

class Usuario(Base):
    __tablename__ = 'usuarios'
    id = Column(Integer, primary_key=True)
    nombre = Column(String, nullable=False)
    correo_electronico = Column(String, unique=True, nullable=False)
    tipo_usuario = Column(String, nullable=False)
    contrasena_hash = Column(String, nullable=False)

    def set_password(self, password):
        self.contrasena_hash = generate_password_hash(password)

class Socio(Base):
    __tablename__ = 'socios'
    id = Column(Integer, primary_key=True)
    nombre = Column(String, nullable=False)
    correo_electronico = Column(String, nullable=False, unique=True)
    fecha_inscripcion = Column(Date, default=datetime.now(timezone.utc))
    activo = Column(Boolean, default=True)

class Deuda(Base):
    __tablename__ = 'deudas'
    id = Column(Integer, primary_key=True)
    socio_id = Column(Integer, ForeignKey('socios.id'), nullable=False)
    fecha = Column(Date, default=datetime.now(timezone.utc))
    total = Column(Float, nullable=False)
    trabajador_id = Column(Integer, ForeignKey('usuarios.id'), nullable=False)
    pagada = Column(Boolean, default=False)

    socio = relationship("app.database.models.Socio", backref="deudas")
    trabajador = relationship("app.database.models.Usuario")
    detalles_venta = relationship("app.database.models.DetalleVenta", backref="deuda")

class DetalleVenta(Base):
    __tablename__ = 'detalles_venta'
    id = Column(Integer, primary_key=True)
    venta_id = Column(Integer, ForeignKey('ventas.id'), nullable=True)
    producto_id = Column(Integer, ForeignKey('productos.id'), nullable=False)
    cantidad = Column(Integer, nullable=False)
    precio = Column(Float, nullable=False)
    producto = relationship("app.database.models.Producto")
    deuda_id = Column(Integer, ForeignKey('deudas.id'))

class Reserva(Base):
    __tablename__ = 'reservas'
    id = Column(Integer, primary_key=True)
    socio_id = Column(Integer, ForeignKey('socios.id'), nullable=False)
    fecha_reserva = Column(Date, nullable=False)
    fecha_creacion = Column(DateTime, default=datetime.now)
    recepcionista_id = Column(Integer, ForeignKey('usuarios.id'), nullable=False)
    servicio_id = Column(Integer, ForeignKey('servicios.id'), nullable=False)
    importe_abonado = Column(Float, nullable=False)
    precio = Column(Float, nullable=False)
    opciones_adicionales = Column(String)
    pagada = Column(Boolean, default=False)

    # Relaciones
    socio = relationship("Socio")
    recepcionista = relationship("Usuario")
    servicio = relationship("Servicio", backref="reservas") 

class Servicio(Base):
    __tablename__ = 'servicios'
    id = Column(Integer, primary_key=True)
    nombre = Column(String, nullable=False)
    precio = Column(Float, nullable=False)
    tipo = Column(String, nullable=False)
    activo = Column(Boolean, default=True)
# Modelos de la base de datos (tablas, relaciones)

from datetime import datetime, timezone
from sqlalchemy import Column, Integer, ForeignKey, Float, Date, Boolean, String, DateTime, Text, UniqueConstraint
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
    socio = relationship("Socio", back_populates="ventas")
    trabajador = relationship("Usuario", backref="ventas_realizadas")
    detalles = relationship("DetalleVenta", back_populates="venta")

class Usuario(Base):
    __tablename__ = 'usuarios'
    id = Column(Integer, primary_key=True)
    nombre = Column(String, nullable=False)
    user = Column(String, unique=True, nullable=False)
    tipo_usuario = Column(String, nullable=False)
    contrasena_hash = Column(String, nullable=False)
    activo = Column(Boolean, default=True) 
    
    def set_password(self, password):
        self.contrasena_hash = generate_password_hash(password)

class Socio(Base):
    __tablename__ = 'socios'
    
    id = Column(Integer, primary_key=True)
    rgpd = Column(Boolean, default=False)
    codigo_socio = Column(String(10))
    canvi = Column(String(50))
    casa = Column(Integer)
    total_soc = Column(Integer)
    num_pers = Column(Integer)
    adherits = Column(Integer)
    menor_3_anys = Column(Integer)
    cuota = Column(Float)
    dni = Column(String(9))
    nombre = Column(String(100))
    primer_apellido = Column(String(100))
    segundo_apellido = Column(String(100))
    direccion = Column(String(200))
    poblacion = Column(String(100))
    codigo_postal = Column(String(5))
    provincia = Column(String(100))
    iban = Column(String(4))
    entidad = Column(String(4))
    oficina = Column(String(4))
    dc = Column(String(2))
    cuenta_corriente = Column(String(10))
    telefono = Column(String(15))
    telefono2 = Column(String(15))
    email = Column(String(100))
    email2 = Column(String(100))
    observaciones = Column(Text)
    fecha_nacimiento = Column(Date)
    fecha_registro = Column(DateTime, default=datetime.now)
    activo = Column(Boolean, default=True)
    es_principal = Column(Boolean, default=True)
    socio_principal_id = Column(Integer, ForeignKey('socios.id'), nullable=True)
    foto_path = Column(String(255), nullable=True)
    
    # Relaciones
    socio_principal = relationship('Socio', remote_side=[id], backref='miembros_familia')
    deudas = relationship('Deuda', back_populates='socio')
    ventas = relationship('Venta', back_populates='socio')
    reservas = relationship('Reserva', back_populates='socio')
    
    # Campos para miembros de familia
    miembros = relationship('MiembroFamilia', 
                          back_populates='socio_principal',
                          foreign_keys='[MiembroFamilia.socio_principal_id]')
    
    def __repr__(self):
        return f"<Socio {self.nombre} {self.primer_apellido} {self.segundo_apellido}>"
    
    __table_args__ = (
        # Añadimos el UNIQUE constraint aquí
        UniqueConstraint('codigo_socio', name='uq_socio_codigo'),
    )

class Deuda(Base):
    __tablename__ = 'deudas'
    id = Column(Integer, primary_key=True)
    socio_id = Column(Integer, ForeignKey('socios.id'), nullable=False)
    fecha = Column(Date, default=datetime.now(timezone.utc))
    total = Column(Float, nullable=False)
    trabajador_id = Column(Integer, ForeignKey('usuarios.id'), nullable=False)
    pagada = Column(Boolean, default=False)

    socio = relationship("Socio", back_populates="deudas")
    trabajador = relationship("Usuario")
    detalles_venta = relationship("DetalleVenta", back_populates="deuda")

class DetalleVenta(Base):
    __tablename__ = 'detalles_venta'
    id = Column(Integer, primary_key=True)
    venta_id = Column(Integer, ForeignKey('ventas.id'), nullable=True)
    producto_id = Column(Integer, ForeignKey('productos.id'), nullable=False)
    cantidad = Column(Integer, nullable=False)
    precio = Column(Float, nullable=False)
    deuda_id = Column(Integer, ForeignKey('deudas.id'))
    
    # Relaciones
    venta = relationship("Venta", back_populates="detalles")
    producto = relationship("Producto")
    deuda = relationship("Deuda", back_populates="detalles_venta")

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
    en_lista_de_espera = Column(Boolean, default=False)

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

class MiembroFamilia(Base):
    __tablename__ = 'miembros_familia'
    id = Column(Integer, primary_key=True)
    socio_principal_id = Column(Integer, ForeignKey('socios.id'), nullable=False)
    socio_miembro_id = Column(Integer, ForeignKey('socios.id'), nullable=False)
    fecha_registro = Column(DateTime, default=datetime.now)
    activo = Column(Boolean, default=True)
    
    # Relaciones
    socio_principal = relationship("Socio", 
                                 foreign_keys=[socio_principal_id],
                                 back_populates="miembros")
    socio_miembro = relationship("Socio", 
                               foreign_keys=[socio_miembro_id])
# Gestión de stock

from app.database.connection import Session
from app.database.models import Producto

def añadir_producto(nombre, precio, stock_inicial):
    """Añade un nuevo producto a la base de datos."""
    with Session() as session:
        nuevo_producto = Producto(nombre=nombre, precio=precio, stock_actual=stock_inicial)
        session.add(nuevo_producto)
        session.commit()
        return nuevo_producto.id  # Retorna el ID del nuevo producto

def obtener_productos():
    """Obtiene una lista de todos los productos."""
    with Session() as session:
        productos = session.query(Producto).all()
        return productos  # Retorna una lista de objetos Producto

def actualizar_stock(session, producto_id, cantidad):
    """Actualiza el stock de un producto específico."""
    producto = session.query(Producto).filter_by(id=producto_id).one()
    producto.stock_actual += cantidad
        
def obtener_stock_actual(producto_id):
    """Obtiene el stock actual de un producto específico."""
    with Session() as session:
        producto = session.query(Producto).filter_by(id=producto_id).one()
        return producto.stock_actual

def eliminar_producto(producto_id):
    """Elimina un producto específico de la base de datos."""
    with Session() as session:
        producto = session.query(Producto).filter_by(id=producto_id).one()
        session.delete(producto)
        session.commit()

def actualizar_producto(producto_id, nombre, precio, stock_actual):
    """Actualiza los detalles de un producto específico."""
    with Session() as session:
        producto = session.query(Producto).filter_by(id=producto_id).one()
        producto.nombre = nombre
        producto.precio = precio
        producto.stock_actual = stock_actual
        session.commit()

def deshabilitar_producto(producto_id):
    """Marca un producto como deshabilitado en lugar de eliminarlo físicamente."""
    with Session() as session:
        producto = session.query(Producto).filter_by(id=producto_id).one()
        producto.estado = 'deshabilitado'  # Asumiendo que existe este campo
        session.commit()

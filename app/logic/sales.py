# Gestión de ventas
from datetime import date
from sqlalchemy.exc import SQLAlchemyError
from app.database.models import DetalleVenta, Producto, Venta

def procesar_venta(session, detalles_venta):
    try:
        venta = Venta(fecha=date.today(), total=0)
        session.add(venta)
        total_venta = 0
        for detalle in detalles_venta:
            producto = session.query(Producto).filter(Producto.id == detalle['producto_id']).one()
            if producto.stock_actual >= detalle['cantidad']:
                producto.stock_actual -= detalle['cantidad']
                total_linea = detalle['cantidad'] * producto.precio
                total_venta += total_linea
                detalle_venta = DetalleVenta(
                    venta=venta,  # Aquí cambiamos venta_id por venta gracias a la relación definida en los modelos
                    producto_id=detalle['producto_id'],
                    cantidad=detalle['cantidad'],
                    precio=producto.precio
                )
                session.add(detalle_venta)
            else:
                raise Exception(f"Stock insuficiente para el producto {producto.nombre}")
        venta.total = total_venta
        session.commit()
        return venta.id  # Devolvemos el ID de la venta procesada como confirmación
    except SQLAlchemyError as e:
        session.rollback()  # En caso de error, revertimos la transacción
        raise e

def obtener_informe_ventas(session, fecha_inicio, fecha_fin):
    """Obtiene un informe de ventas para un período específico."""
    try:
        ventas = session.query(Venta).filter(Venta.fecha >= fecha_inicio, Venta.fecha <= fecha_fin).all()
        informe = [{"venta_id": venta.id, "fecha": venta.fecha, "total": venta.total} for venta in ventas]
        return informe
    except SQLAlchemyError as e:
        raise e

def actualizar_stock_producto(session, producto_id, cantidad):
    """Actualiza el stock de un producto específico."""
    try:
        producto = session.query(Producto).filter(Producto.id == producto_id).one()
        producto.stock_actual += cantidad  # Asumimos que cantidad puede ser negativa para reducir el stock
        session.commit()
    except SQLAlchemyError as e:
        session.rollback()
        raise e

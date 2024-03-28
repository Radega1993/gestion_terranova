# Gestión de ventas
from datetime import datetime, timezone
from sqlalchemy.exc import SQLAlchemyError
from app.database.models import DetalleVenta, Producto, Venta

def procesar_venta(session, socio_id, detalles_venta, total_venta, trabajador_id):
    try:
        # Creamos una nueva venta
        nueva_venta = Venta(
            fecha=datetime.now(timezone.utc),
            total=total_venta,
            socio_id=socio_id,
            trabajador_id=trabajador_id,
            pagada=True  # Asumimos que esta función procesa ventas pagadas
        )
        session.add(nueva_venta)

        for detalle in detalles_venta:
            producto = session.query(Producto).filter_by(id=detalle['producto_id']).one()
            if producto.stock_actual >= detalle['cantidad']:
                # Actualizamos el stock del producto
                producto.stock_actual -= detalle['cantidad']
                
                # Creamos el detalle de la venta
                detalle_venta = DetalleVenta(
                    venta=nueva_venta,
                    producto_id=detalle['producto_id'],
                    cantidad=detalle['cantidad'],
                    precio=producto.precio
                )
                session.add(detalle_venta)
            else:
                raise Exception(f"Stock insuficiente para el producto {producto.nombre}")

        session.commit()
        return nueva_venta.id
    except SQLAlchemyError as e:
        session.rollback()
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

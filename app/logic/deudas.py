from datetime import datetime, timezone
from sqlalchemy.exc import SQLAlchemyError
from app.database.connection import Session
from app.database.models import Deuda, DetalleVenta, Producto

def verificar_deudas_socio(socio_id):
    """Verifica si un socio tiene deudas pendientes."""
    with Session() as session:
        # Este es un ejemplo y necesitarás adaptarlo según tu modelo de datos y estructura
        deudas = session.query(Deuda).filter_by(socio_id=socio_id, pagada=False).count()
        return deudas > 0

def obtener_deudas_socio(socio_id):
    """Obtiene las deudas pendientes de un socio, incluyendo el total de cada deuda."""
    with Session() as session:
        deudas_con_total = []
        deudas = session.query(Deuda).filter_by(socio_id=socio_id, pagada=False).all()
        for deuda in deudas:
            deuda_info = {
                "deuda": deuda,
                "total": deuda.total  # Asumiendo que Deuda tiene un campo 'total'
            }
            deudas_con_total.append(deuda_info)
        return deudas_con_total

def procesar_deuda(session, socio_id, detalles_venta, total_venta, trabajador_id):
    """
    Registra una deuda para un socio por una venta no pagada utilizando una sesión existente.

    Args:
        session: La sesión de SQLAlchemy para realizar las operaciones de base de datos.
        socio_id: El ID del socio que incurre en la deuda.
        detalles_venta: Una lista de diccionarios con los detalles de los productos vendidos y sus cantidades.
        total_venta: El total monetario de la venta que se convierte en deuda.
        trabajador_id: El ID del trabajador (usuario) que registra la deuda.

    Returns:
        El ID de la deuda registrada.
    """
    try:
        nueva_deuda = Deuda(
            socio_id=socio_id,
            fecha=datetime.now(timezone.utc),  # Asegura que la fecha sea timezone-aware
            total=total_venta,
            trabajador_id=trabajador_id,
            pagada=False
        )
        session.add(nueva_deuda)
        session.flush()  # Para obtener el ID de la nueva deuda antes de hacer commit

        for detalle in detalles_venta:
            producto = session.query(Producto).filter_by(id=detalle['producto_id']).first()
            if producto:
                detalle_venta = DetalleVenta(
                    deuda_id=nueva_deuda.id,
                    producto_id=detalle['producto_id'],
                    cantidad=detalle['cantidad'],
                    precio=producto.precio  # Utiliza el precio del modelo Producto
                )
                session.add(detalle_venta)
            else:
                raise ValueError(f"Producto con ID {detalle['producto_id']} no encontrado.")

        # No hacemos session.commit() aquí para permitir que la transacción se maneje externamente
        return nueva_deuda.id

    except SQLAlchemyError as e:
        session.rollback()
        raise e
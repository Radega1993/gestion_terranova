from datetime import datetime, timezone
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import func
from app.database.connection import Session
from app.database.models import Deuda, DetalleVenta, Producto, Socio, Venta
from app.logic.EstadoApp import EstadoApp

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
        session.flush()  # Para obtener el ID de la deuda antes de commit

        # Crear los detalles de venta asociados a la deuda
        for detalle in detalles_venta:
            producto_id = detalle["producto_id"]
            cantidad = detalle["cantidad"]
            
            # Obtener el precio del producto
            producto = session.query(Producto).filter_by(id=producto_id).first()
            if not producto:
                raise ValueError(f"Producto con ID {producto_id} no encontrado")
                
            precio = producto.precio
            
            # Crear el detalle de venta
            nuevo_detalle = DetalleVenta(
                producto_id=producto_id,
                cantidad=cantidad,
                precio=precio,
                venta_id=None  # No está asociado a una venta, sino a una deuda
            )
            session.add(nuevo_detalle)
            
        session.commit()
        return nueva_deuda.id
    except SQLAlchemyError as e:
        session.rollback()
        raise Exception(f"Error al procesar la deuda: {str(e)}")

def procesar_pago_parcial(session, deuda_id, cantidad_pagada, trabajador_id):
    """
    Procesa un pago parcial de una deuda.
    
    Args:
        session: La sesión de SQLAlchemy para realizar las operaciones de base de datos.
        deuda_id: El ID de la deuda a pagar parcialmente.
        cantidad_pagada: La cantidad que se va a pagar.
        trabajador_id: El ID del trabajador (usuario) que procesa el pago.
        
    Returns:
        El ID de la nueva deuda creada con el monto restante, o None si se pagó la deuda completa.
    """
    try:
        # Obtener la deuda
        deuda = session.query(Deuda).filter_by(id=deuda_id).first()
        if not deuda:
            raise ValueError(f"Deuda con ID {deuda_id} no encontrada")
            
        if deuda.pagada:
            raise ValueError(f"La deuda con ID {deuda_id} ya está pagada")
            
        # Verificar que la cantidad pagada no sea mayor que el total de la deuda
        if cantidad_pagada > deuda.total:
            raise ValueError(f"La cantidad pagada ({cantidad_pagada}) no puede ser mayor que el total de la deuda ({deuda.total})")
            
        # Si se paga la deuda completa
        if cantidad_pagada == deuda.total:
            deuda.pagada = True
            session.commit()
            return None
            
        # Si es un pago parcial, crear una nueva deuda con el monto restante
        monto_restante = deuda.total - cantidad_pagada
        nueva_deuda = Deuda(
            socio_id=deuda.socio_id,
            fecha=datetime.now(timezone.utc),
            total=monto_restante,
            trabajador_id=trabajador_id,
            pagada=False
        )
        session.add(nueva_deuda)
        session.flush()
        
        # Actualizar la deuda original con el monto pagado
        deuda.total = cantidad_pagada
        deuda.pagada = True
        
        session.commit()
        return nueva_deuda.id
    except SQLAlchemyError as e:
        session.rollback()
        raise Exception(f"Error al procesar el pago parcial: {str(e)}")

def obtener_deudas_agrupadas():
    with Session() as session:
        resultado = session.query(
            Socio.nombre, 
            Socio.id.label("socio_id"),
            func.sum(Deuda.total).label("total_deuda")
        ).join(Deuda, Socio.id == Deuda.socio_id).filter(
            Deuda.pagada == False
        ).group_by(Socio.id).all()

        return [{"nombre": nombre, "socio_id": socio_id, "total_deuda": total_deuda} for nombre, socio_id, total_deuda in resultado]

def procesar_pago(socio_id):
    with Session() as session:
        # 1. Crea una nueva Venta
        trabajador_id = EstadoApp.get_usuario_logueado_id()
        nueva_venta = Venta(fecha=datetime.now(timezone.utc), total=0, socio_id=socio_id, trabajador_id=trabajador_id, pagada=True)
        session.add(nueva_venta)
        session.flush()  # Para obtener el ID de la nueva venta
        
        # 2. Encuentra y actualiza las deudas y detalles de venta
        total = 0
        deudas = session.query(Deuda).filter(Deuda.socio_id == socio_id, Deuda.pagada == False).all()
        for deuda in deudas:
            deuda.pagada = True
            for detalle in deuda.detalles_venta:
                detalle.venta_id = nueva_venta.id  # Asocia el detalle de venta con la nueva venta
                total += detalle.precio * detalle.cantidad
        
        # Actualiza el total de la nueva venta
        nueva_venta.total = total

        session.commit()
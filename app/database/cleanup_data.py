import logging
from sqlalchemy import text
from app.database.connection import Session, engine
from app.database.models import Deuda, DetalleVenta, Venta

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def cleanup_data():
    session = Session()
    try:
        # Corregir detalles_venta con venta_id NULL
        session.execute(text("""
            UPDATE detalles_venta 
            SET venta_id = (
                SELECT v.id 
                FROM ventas v 
                WHERE v.fecha = (
                    SELECT MAX(fecha) 
                    FROM ventas 
                    WHERE socio_id = (
                        SELECT socio_id 
                        FROM deudas 
                        WHERE id = detalles_venta.deuda_id
                    )
                )
                AND v.socio_id = (
                    SELECT socio_id 
                    FROM deudas 
                    WHERE id = detalles_venta.deuda_id
                )
            )
            WHERE venta_id IS NULL AND deuda_id IS NOT NULL
        """))
        
        # Eliminar detalles duplicados
        session.execute(text("""
            DELETE FROM detalles_venta 
            WHERE id NOT IN (
                SELECT MIN(id) 
                FROM detalles_venta 
                GROUP BY venta_id, producto_id, cantidad, precio
            )
        """))
        
        # Corregir precios en 0
        session.execute(text("""
            UPDATE detalles_venta 
            SET precio = COALESCE(
                (
                    SELECT precio 
                    FROM productos 
                    WHERE productos.id = detalles_venta.producto_id
                    AND precio IS NOT NULL
                    AND precio > 0
                ),
                1000  -- precio por defecto si no se encuentra el producto o su precio
            )
            WHERE precio = 0
        """))
        
        # Actualizar estado de deudas
        session.execute(text("""
            UPDATE deudas 
            SET pagada_parcialmente = TRUE 
            WHERE id IN (
                SELECT d.id 
                FROM deudas d 
                JOIN detalles_venta dv ON d.id = dv.deuda_id 
                GROUP BY d.id 
                HAVING SUM(dv.cantidad * dv.precio) < d.total
            )
        """))
        
        session.commit()
        logger.info("Limpieza de datos completada exitosamente")
        
    except Exception as e:
        session.rollback()
        logger.error(f"Error durante la limpieza de datos: {str(e)}")
        raise
    finally:
        session.close()

if __name__ == "__main__":
    cleanup_data() 
from app.database.connection import Session
from app.database.models import Deuda  # Asegúrate de que Deuda es un modelo en tu base de datos

def verificar_deudas_socio(socio_id):
    """Verifica si un socio tiene deudas pendientes."""
    with Session() as session:
        # Este es un ejemplo y necesitarás adaptarlo según tu modelo de datos y estructura
        deudas = session.query(Deuda).filter_by(socio_id=socio_id, pagada=False).count()
        return deudas > 0

def obtener_deudas_socio(socio_id):
    """Obtiene las deudas pendientes de un socio."""
    with Session() as session:
        # Igualmente, adapta esta consulta a tu estructura de datos
        deudas = session.query(Deuda).filter_by(socio_id=socio_id, pagada=False).all()
        return deudas

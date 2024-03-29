# Sistema de reservas
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from datetime import datetime
from app.database.connection import Session
from app.database.models import Reserva  # Asegúrate de que este import refleje la ubicación real de tu modelo


def obtener_fechas_reservadas():
    with Session() as session:
        # Asume que la columna de fecha en tu modelo Reserva se llama 'fecha_reserva'
        reservas = session.query(Reserva.fecha_reserva).all()
        
        # Convertir las fechas a strings para ser compatibles con tkcalendar
        # Esto asume que quieres todas las reservas, sin filtrar por activas/inactivas, etc.
        fechas_reservadas = [reserva.fecha_reserva.strftime("%Y-%m-%d") for reserva in reservas]
        
        return fechas_reservadas

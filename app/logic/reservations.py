# Sistema de reservas
from datetime import datetime
from tkinter import messagebox
from app.database.connection import Session
from app.database.models import Reserva, Socio  # Asegúrate de que este import refleje la ubicación real de tu modelo
from tkcalendar import Calendar


def obtener_fechas_reservadas(session):
    reservas = session.query(Reserva.fecha_reserva).all()
    
    # Convertir las fechas a strings para ser compatibles con tkcalendar
    fechas_reservadas = [reserva.fecha_reserva.strftime("%Y-%m-%d") for reserva in reservas]
    
    return fechas_reservadas

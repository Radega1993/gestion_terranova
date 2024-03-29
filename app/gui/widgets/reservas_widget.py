import tkinter as tk
from tkinter import ttk, messagebox
from tkcalendar import Calendar

from app.logic.reservations import obtener_fechas_reservadas

class ReservasWidget(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
      
        self.create_widgets()

    def create_widgets(self):
        # Calendario para seleccionar el día de la reserva
        self.calendario = Calendar(self, selectmode='day')
        self.calendario.pack(pady=20)

        # Dropdown para seleccionar el servicio a reservar
        self.servicio_label = tk.Label(self, text="Servicio a Reservar:")
        self.servicio_label.pack()
        
        self.servicios = ["Barbacoa", "Sala", "Barbacoa + Sala", "Pista"]
        self.servicio_var = tk.StringVar()
        self.servicio_combobox = ttk.Combobox(self, textvariable=self.servicio_var, values=self.servicios, state="readonly")
        self.servicio_combobox.pack()


        # Añadir campos para el número de socio y el importe abonado
        self.socio_id_label = tk.Label(self, text="Número de Socio:")
        self.socio_id_label.pack()
        self.socio_id_entry = tk.Entry(self)
        self.socio_id_entry.pack()

        self.importe_abonado_label = tk.Label(self, text="Importe Abonado:")
        self.importe_abonado_label.pack()
        self.importe_abonado_entry = tk.Entry(self)
        self.importe_abonado_entry.pack()

        # Añadir checkboxes para opciones adicionales
        self.aire_acondicionado_var = tk.BooleanVar()
        self.aire_acondicionado_check = tk.Checkbutton(self, text="Aire Acondicionado / Calefacción (10€)", variable=self.aire_acondicionado_var)
        self.aire_acondicionado_check.pack()

        self.suplemento_exclusividad_var = tk.BooleanVar()
        self.suplemento_exclusividad_check = tk.Checkbutton(self, text="Suplemento Exclusividad (25€)", variable=self.suplemento_exclusividad_var)
        self.suplemento_exclusividad_check.pack()

        # Botón para confirmar la fecha seleccionada
        self.btn_confirmar_fecha = ttk.Button(self, text="Confirmar Fecha", command=self.confirmar_fecha)
        self.btn_confirmar_fecha.pack()


    def confirmar_fecha(self):
        fecha = self.calendario.get_date()
        # Aquí añades tu lógica para procesar y guardar la reserva
        # Después de guardar la reserva exitosamente, actualizas el calendario:
        fecha_codificada = self.calendario.cdate(fecha)
        self.calendario.calevent_create(fecha_codificada, 'Reservado', 'reserva')
        self.calendario.tag_config('reserva', background='red', foreground='white')
        messagebox.showinfo("Reserva Confirmada", f"Reserva realizada para: {fecha}")

    def cargar_reservas_existentes(self):
        # Esta es una función de ejemplo, necesitarás ajustarla según cómo accedas a tus datos de reserva
        fechas_reservadas = obtener_fechas_reservadas()  # Esta función debería devolver una lista de fechas reservadas
        
        for fecha in fechas_reservadas:
            fecha_codificada = self.calendario.cdate(fecha)
            self.calendario.calevent_create(fecha_codificada, 'Reservado', 'reserva')
            self.calendario.tag_config('reserva', background='red', foreground='white')

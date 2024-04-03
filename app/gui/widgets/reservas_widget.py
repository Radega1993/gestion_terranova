from datetime import datetime
import tkinter as tk
from tkinter import ttk, messagebox
from tkcalendar import Calendar

from app.database.connection import Session
from app.database.models import Reserva, Servicio, Socio
from app.logic.reservations import obtener_fechas_reservadas

class ReservasWidget(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.session = Session()
        self.servicios = {}
        self.create_widgets()
        self.cargar_servicios() 
        self.cargar_reservas_existentes()


    def create_widgets(self):
        # Calendario para seleccionar el día de la reserva
        self.calendario = Calendar(self, selectmode='day')
        self.calendario.pack(pady=20)

        # Dropdown para seleccionar el servicio a reservar
        self.servicio_label = tk.Label(self, text="Servicio a Reservar:")
        self.servicio_label.pack()
             
        self.servicio_var = tk.StringVar()
        self.servicio_combobox = ttk.Combobox(self, textvariable=self.servicio_var, state="readonly")
        self.servicio_combobox.pack()

        self.servicio_combobox.bind("<<ComboboxSelected>>", self.actualizar_precio_servicio)

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

        # Etiqueta para mostrar el precio del servicio seleccionado
        self.precio_servicio_label = tk.Label(self, text="Precio: ")
        self.precio_servicio_label.pack()


        # Botón para confirmar la fecha seleccionada
        self.btn_confirmar_fecha = ttk.Button(self, text="Confirmar Fecha", command=self.confirmar_fecha)
        self.btn_confirmar_fecha.pack()

        # Frame para el Listbox de reservas
        self.reservas_frame = tk.Frame(self)
        self.reservas_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        self.lista_reservas = tk.Listbox(self.reservas_frame, height=20, width=50)
        self.lista_reservas.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)
        
        # Enlazar evento de selección en el calendario
        self.calendario.bind("<<CalendarSelected>>", self.mostrar_reservas_dia)

    def confirmar_fecha(self):
        fecha = self.calendario.get_date()  # Fecha en formato 'd/m/YYYY' desde tkcalendar
        socio_id = self.socio_id_entry.get().strip()
        importe_abonado = float(self.importe_abonado_entry.get().strip())

        # Verificar la existencia del socio
        socio = self.session.query(Socio).filter_by(id=socio_id).first()
        if not socio:
            messagebox.showerror("Error", "El número de socio no existe.")
            return

        try:
            # Convierte primero a 'd/m/y', luego a objeto date
            fecha_convertida = datetime.strptime(fecha, "%m/%d/%y").strftime("%d/%m/%Y")
            fecha_reserva = datetime.strptime(fecha_convertida, "%d/%m/%Y").date()
        except ValueError as e:
            messagebox.showerror("Error de formato de fecha", str(e))
            return

        # Calcula opciones adicionales basado en checkboxes y otros inputs
        opciones_adicionales = ""
        if self.aire_acondicionado_var.get():
            opciones_adicionales += "Aire Acondicionado / Calefacción, "
        if self.suplemento_exclusividad_var.get():
            opciones_adicionales += "Suplemento Exclusividad, "
        # Ajustar según necesidad para agregar más opciones

        nueva_reserva = Reserva(
            socio_id=socio.id,  # Usa el ID del objeto socio encontrado
            fecha_reserva=fecha_reserva,
            recepcionista_id=1,  # Asume un ID de recepcionista; ajusta según sea necesario
            importe_abonado=importe_abonado,
            opciones_adicionales=opciones_adicionales.rstrip(", "),  # Elimina la última coma y espacio
            pagada=False  # Ajusta según la lógica de pago
        )
        self.session.add(nueva_reserva)
        self.session.commit()

        messagebox.showinfo("Reserva Confirmada", f"La reserva ha sido confirmada para el {fecha_reserva}.")
        self.cargar_reservas_existentes()

    def cargar_servicios(self):
        """Carga los servicios desde la base de datos y actualiza el combobox."""
        with self.session as session:
            servicios = session.query(Servicio).filter(Servicio.activo==True).all()
            self.servicios = {servicio.nombre: servicio.precio for servicio in servicios}
            self.servicio_combobox['values'] = list(self.servicios.keys())

    def actualizar_precio_servicio(self, event=None):
        """Calcula y muestra el precio total basado en el servicio y suplementos seleccionados."""
        servicio_seleccionado = self.servicio_var.get()
        precio_base = self.servicios.get(servicio_seleccionado, 0)
        precio_suplementos = 0
        if self.aire_acondicionado_var.get():
            precio_suplementos += 10
        if self.suplemento_exclusividad_var.get():
            precio_suplementos += 25
        precio_total = precio_base + precio_suplementos
        self.precio_servicio_label.config(text=f"Precio total: {precio_total}€")
    
    def cargar_reservas_existentes(self):
        fechas_reservadas = obtener_fechas_reservadas(self.session)
        for fecha in fechas_reservadas:
            # Convertir las fechas al formato esperado por tkcalendar si es necesario
            fecha_codificada = datetime.strptime(fecha, '%Y-%m-%d').date()
            self.calendario.calevent_create(fecha_codificada, 'Reservado', 'reserva')
            self.calendario.tag_config('reserva', background='red', foreground='white')

    def mostrar_reservas_dia(self, event=None):
        fecha_seleccionada = self.calendario.get_date()
        
        try:
            fecha_convertida = datetime.strptime(fecha_seleccionada, "%m/%d/%y").strftime("%d/%m/%Y")
            fecha_reserva = datetime.strptime(fecha_convertida, "%d/%m/%Y").date()
        except ValueError as e:
            messagebox.showerror("Error de formato de fecha", f"Error interpretando la fecha seleccionada: {fecha_seleccionada}\nDetalle: {str(e)}")
            return
        
        # Limpiar el listbox antes de agregar nuevas entradas
        self.lista_reservas.delete(0, tk.END)
        
        # Buscar reservas para la fecha seleccionada
        reservas_dia = self.session.query(Reserva).filter_by(fecha_reserva=fecha_reserva).all()
        
        if reservas_dia:
            # Agregar cada reserva al listbox
            for reserva in reservas_dia:
                reserva_info = f"Socio ID: {reserva.socio_id}, Servicio: {reserva.opciones_adicionales}, Importe: {reserva.importe_abonado}"
                self.lista_reservas.insert(tk.END, reserva_info)
        else:
            # No hay reservas para esta fecha
            self.lista_reservas.insert(tk.END, "No hay reservas para esta fecha.")

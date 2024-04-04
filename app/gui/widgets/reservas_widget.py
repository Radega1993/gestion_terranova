from datetime import datetime
import tkinter as tk
from tkinter import ttk, messagebox
from tkcalendar import Calendar

from app.database.connection import Session
from app.database.models import Reserva, Servicio, Socio
from app.gui.widgets.gestion_reservas_dialog import DialogoGestionReserva
from app.logic.EstadoApp import EstadoApp
from app.logic.reservations import obtener_fechas_reservadas

class ReservasWidget(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.session = Session()
        self.servicios = {}
        self.suplementos = {} 
        self.suplementos_vars = {}
        self.create_widgets()
        self.cargar_servicios_suplementos()
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

        # Añadir checkboxes para opciones adicionales
        self.frame_suplementos = tk.Frame(self)
        self.frame_suplementos.pack(pady=10)

        self.importe_abonado_label = tk.Label(self, text="Importe Abonado:")
        self.importe_abonado_label.pack()
        self.importe_abonado_entry = tk.Entry(self)
        self.importe_abonado_entry.pack()

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
        self.lista_reservas.bind("<Double-1>", self.abrir_dialogo_reserva)
        
    def confirmar_fecha(self):
        fecha = self.calendario.get_date()  # Fecha en formato 'd/m/YYYY' desde tkcalendar
        socio_id = self.socio_id_entry.get().strip()
        servicio_seleccionado = self.servicio_var.get()
        precio_base = self.servicios[servicio_seleccionado]
        importe_abonado_str = self.importe_abonado_entry.get().strip()
        importe_abonado = float(importe_abonado_str) if importe_abonado_str else 0
        trabajador_id = EstadoApp.get_usuario_logueado_id()

        # Verificar la existencia del socio
        socio = self.session.query(Socio).filter_by(id=socio_id).first()
        if not socio:
            messagebox.showerror("Error", "El número de socio no existe.")
            return

        try:
            fecha_convertida = datetime.strptime(fecha, "%m/%d/%y").strftime("%d/%m/%Y")
            fecha_reserva = datetime.strptime(fecha_convertida, "%d/%m/%Y").date()
        except ValueError as e:
            messagebox.showerror("Error de formato de fecha", str(e))
            return
        
        total_suplementos = sum(self.suplementos[suplemento] for suplemento, var in self.suplementos_vars.items() if var.get())
        precio_total = precio_base + total_suplementos

        opciones_adicionales = [suplemento for suplemento, check_var in self.suplementos_vars.items() if check_var.get()]
        opciones_adicionales_str = ", ".join(opciones_adicionales)

        # Obtener el ID del servicio seleccionado
        with self.session as session:
            servicio = session.query(Servicio).filter_by(nombre=servicio_seleccionado, activo=True).first()
            if servicio is None:
                messagebox.showerror("Error", "Servicio seleccionado no válido.")
                return
            
            reserva_existente = session.query(Reserva).filter_by(fecha_reserva=fecha_reserva, servicio_id=servicio.id, en_lista_de_espera=False).first()

            if reserva_existente:
                respuesta = messagebox.askyesno("Lista de espera", "Este servicio ya está reservado para este día. ¿Quieres ser añadido a la lista de espera?")
                if not respuesta:
                    return
                en_lista_de_espera = True
            else:
                en_lista_de_espera = False
            
            en_lista_de_espera = bool(reserva_existente)
            
            if not en_lista_de_espera and not (precio_total / 2 <= importe_abonado <= precio_total):
                messagebox.showerror("Error de Importe", "El importe abonado debe ser entre el 50% y el 100% del precio total.")
                return
            
            nueva_reserva = Reserva(
                socio_id=socio.id,
                fecha_reserva=fecha_reserva,
                recepcionista_id=trabajador_id,
                servicio_id=servicio.id,
                importe_abonado=importe_abonado,
                precio=precio_total,
                opciones_adicionales=opciones_adicionales_str,
                pagada=importe_abonado == precio_total,
                en_lista_de_espera=en_lista_de_espera,
            )

            
            session.add(nueva_reserva)
            session.commit()

            estado_reserva = "en lista de espera" if en_lista_de_espera else "confirmada"
            messagebox.showinfo("Reserva " + estado_reserva, f"La reserva ha sido {estado_reserva} para el {fecha_reserva}.")
            self.cargar_reservas_existentes()

    def cargar_servicios_suplementos(self):
        with self.session as session:
            # Carga servicios y suplementos
            servicios_query = session.query(Servicio).filter(Servicio.tipo == 'servicio', Servicio.activo == True).all()
            self.servicios = {servicio.nombre: servicio.precio for servicio in servicios_query}
            self.servicio_combobox['values'] = list(self.servicios.keys())

            suplementos_query = session.query(Servicio).filter(Servicio.tipo == 'suplemento', Servicio.activo == True).all()
            for suplemento in suplementos_query:
                check_var = tk.BooleanVar()
                check_button = tk.Checkbutton(self.frame_suplementos, text=f"{suplemento.nombre} ({suplemento.precio}€)", variable=check_var)
                check_button.pack(anchor='w')
                check_var.trace_add("write", lambda *args: self.actualizar_precio_servicio())
                self.suplementos[suplemento.nombre] = suplemento.precio
                self.suplementos_vars[suplemento.nombre] = check_var
    
    def actualizar_precio_servicio(self, event=None):
        servicio_seleccionado = self.servicio_var.get()
        precio_base = self.servicios.get(servicio_seleccionado, 0)
        
        total_suplementos = sum(self.suplementos[suplemento] for suplemento, var in self.suplementos_vars.items() if var.get())
        precio_total = precio_base + total_suplementos
        
        self.precio_servicio_label.config(text=f"Precio total: {precio_total}€")

    def cargar_reservas_existentes(self):
        # Limpia cualquier evento existente en el calendario
        for eid in self.calendario.get_calevents():
            self.calendario.calevent_remove(eid)
        
        fechas_reservadas = obtener_fechas_reservadas(self.session)
        for fecha in fechas_reservadas:
            # Convertir las fechas al formato esperado por tkcalendar si es necesario
            fecha_codificada = datetime.strptime(fecha, '%Y-%m-%d').date()
            self.calendario.calevent_create(fecha_codificada, 'Reservado', 'reserva')
            self.calendario.tag_config('reserva', background='red', foreground='white')
        
        self.mostrar_reservas_dia()

    def mostrar_reservas_dia(self, event=None):
        fecha_seleccionada = self.calendario.get_date()

        try:
            fecha_convertida = datetime.strptime(fecha_seleccionada, "%m/%d/%y").strftime("%d/%m/%Y")
            fecha_reserva = datetime.strptime(fecha_convertida, "%d/%m/%Y").date()
        except ValueError as e:
            messagebox.showerror("Error de formato de fecha", str(e))
            return

        # Limpiar el listbox antes de agregar nuevas entradas
        self.lista_reservas.delete(0, tk.END)

        # Buscar reservas para la fecha seleccionada incluyendo nombre del socio y del servicio
        with self.session as session:
            reservas_dia = session.query(Reserva, Socio.nombre, Servicio.nombre).\
                join(Socio, Reserva.socio_id == Socio.id).\
                join(Servicio, Reserva.servicio_id == Servicio.id).\
                filter(Reserva.fecha_reserva == fecha_reserva).all()

        if reservas_dia:
            for reserva, nombre_socio, nombre_servicio in reservas_dia:
                estado_reserva = "En lista de espera" if reserva.en_lista_de_espera else "Confirmada"
                reserva_info = f"ID: {reserva.id}, Socio: {nombre_socio}, Servicio: {nombre_servicio}, Adicionales: {reserva.opciones_adicionales}, Importe: {reserva.importe_abonado}, Restante:{reserva.precio - reserva.importe_abonado}, Pagada: {reserva.pagada}, Estado: {estado_reserva}"
                self.lista_reservas.insert(tk.END, reserva_info)
        else:
            self.lista_reservas.insert(tk.END, "No hay reservas para esta fecha.")

    def abrir_dialogo_reserva(self, event):
        seleccion = self.lista_reservas.curselection()
        if not seleccion:
            return
        
        # Obtiene el ID de la reserva seleccionada. Esto requerirá que ajustes cómo listas las reservas para incluir el ID.
        reserva_id = self.lista_reservas.get(seleccion[0]).split(',')[0]  # Ajusta según cómo listes las reservas
        
        # Ahora, abre el diálogo pasándole el ID de la reserva
        DialogoGestionReserva(self, reserva_id)
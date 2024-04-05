import tkinter as tk
from tkinter import messagebox, ttk
from tkcalendar import DateEntry
from app.database.connection import Session
from sqlalchemy import func, and_
from app.database.models import Venta, Reserva, Producto, Usuario
from datetime import datetime

class RecaudacionesManagementWidget(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.configure(bg='#f0f0f0')
        self.session = Session()

        style = ttk.Style()
        style.configure("Treeview", font=('Helvetica', 12), rowheight=25)
        style.configure("Treeview.Heading", font=('Helvetica', 13, 'bold'))
        
        self.trabajador_id = None
        
        self.create_widgets()
        self.populate_workers()
        self.populate_summary()

    def create_widgets(self):
        # Selector de trabajador
        self.trabajador_var = tk.StringVar()
        self.trabajador_combobox = ttk.Combobox(self, textvariable=self.trabajador_var, state="readonly")
        self.trabajador_combobox.pack(pady=10)

        # Conectar el evento de selección en el combobox al método on_trabajador_selected
        self.trabajador_combobox.bind("<<ComboboxSelected>>", self.on_trabajador_selected)

        # Selectores de fecha
        ttk.Label(self, text="Fecha inicio:").pack(pady=5)
        self.fecha_inicio = DateEntry(self, date_pattern='d/m/Y', width=12, background='darkblue', foreground='white', borderwidth=2)
        self.fecha_inicio.pack(pady=5)
        ttk.Label(self, text="Fecha fin:").pack(pady=5)
        self.fecha_fin = DateEntry(self, date_pattern='d/m/Y', width=12, background='darkblue', foreground='white', borderwidth=2)
        self.fecha_fin.pack(pady=5)

        ttk.Button(self, text="Consultar", command=self.populate_summary).pack(pady=10)

        # Treeview para los resultados
        self.summary_treeview = ttk.Treeview(self, columns=("Tipo", "Total"), show="headings")
        self.summary_treeview.heading("Tipo", text="Tipo")
        self.summary_treeview.heading("Total", text="Total Recaudado")
        self.summary_treeview.pack(expand=True, fill="both", pady=10)

    def populate_workers(self):
        # Llenar el combobox de trabajador con los usuarios
        with self.session as session:
            trabajadores = session.query(Usuario).all()
            trabajador_values = ['Todos'] + [f"id: {trabajador.id}, nombre: {trabajador.nombre}" for trabajador in trabajadores]
            self.trabajador_combobox['values'] = trabajador_values
            self.trabajador_combobox.set("Todos")

    def on_trabajador_selected(self, event=None):
        # Esta función se debe llamar cuando se selecciona un trabajador en el combobox
        seleccion = self.trabajador_combobox.get()
        if seleccion != "Todos":
            trabajador_id = int(seleccion.split(',')[0].split(': ')[1])
            # Ahora tienes el ID del trabajador que puedes usar para filtrar tus consultas
        else:
            trabajador_id = None  # Significa que se seleccionó "Todos"

    def populate_summary(self):
        inicio = self.fecha_inicio.get_date()
        fin = self.fecha_fin.get_date()

        # Limpiar el treeview
        for i in self.summary_treeview.get_children():
            self.summary_treeview.delete(i)

        with self.session as session:
            if self.trabajador_id:
                # Consultas filtrando por trabajador específico
                total_productos = session.query(func.sum(Venta.total)) \
                                .filter(Venta.fecha >= inicio, Venta.fecha <= fin, Venta.trabajador_id == self.trabajador_id) \
                                .scalar()
                total_servicios = session.query(func.sum(Reserva.importe_abonado)) \
                                .filter(Reserva.fecha_creacion >= inicio, Reserva.fecha_creacion <= fin, Reserva.recepcionista_id == self.trabajador_id) \
                                .scalar()
            else:
                # Consultas sin filtrar por trabajador
                total_productos = session.query(func.sum(Venta.total)) \
                                .filter(Venta.fecha >= inicio, Venta.fecha <= fin) \
                                .scalar()
                total_servicios = session.query(func.sum(Reserva.importe_abonado)) \
                                .filter(Reserva.fecha_creacion >= inicio, Reserva.fecha_creacion <= fin) \
                                .scalar()

            self.summary_treeview.insert("", "end", values=("Productos", total_productos or 0))
            self.summary_treeview.insert("", "end", values=("Servicios", total_servicios or 0))

import tkinter as tk
from tkinter import messagebox, ttk
from tkinter import filedialog
from tkcalendar import DateEntry
from app.database.connection import Session
from app.database.models import DetalleVenta, Servicio, Socio, Venta, Reserva, Producto, Usuario
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib import colors
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

        # Sección de resumen usando etiquetas
        self.resumen_frame = tk.Frame(self, bg='#f0f0f0')
        self.resumen_frame.pack(fill=tk.X, padx=10, pady=10)

        self.total_productos_label = tk.Label(self.resumen_frame, text="Total Productos: $0", bg='#f0f0f0')
        self.total_productos_label.pack(side=tk.LEFT)

        self.total_reservas_label = tk.Label(self.resumen_frame, text="Total Reservas: $0", bg='#f0f0f0')
        self.total_reservas_label.pack(side=tk.LEFT, padx=10)

        self.total_recaudado_label = tk.Label(self.resumen_frame, text="Total Recaudado: $0", bg='#f0f0f0')
        self.total_recaudado_label.pack(side=tk.LEFT, padx=10)
        
        ttk.Button(self, text="Export to PDF", command=self.export_to_pdf).pack(pady=10)

        ttk.Label(self, text="Detalle de transacciones:").pack(pady=10)
        self.details_treeview = ttk.Treeview(self, columns=("Fecha", "Trabajador", "Socio", "Tipo", "Detalle", "Monto"), show="headings")
        self.details_treeview.heading("Fecha", text="Fecha")
        self.details_treeview.heading("Trabajador", text="Trabajador")  # Ensure this matches the column name
        self.details_treeview.heading("Socio", text="Socio")
        self.details_treeview.heading("Tipo", text="Tipo")
        self.details_treeview.heading("Detalle", text="Detalle")
        self.details_treeview.heading("Monto", text="Monto")
        self.details_treeview.pack(expand=True, fill="both", pady=10)

    def populate_workers(self):
        # Llenar el combobox de trabajador con los usuarios
        with self.session as session:
            trabajadores = session.query(Usuario).all()
            trabajador_values = ['Todos'] + [f"id: {trabajador.id}, nombre: {trabajador.nombre}" for trabajador in trabajadores]
            self.trabajador_combobox['values'] = trabajador_values
            self.trabajador_combobox.set("Todos")

    def on_trabajador_selected(self, event=None):
        seleccion = self.trabajador_combobox.get()
        if seleccion != "Todos":
            self.trabajador_id = int(seleccion.split(',')[0].split(': ')[1])
        else:
            self.trabajador_id = None

    def populate_summary(self):
        inicio = self.fecha_inicio.get_date()
        fin = self.fecha_fin.get_date()

        # Ensure the treeviews are cleared before populating
        for i in self.details_treeview.get_children():
            self.details_treeview.delete(i)

        with self.session as session:
            # Apply filtering based on the selected trabajador_id
            trabajador_filter = Venta.trabajador_id == self.trabajador_id if self.trabajador_id else True
            recepcionista_filter = Reserva.recepcionista_id == self.trabajador_id if self.trabajador_id else True

            sales_details = session.query(
                Venta.fecha,
                Usuario.nombre.label("trabajador"),
                Socio.id.label("socio_id"),
                Socio.nombre.label("socio_nombre"),
                Producto.nombre,
                DetalleVenta.cantidad,
                (DetalleVenta.precio * DetalleVenta.cantidad).label("monto")
            ).join(Venta.trabajador)\
            .join(Venta.socio, isouter=True)\
            .join(DetalleVenta, DetalleVenta.venta_id == Venta.id)\
            .join(Producto, DetalleVenta.producto_id == Producto.id)\
            .filter(Venta.fecha >= inicio, Venta.fecha <= fin, trabajador_filter)\
            .all()

            reservation_details = session.query(
                Reserva.fecha_creacion,
                Usuario.nombre.label("recepcionista"),
                Socio.id.label("socio_id"),
                Socio.nombre.label("socio_nombre"),
                Servicio.nombre,
                Reserva.importe_abonado
            ).join(Reserva.recepcionista)\
            .join(Reserva.socio, isouter=True)\
            .join(Servicio, Reserva.servicio_id == Servicio.id)\
            .filter(Reserva.fecha_creacion >= inicio, Reserva.fecha_creacion <= fin, recepcionista_filter)\
            .all()

            # Inside populate_summary, when inserting into details_treeview
            for fecha, trabajador, socio_id, socio_nombre, producto, cantidad, monto in sales_details:
                self.details_treeview.insert("", "end", values=(
                    fecha.strftime('%d/%m/%Y'), trabajador, f"ID: {socio_id} - Nombre: {socio_nombre}", "Venta", f"{producto} x{cantidad}", f"${monto}"
                ))

            for fecha, trabajador, socio_id, socio_nombre, servicio, monto in reservation_details:
                self.details_treeview.insert("", "end", values=(
                    fecha.strftime('%d/%m/%Y'), trabajador, f"ID: {socio_id} - Nombre: {socio_nombre}", "Reserva", servicio, f"${monto}"
                ))

            # Update the total labels with computed totals
            total_productos = sum(monto for *_, monto in sales_details)
            total_reservas = sum(monto for *_, monto in reservation_details)
            total_recaudado = total_productos + total_reservas

            # Update labels with new totals
            self.total_productos_label.config(text=f"Total Productos: ${total_productos}")
            self.total_reservas_label.config(text=f"Total Reservas: ${total_reservas}")
            self.total_recaudado_label.config(text=f"Total Recaudado: ${total_recaudado}")

    def export_to_pdf(self):
        filepath = filedialog.asksaveasfilename(defaultextension=".pdf",
                                                filetypes=[("PDF files", "*.pdf")])
        if not filepath:
            return

        c = canvas.Canvas(filepath, pagesize=letter)
        width, height = letter

        # Adjust the font size and spacing
        c.setFont("Helvetica-Bold", 14)
        c.drawString(30, height - 40, "Informe de recaudaciones de Terranova")
        c.setFont("Helvetica", 10)
        report_info_y = height - 60
        c.drawString(30, report_info_y, f"Fecha del informe: {datetime.now().strftime('%d/%m/%Y')}")
        c.drawString(30, report_info_y - 15, f"Periodo: {self.fecha_inicio.get_date().strftime('%d/%m/%Y')} - {self.fecha_fin.get_date().strftime('%d/%m/%Y')}")
        c.drawString(30, report_info_y - 30, f"{self.total_productos_label.cget('text')}, {self.total_reservas_label.cget('text')}, {self.total_recaudado_label.cget('text')}")

        # Adjust column widths based on the page size
        column_widths = [70, 90, 100, 45, 155, 60]  # Adjust to fit your needs
        columns = ["Fecha", "Trabajador", "Socio", "Tipo", "Detalle", "Monto"]
        y = height - 125

        # Draw the table headers
        x = 30
        for i, column in enumerate(columns):
            c.drawString(x, y, column)
            x += column_widths[i]

        y -= 20
        c.setFont("Helvetica", 9)

        # Populate table rows
        for child in self.details_treeview.get_children():
            values = self.details_treeview.item(child, "values")
            x = 30
            for i, value in enumerate(values):
                c.drawString(x, y, str(value))
                x += column_widths[i]
            y -= 15
            if y < 50:  # Add a new page if there's not enough space
                c.showPage()
                y = height - 50
                c.setFont("Helvetica", 9)

        c.save()
        messagebox.showinfo("Export Successful", f"The data was successfully exported to {filepath}.")

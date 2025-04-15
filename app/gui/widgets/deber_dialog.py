import tkinter as tk
from tkinter import ttk
from app.database.connection import Session
from app.database.models import Deuda, DetalleVenta, Producto

class DeudaDetalleDialog(tk.Toplevel):
    def __init__(self, parent, socio_id):
        super().__init__(parent)
        self.transient(parent)
        self.title(f"Detalle de Deudas para el socio ID: {socio_id}")

        # Configuración del Treeview
        self.tree = ttk.Treeview(self, columns=("Fecha", "Producto", "Cantidad", "Precio Unitario", "Precio Total"), show="headings")
        self.tree.heading("Fecha", text="Fecha")
        self.tree.heading("Producto", text="Producto")
        self.tree.heading("Cantidad", text="Cantidad")
        self.tree.heading("Precio Unitario", text="Precio Unitario")
        self.tree.heading("Precio Total", text="Precio Total")

        # Suponiendo que tienes una función que obtiene el detalle de deudas por socio
        detalles_deuda = obtener_detalle_deudas_socio(socio_id)

        for detalle in detalles_deuda:
            self.tree.insert('', tk.END, values=(detalle['fecha'], detalle['producto'], detalle['cantidad'], f"{detalle['precio']}€", f"{detalle['total']}€"))

        self.tree.pack(fill=tk.BOTH, expand=True)

        tk.Button(self, text="Cerrar", command=self.destroy).pack()

        self.update()
        self.grab_set()
        
        self.wait_window(self)

def obtener_detalle_deudas_socio(socio_id):
    session = Session()
    try:
        # Obtener solo las deudas no pagadas y no pagadas parcialmente
        deudas = session.query(Deuda).filter(
            Deuda.socio_id == socio_id, 
            Deuda.pagada == False,
            Deuda.pagada_parcialmente == False
        ).all()
        
        detalles = {}
        
        for deuda in deudas:
            for detalle_venta in deuda.detalles_venta:
                # Solo procesar si la cantidad es mayor que 0
                if detalle_venta.cantidad > 0:
                    producto = session.query(Producto).filter(Producto.id == detalle_venta.producto_id).first()
                    if producto:
                        clave = (deuda.fecha.strftime("%Y-%m-%d"), producto.nombre)
                        if clave not in detalles:
                            detalles[clave] = {
                                'cantidad': 0,
                                'precio': detalle_venta.precio,
                                'total': 0
                            }
                        detalles[clave]['cantidad'] += detalle_venta.cantidad
                        detalles[clave]['total'] += detalle_venta.cantidad * detalle_venta.precio
        
        return detalles
    finally:
        session.close()

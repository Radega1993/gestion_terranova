import tkinter as tk
from tkinter import ttk
from app.database.connection import Session
from app.database.models import Deuda, DetalleVenta

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
            self.tree.insert('', tk.END, values=(detalle['fecha'], detalle['producto'], detalle['cantidad'], f"{detalle['precio_unitario']}€", f"{detalle['precio_total']}€"))

        self.tree.pack(fill=tk.BOTH, expand=True)

        tk.Button(self, text="Cerrar", command=self.destroy).pack()

        self.update()
        self.grab_set()
        
        self.wait_window(self)

def obtener_detalle_deudas_socio(socio_id):
    with Session() as session:
        # Filtra solo las deudas que no han sido pagadas y pertenecen al socio dado
        detalles_deuda = session.query(Deuda)\
                            .filter(Deuda.socio_id == socio_id, Deuda.pagada == False)\
                            .join(DetalleVenta).all()

        # Diccionario para agrupar los detalles por fecha y producto
        agrupados = {}
        for deuda in detalles_deuda:
            for detalle_venta in deuda.detalles_venta:
                clave = (deuda.fecha.strftime("%Y-%m-%d"), detalle_venta.producto.nombre)
                
                if clave not in agrupados:
                    agrupados[clave] = {
                        "cantidad": 0,
                        "precio_total": 0.0,
                        "precio_unitario": detalle_venta.precio  # Asumiendo precio uniforme por producto
                    }
                
                agrupados[clave]["cantidad"] += detalle_venta.cantidad
                agrupados[clave]["precio_total"] += detalle_venta.precio * detalle_venta.cantidad

        # Transformar los resultados agrupados en el formato deseado
        detalle_deudas_formato = []
        for (fecha, producto), datos in agrupados.items():
            detalle_deuda_formato = {
                "fecha": fecha,
                "producto": producto,
                "cantidad": datos["cantidad"],
                "precio_unitario": datos["precio_unitario"],
                "precio_total": datos["precio_total"]
            }
            detalle_deudas_formato.append(detalle_deuda_formato)

        session.close()
        return detalle_deudas_formato

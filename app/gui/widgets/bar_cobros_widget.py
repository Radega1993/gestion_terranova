# app/gui/widgets/bar_cobros_widget.py
import tkinter as tk
from tkinter import ttk, messagebox
from app.gui.widgets.socio_dialog import abrir_dialogo_socio 
from app.logic.stock import obtener_productos
from app.logic.socios import obtener_socio_por_id
from app.logic.sales import procesar_venta
from app.logic.deudas import verificar_deudas_socio


class BarCobrosWidget(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.productos_consumidos = []
        self.total_consumicion = 0
        self.create_widgets()
        self.cargar_stock_productos()

    def create_widgets(self):
        # Configuración de la zona de datos del socio
        self.frame_datos_socio = tk.Frame(self, borderwidth=2, relief=tk.GROOVE)
        self.frame_datos_socio.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)

        tk.Label(self.frame_datos_socio, text="ID Socio:").pack(pady=(10,0))
        self.entry_id_socio = tk.Entry(self.frame_datos_socio)
        self.entry_id_socio.pack(pady=5)

        self.btn_confirmar_socio = tk.Button(self.frame_datos_socio, text="Confirmar Socio", command=self.confirmar_socio)
        self.btn_confirmar_socio.pack(pady=(0,10))

        self.label_info_socio = tk.Label(self.frame_datos_socio, text="", wraplength=400)
        self.label_info_socio.pack(pady=(5, 0))

        self.label_estado_deuda = tk.Label(self.frame_datos_socio, text="")
        self.label_estado_deuda.pack(pady=(5, 0))

        # Configuración de la zona de stock de productos
        self.frame_stock_productos = tk.Frame(self, borderwidth=2, relief=tk.GROOVE)
        self.frame_stock_productos.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)

        self.lista_productos_stock = ttk.Treeview(self.frame_stock_productos, columns=("Producto", "Precio"), show="headings")
        self.lista_productos_stock.heading("Producto", text="Producto")
        self.lista_productos_stock.heading("Precio", text="Precio")
        self.lista_productos_stock.pack(fill=tk.BOTH, expand=True)
        self.lista_productos_stock.bind("<Double-1>", self.añadir_producto_consumido)

        # Configuración de la zona de productos consumidos
        self.frame_productos_consumidos = tk.Frame(self, borderwidth=2, relief=tk.GROOVE)
        self.frame_productos_consumidos.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)

        self.lista_productos_consumidos = ttk.Treeview(self.frame_productos_consumidos, columns=("Producto", "Precio"), show="headings")
        self.lista_productos_consumidos.heading("Producto", text="Producto")
        self.lista_productos_consumidos.heading("Precio", text="Precio")
        self.lista_productos_consumidos.pack(fill=tk.BOTH, expand=True)

        # Etiqueta para mostrar el precio total
        self.label_precio_total = tk.Label(self.frame_productos_consumidos, text="Precio total: 0")
        self.label_precio_total.pack(pady=(10, 5))

       # Botón para finalizar compra como pagada
        self.btn_compra_pagada = tk.Button(self.frame_productos_consumidos, text="Compra Pagada", command=lambda: self.finalizar_compra(pagada=True))
        self.btn_compra_pagada.pack(pady=5)

        # Botón para finalizar compra como deuda
        self.btn_compra_deuda = tk.Button(self.frame_productos_consumidos, text="Dejar como Deuda", command=lambda: self.finalizar_compra(pagada=False))
        self.btn_compra_deuda.pack(pady=5)

    def confirmar_socio(self):
        socio_id = self.entry_id_socio.get()
        if not socio_id.isdigit():
            messagebox.showwarning("Advertencia", "El ID del socio debe ser un número.")
            return
        socio_id = int(socio_id)
        socio = obtener_socio_por_id(socio_id)
        if socio:
            self.socio_actual = socio
            deudas = verificar_deudas_socio(socio_id)
            deudas_info = "Tiene deudas pendientes." if deudas else "No tiene deudas pendientes."
            
            # Actualizar el texto del label con la información del socio y sus deudas
            info_text = f"Socio: {socio.nombre}\nCorreo: {socio.correo_electronico}\n{deudas_info}"
            self.label_info_socio.config(text=info_text)
        else:
            messagebox.showerror("Error", "Socio no encontrado.")
            # Limpiar el texto del label si el socio no se encuentra
            self.label_info_socio.config(text="")


    def cargar_stock_productos(self):
    # Limpia la lista de productos para asegurar que no haya duplicados
        for i in self.lista_productos_stock.get_children():
            self.lista_productos_stock.delete(i)
        
        # Obtiene la lista de productos desde la base de datos
        productos = obtener_productos()
        
        # Añade los productos al Treeview
        for producto in productos:
            if producto.stock_actual > 0:  # Asume que solo quieres mostrar productos con stock disponible
                self.lista_productos_stock.insert("", "end", values=(producto.nombre, producto.precio))

    def añadir_producto_consumido(self, event):
         # Obtener el ítem seleccionado
        seleccion = self.lista_productos_stock.selection()
        if not seleccion:
            return  # No hacer nada si no hay selección
        item = self.lista_productos_stock.item(seleccion)
        nombre_producto, precio_producto = item['values']

        # Solicitar la cantidad a consumir
        cantidad = tk.simpledialog.askinteger("Cantidad", "¿Cuántas unidades?", minvalue=1)
        if cantidad is None:  # Si el usuario cancela, no hacer nada
            return

        # Añadir el producto y la cantidad a la lista de productos consumidos
        self.productos_consumidos.append((nombre_producto, precio_producto, cantidad))

        # Actualizar la lista de productos consumidos en la UI
        self.lista_productos_consumidos.insert("", "end", values=(nombre_producto, f'{precio_producto} x {cantidad} = {precio_producto * cantidad}'))
        
        # Actualizar el precio total y mostrarlo en la etiqueta
        self.total_consumicion += float(precio_producto) * float(cantidad)
        self.label_precio_total.config(text=f"Precio total: {self.total_consumicion}")

    def finalizar_compra(self, pagada):
        if not self.socio_actual:
            messagebox.showerror("Error", "No se ha seleccionado un socio.")
            return
        
        # Aquí implementarías la lógica para procesar la venta, actualizar el stock y marcar la venta como pagada o deuda
        detalles_venta = [{"producto_id": p['id'], "cantidad": p['cantidad']} for p in self.productos_consumidos]
        try:
            venta_id = procesar_venta(self.session, detalles_venta)
            messagebox.showinfo("Compra finalizada", f"La compra ha sido {'pagada' if pagada else 'dejada como deuda'} con éxito. ID de venta: {venta_id}")
            # Limpiar la interfaz y preparar para la siguiente venta
        except Exception as e:
            messagebox.showerror("Error al procesar la venta", str(e))
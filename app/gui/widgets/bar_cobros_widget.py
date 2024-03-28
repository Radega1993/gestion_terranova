# app/gui/widgets/bar_cobros_widget.py
import tkinter as tk
from tkinter import ttk, messagebox
from sqlalchemy import func
from app.database.connection import Session
from app.database.models import Deuda
from app.logic.EstadoApp import EstadoApp 

from app.logic.stock import obtener_productos, actualizar_stock
from app.logic.socios import obtener_socio_por_id
from app.logic.sales import procesar_venta
from app.logic.deudas import procesar_deuda


class BarCobrosWidget(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.socio_actual = None
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

        self.lista_productos_stock = ttk.Treeview(self.frame_stock_productos, columns=("ID", "Producto", "Precio", "Stock"), show="headings")
        self.lista_productos_stock.heading("ID", text="ID")  # Configura la cabecera de la nueva columna ID
        self.lista_productos_stock.heading("Producto", text="Producto")
        self.lista_productos_stock.heading("Precio", text="Precio")
        self.lista_productos_stock.heading("Stock", text="Stock")
        self.lista_productos_stock.pack(fill=tk.BOTH, expand=True)
        self.lista_productos_stock.bind("<Double-1>", self.añadir_producto_consumido)

        # Configuración de la zona de productos consumidos
        self.frame_productos_consumidos = tk.Frame(self, borderwidth=2, relief=tk.GROOVE)
        self.frame_productos_consumidos.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)

        self.lista_productos_consumidos = ttk.Treeview(self.frame_productos_consumidos, columns=("Producto", "Cantidad"), show="headings")
        self.lista_productos_consumidos.heading("Producto", text="Producto")
        self.lista_productos_consumidos.heading("Cantidad", text="Cantidad")
        self.lista_productos_consumidos.pack(fill=tk.BOTH, expand=True)
        self.lista_productos_consumidos.bind("<Double-1>", self.eliminar_producto_seleccionado)
    
        # Etiqueta para mostrar el precio total
        self.label_precio_total = tk.Label(self.frame_productos_consumidos, text="Precio total: 0")
        self.label_precio_total.pack(pady=(10, 5))

       # Botón para finalizar compra como pagada
        self.btn_compra_pagada = tk.Button(self.frame_productos_consumidos, text="Compra Pagada", command=lambda: self.finalizar_compra(pagada=True))
        self.btn_compra_pagada.pack(pady=5)

        # Botón para finalizar compra como deuda
        self.btn_compra_deuda = tk.Button(self.frame_productos_consumidos, text="Dejar como Deuda", command=lambda: self.finalizar_compra(pagada=False))
        self.btn_compra_deuda.pack(pady=5)

    def obtener_total_deudas_socio(self, socio_id):
        """Obtiene el total de las deudas pendientes de un socio."""
        with Session() as session:
            total_deuda = session.query(func.sum(Deuda.total))\
                                 .filter(Deuda.socio_id == socio_id, Deuda.pagada == False)\
                                 .scalar()
            return total_deuda if total_deuda is not None else 0

    def confirmar_socio(self):
        socio_id = self.entry_id_socio.get()
        if not socio_id.isdigit():
            messagebox.showwarning("Advertencia", "El ID del socio debe ser un número.")
            return
        socio_id = int(socio_id)
        socio = obtener_socio_por_id(socio_id)
        if socio:
            self.socio_actual = socio
            total_deudas = self.obtener_total_deudas_socio(socio_id)
            deudas_info = f"Tiene deudas pendientes por un total de {total_deudas}€." if total_deudas > 0 else "No tiene deudas pendientes."
            
            # Actualizar el texto del label con la información del socio, sus deudas y el total adeudado
            info_text = f"Socio: {socio.nombre}\nCorreo: {socio.correo_electronico}\n{deudas_info}"
            self.label_info_socio.config(text=info_text)
        else:
            messagebox.showerror("Error", "Socio no encontrado.")
            self.label_info_socio.config(text="")


    def cargar_stock_productos(self):
    # Limpia la lista de productos para asegurar que no haya duplicados
        for i in self.lista_productos_stock.get_children():
            self.lista_productos_stock.delete(i)
        
        # Obtiene la lista de productos desde la base de datos
        productos = obtener_productos()
        
        # Añade los productos al Treeview
        for producto in productos:
            if producto.stock_actual > 0:
                self.lista_productos_stock.insert("", "end", values=(producto.id, producto.nombre, producto.precio, producto.stock_actual))

    def añadir_producto_consumido(self, event):
        # Obtener el ítem seleccionado
        seleccion = self.lista_productos_stock.selection()
        if not seleccion:
            return  # No hacer nada si no hay selección
        item = self.lista_productos_stock.item(seleccion)
        producto_id, nombre_producto, precio_producto, stock_disponible = item['values']

        # Solicitar la cantidad a consumir
        cantidad = tk.simpledialog.askinteger("Cantidad", f"¿Cuántas unidades de {nombre_producto}? (Stock disponible: {stock_disponible})", minvalue=1, maxvalue=stock_disponible)
        if cantidad is None or cantidad > stock_disponible:  # Si el usuario cancela o solicita más del stock disponible
            messagebox.showerror("Error", "Cantidad no válida o excede el stock disponible.")
            return

        # Convertir precio_producto a float para la operación matemática
        precio_producto = float(precio_producto)

        # Añadir el producto y la cantidad a la lista de productos consumidos
        self.productos_consumidos.append({"id": producto_id, "nombre": nombre_producto, "precio": precio_producto, "cantidad": cantidad})

        # Actualizar la lista de productos consumidos en la UI
        self.actualizar_lista_productos_consumidos()

        # Actualizar el precio total y mostrarlo en la etiqueta
        self.total_consumicion += precio_producto * cantidad
        self.label_precio_total.config(text=f"Precio total: {self.total_consumicion}€")

        # Actualizar el stock en la lista de productos disponibles
        nuevo_stock = stock_disponible - cantidad
        self.lista_productos_stock.item(seleccion, values=(producto_id, nombre_producto, precio_producto, nuevo_stock))

    def actualizar_lista_productos_consumidos(self):
        # Limpia la lista actual para evitar duplicados
        for i in self.lista_productos_consumidos.get_children():
            self.lista_productos_consumidos.delete(i)
        
        # Recorre la lista de productos consumidos para añadirlos a la UI
        for producto in self.productos_consumidos:
            self.lista_productos_consumidos.insert("", "end", values=(producto["nombre"], f'{producto["cantidad"]} unidad(es)', f'{producto["precio"] * producto["cantidad"]}€'))
        
    def eliminar_producto_seleccionado(self, event=None):
        seleccion = self.lista_productos_consumidos.selection()
        if seleccion:
            # Obtener los detalles del producto seleccionado
            item = self.lista_productos_consumidos.item(seleccion)
            values = item['values']
            nombre_producto, cantidad_y_precio = values[0], values[2]
            
            # Separar cantidad y precio total de la cadena "cantidad x precio = total"
            cantidad, precio_total = cantidad_y_precio.split(' = ')[-1]
            precio_total = float(precio_total.replace('€', ''))  # Convertir a float y eliminar el símbolo de euro
            
            # Actualizar el total de la consumición
            self.total_consumicion -= precio_total
            self.label_precio_total.config(text=f"Precio total: {self.total_consumicion}€")
            
            # Eliminar el producto de la lista interna de productos consumidos
            # Esto es más complejo si solo tienes el nombre, cantidad y precio total, y puede requerir repensar cómo rastreas estos productos
            for i, producto in enumerate(self.productos_consumidos):
                if producto['nombre'] == nombre_producto and producto['precio'] * producto['cantidad'] == precio_total:
                    del self.productos_consumidos[i]
                    break
            
            # Eliminar el producto seleccionado de la lista de UI
            self.lista_productos_consumidos.delete(seleccion[0])

    def finalizar_compra(self, pagada):
        if not self.socio_actual:
            messagebox.showerror("Error", "No se ha seleccionado un socio.")
            return

        trabajador_id = EstadoApp.get_usuario_logueado_id()

        with Session() as session:
            detalles_venta = [{"producto_id": p["id"], "cantidad": p["cantidad"]} for p in self.productos_consumidos]
            total_venta = sum(p["precio"] * p["cantidad"] for p in self.productos_consumidos)
            
            if pagada:
                try:
                    venta_id = procesar_venta(session, self.socio_actual.id, detalles_venta, total_venta, trabajador_id)
                    messagebox.showinfo("Compra finalizada", f"La compra ha sido registrada como pagada con éxito. ID de venta: {venta_id}")
                except Exception as e:
                    messagebox.showerror("Error al procesar la venta", str(e))
                    return
            else:
                try:
                    deuda_id = procesar_deuda(session, self.socio_actual.id, detalles_venta, total_venta, trabajador_id)
                    messagebox.showinfo("Deuda registrada", f"La compra ha sido registrada como deuda con éxito. ID de deuda: {deuda_id}")
                except Exception as e:
                    messagebox.showerror("Error al procesar la deuda", str(e))
                    return

            # Actualizar el stock de los productos vendidos
            for producto in self.productos_consumidos:
                actualizar_stock(session, producto["id"], -producto["cantidad"])

            session.commit()

        self.preparar_para_siguiente_venta()

    def preparar_para_siguiente_venta(self):
        # Limpia la UI y reinicia los atributos para la próxima venta
        self.lista_productos_consumidos.delete(*self.lista_productos_consumidos.get_children())
        self.productos_consumidos.clear()
        self.total_consumicion = 0
        self.label_precio_total.config(text="Precio total: 0€")
        self.socio_actual = None
        # Actualizar la UI según sea necesario

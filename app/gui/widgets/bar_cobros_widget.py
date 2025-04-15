# app/gui/widgets/bar_cobros_widget.py
import tkinter as tk
from tkinter import ttk, messagebox
from sqlalchemy import func
from app.database.connection import Session
from app.database.models import Deuda, DetalleVenta, Socio, Producto, Venta
from app.logic.EstadoApp import EstadoApp 
from app.gui.widgets.pago_dialog import PagoDialog

from app.logic.stock import obtener_productos, actualizar_stock
from app.logic.socios import obtener_socio_por_id, buscar_socios
from app.logic.sales import procesar_venta
from app.logic.deudas import procesar_deuda, verificar_deudas_socio

from datetime import datetime, timezone
import logging
from decimal import Decimal

logger = logging.getLogger(__name__)


class BarCobrosWidget(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.socio_actual = None
        self.productos_consumidos = []
        self.total_consumicion = 0
        self.deudas_pendientes = []
        self.create_widgets()
        self.cargar_stock_productos()

    def create_widgets(self):
        # Configuración de la zona de datos del socio
        self.frame_datos_socio = tk.Frame(self, borderwidth=2, relief=tk.GROOVE)
        self.frame_datos_socio.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)

        tk.Label(self.frame_datos_socio, text="Buscar Socio:").pack(pady=(10,0))
        
        # Frame para el buscador de socios
        self.frame_buscador = tk.Frame(self.frame_datos_socio)
        self.frame_buscador.pack(fill=tk.X, pady=5)
        
        self.entry_buscar_socio = tk.Entry(self.frame_buscador)
        self.entry_buscar_socio.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.entry_buscar_socio.bind('<KeyRelease>', self.buscar_socios)
        
        self.btn_buscar = tk.Button(self.frame_buscador, text="Buscar", command=self.buscar_socios)
        self.btn_buscar.pack(side=tk.RIGHT, padx=5)
        
        # Lista de socios encontrados
        self.frame_lista_socios = tk.Frame(self.frame_datos_socio)
        self.frame_lista_socios.pack(fill=tk.BOTH, expand=True, pady=5)
        
        self.lista_socios = ttk.Treeview(self.frame_lista_socios, columns=("ID", "Nombre", "Email"), show="headings", height=5)
        self.lista_socios.heading("ID", text="ID")
        self.lista_socios.heading("Nombre", text="Nombre")
        self.lista_socios.heading("Email", text="Email")
        self.lista_socios.column("ID", width=50)
        self.lista_socios.column("Nombre", width=150)
        self.lista_socios.column("Email", width=150)
        self.lista_socios.pack(fill=tk.BOTH, expand=True)
        self.lista_socios.bind("<Double-1>", self.seleccionar_socio)

        self.label_info_socio = tk.Label(self.frame_datos_socio, text="", wraplength=400)
        self.label_info_socio.pack(pady=(5, 0))

        # Frame para mostrar deudas pendientes
        self.frame_deudas = tk.Frame(self.frame_datos_socio, borderwidth=2, relief=tk.GROOVE)
        self.frame_deudas.pack(fill=tk.BOTH, expand=True, pady=5)
        
        tk.Label(self.frame_deudas, text="Deudas Pendientes:").pack(pady=(5,0))
        
        # Lista de deudas pendientes
        self.lista_deudas = ttk.Treeview(self.frame_deudas, columns=("ID", "Fecha", "Total", "Estado"), show="headings", height=3)
        self.lista_deudas.heading("ID", text="ID")
        self.lista_deudas.heading("Fecha", text="Fecha")
        self.lista_deudas.heading("Total", text="Total")
        self.lista_deudas.heading("Estado", text="Estado")
        self.lista_deudas.column("ID", width=50)
        self.lista_deudas.column("Fecha", width=100)
        self.lista_deudas.column("Total", width=80)
        self.lista_deudas.column("Estado", width=100)
        self.lista_deudas.pack(fill=tk.BOTH, expand=True, pady=5)
        self.lista_deudas.bind("<Double-1>", self.seleccionar_deuda)
        
        # Botón para pagar deuda seleccionada
        self.btn_pagar_deuda = tk.Button(self.frame_deudas, text="Pagar Deuda Seleccionada", command=self.pagar_deuda)
        self.btn_pagar_deuda.pack(pady=5)

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

        self.lista_productos_consumidos = ttk.Treeview(self.frame_productos_consumidos, columns=("Producto", "Cantidad", "Precio", "Total"), show="headings")
        self.lista_productos_consumidos.heading("Producto", text="Producto")
        self.lista_productos_consumidos.heading("Cantidad", text="Cantidad")
        self.lista_productos_consumidos.heading("Precio", text="Precio")
        self.lista_productos_consumidos.heading("Total", text="Total")
        self.lista_productos_consumidos.pack(fill=tk.BOTH, expand=True)
        self.lista_productos_consumidos.bind("<Double-1>", self.eliminar_producto_seleccionado)
    
        # Etiqueta para mostrar el precio total
        self.label_precio_total = tk.Label(self.frame_productos_consumidos, text="Precio total: 0€")
        self.label_precio_total.pack(pady=(10, 5))

       # Botón para finalizar compra como pagada
        self.btn_compra_pagada = tk.Button(self.frame_productos_consumidos, text="Compra Pagada", command=lambda: self.finalizar_compra(pagada=True))
        self.btn_compra_pagada.pack(pady=5)

        # Botón para finalizar compra como deuda
        self.btn_compra_deuda = tk.Button(self.frame_productos_consumidos, text="Dejar como Deuda", command=lambda: self.finalizar_compra(pagada=False))
        self.btn_compra_deuda.pack(pady=5)

    def buscar_socios(self, event=None):
        # Limpiar la lista actual
        for item in self.lista_socios.get_children():
            self.lista_socios.delete(item)
            
        # Obtener el término de búsqueda
        termino = self.entry_buscar_socio.get().strip()
        if not termino:
            return
            
        # Buscar socios
        with Session() as session:
            socios = buscar_socios(session, termino)
            
            # Mostrar los resultados
            for socio in socios:
                self.lista_socios.insert("", "end", values=(socio.id, socio.nombre, socio.email))
                
    def seleccionar_socio(self, event):
        # Obtener el socio seleccionado
        seleccion = self.lista_socios.selection()
        if not seleccion:
            return
            
        item = self.lista_socios.item(seleccion)
        socio_id = item['values'][0]
        
        # Obtener el socio completo
        session = Session()
        try:
            socio = session.query(Socio).get(socio_id)
            if socio:
                self.socio_actual = socio
                total_deudas = self.obtener_total_deudas_socio(socio_id)
                deudas_info = f"Tiene deudas pendientes por un total de {total_deudas:.2f}€." if total_deudas > 0 else "No tiene deudas pendientes."
                
                # Actualizar el texto del label con la información del socio, sus deudas y el total adeudado
                info_text = f"Socio: {socio.nombre}\nCorreo: {socio.email}\n{deudas_info}"
                self.label_info_socio.config(text=info_text)
                        
                # Cargar las deudas pendientes
                self.cargar_deudas_pendientes(socio_id)
                
                # Cargar productos disponibles
                self.cargar_stock_productos()
        finally:
            session.close()

    def cargar_deudas_pendientes(self, socio_id):
        """Carga las deudas pendientes del socio"""
        # Limpiar la lista actual
        for item in self.lista_deudas.get_children():
            self.lista_deudas.delete(item)
            
        if not socio_id:
            return
            
        # Obtener las deudas pendientes
        session = Session()
        try:
            deudas = session.query(Deuda).filter(
                Deuda.socio_id == socio_id,
                Deuda.pagada == False,
                Deuda.pagada_parcialmente == False
            ).all()
            
            for deuda in deudas:
                self.lista_deudas.insert("", "end", values=(
                    deuda.id,
                    deuda.fecha.strftime("%Y-%m-%d"),
                    f"{deuda.total:.2f}€",
                    "Pendiente"
                ))
        except Exception as e:
            print(f"Error al cargar deudas: {e}")
        finally:
            session.close()

    def obtener_total_deudas_socio(self, socio_id):
        """Obtiene el total de deudas pendientes de un socio"""
        session = Session()
        try:
            # Obtener el socio
            socio = session.query(Socio).get(socio_id)
            if not socio:
                return 0
                
            # Obtener todos los IDs de socios (principal y familiares)
            socio_ids = [socio.id]  # Incluir el socio principal
            if socio.es_principal:
                # Obtener los IDs de los miembros de la familia
                familia_ids = [m.socio_miembro_id for m in socio.miembros]
                socio_ids.extend(familia_ids)
            
            # Obtener todas las deudas no pagadas y no parcialmente pagadas
            deudas = session.query(Deuda).filter(
                Deuda.socio_id.in_(socio_ids),
                Deuda.pagada == False,
                Deuda.pagada_parcialmente == False
            ).all()
            
            total = 0
            for deuda in deudas:
                # Obtener los detalles de la venta que aún están asociados a la deuda
                detalles = session.query(DetalleVenta).filter(
                    DetalleVenta.deuda_id == deuda.id
                ).all()
                
                # Calcular el total de la deuda pendiente
                total_deuda = sum(detalle.precio * detalle.cantidad for detalle in detalles)
                total += total_deuda
                
            return total
        except Exception as e:
            print(f"Error al obtener el total de deudas: {str(e)}")
            return 0
        finally:
            session.close()

    def cargar_stock_productos(self):
        for i in self.lista_productos_stock.get_children():
            self.lista_productos_stock.delete(i)
        
        session = Session()
        try:
            productos = session.query(Producto).filter_by(activo=True).all()
            for producto in productos:
                if producto.stock_actual > 0:
                        self.lista_productos_stock.insert("", "end", values=(
                            producto.id,
                            producto.nombre,
                            f"{producto.precio:.2f}€",
                            producto.stock_actual
                        ))
        except Exception as e:
            print(f"Error al cargar productos: {str(e)}")
            messagebox.showerror("Error", f"Error al cargar productos: {str(e)}")
        finally:
            session.close()

    def añadir_producto_consumido(self, event):
        # Obtener el ítem seleccionado
        seleccion = self.lista_productos_stock.selection()
        if not seleccion:
            return  # No hacer nada si no hay selección
        item = self.lista_productos_stock.item(seleccion)
        producto_id, nombre_producto, precio_producto, stock_disponible = item['values']
        
        # Convertir precio_producto a float (eliminar el símbolo €)
        precio_producto = float(precio_producto.replace('€', ''))

        # Solicitar la cantidad a consumir
        cantidad = tk.simpledialog.askinteger("Cantidad", f"¿Cuántas unidades de {nombre_producto}? (Stock disponible: {stock_disponible})", minvalue=1, maxvalue=stock_disponible)
        if cantidad is None or cantidad > stock_disponible:  # Si el usuario cancela o solicita más del stock disponible
            messagebox.showerror("Error", "Cantidad no válida o excede el stock disponible.")
            return

        # Añadir el producto y la cantidad a la lista de productos consumidos
        self.productos_consumidos.append((producto_id, cantidad))

        # Actualizar la lista de productos consumidos en la UI
        self.actualizar_lista_productos_consumidos()

        # Actualizar el precio total y mostrarlo en la etiqueta
        self.total_consumicion += precio_producto * cantidad
        self.label_precio_total.config(text=f"Precio total: {self.total_consumicion:.2f}€")

        # Actualizar el stock en la lista de productos disponibles (solo en la UI)
        nuevo_stock = stock_disponible - cantidad
        self.lista_productos_stock.item(seleccion, values=(producto_id, nombre_producto, f"{precio_producto:.2f}€", nuevo_stock))

    def actualizar_lista_productos_consumidos(self):
        # Limpia la lista actual para evitar duplicados
        for i in self.lista_productos_consumidos.get_children():
            self.lista_productos_consumidos.delete(i)
        
        # Recorre la lista de productos consumidos para añadirlos a la UI
        session = Session()
        try:
            for producto_id, cantidad in self.productos_consumidos:
                producto = session.query(Producto).get(producto_id)
                if producto:
                    subtotal = producto.precio * cantidad
                    self.lista_productos_consumidos.insert("", "end", values=(
                        producto.nombre, 
                        cantidad, 
                        f"{producto.precio:.2f}€", 
                        f"{subtotal:.2f}€"
                    ))
        except Exception as e:
            print(f"Error al actualizar lista de productos consumidos: {str(e)}")
        finally:
            session.close()
        
    def eliminar_producto_seleccionado(self, event=None):
        """Elimina un producto de la lista de productos consumidos."""
        seleccion = self.lista_productos_consumidos.selection()
        if not seleccion:
            return
            
        item = self.lista_productos_consumidos.item(seleccion[0])
        nombre_producto = item['values'][0]
        cantidad = int(item['values'][1])
        precio_total = float(item['values'][3].replace('€', ''))
        
        # Eliminar el producto de la lista de productos consumidos
        for i, (prod_id, cant) in enumerate(self.productos_consumidos):
            if cant == cantidad:
                    del self.productos_consumidos[i]
                    break
            
        # Eliminar el producto de la lista visual
            self.lista_productos_consumidos.delete(seleccion[0])

        # Actualizar el total
        self.total_consumicion -= precio_total
        self.label_precio_total.config(text=f"Precio total: {self.total_consumicion:.2f}€")
        
        # Actualizar el stock en la lista de productos disponibles (solo visual)
        for item in self.lista_productos_stock.get_children():
            if self.lista_productos_stock.item(item)['values'][1] == nombre_producto:
                stock_actual = int(self.lista_productos_stock.item(item)['values'][3])
                self.lista_productos_stock.item(item, values=(
                    self.lista_productos_stock.item(item)['values'][0],
                    nombre_producto,
                    self.lista_productos_stock.item(item)['values'][2],
                    stock_actual + cantidad
                ))
                break

    def pagar_deuda(self, event=None):
        """Procesa el pago de una deuda seleccionada"""
        # Obtener la deuda seleccionada
        seleccion = self.lista_deudas.selection()
        if not seleccion:
            messagebox.showwarning("Advertencia", "Por favor, seleccione una deuda para pagar")
            return

        # Obtener el ID de la deuda
        deuda_id = self.lista_deudas.item(seleccion[0])['values'][0]
        
        session = Session()
        try:
            # Buscar la deuda y sus detalles
            deuda = session.query(Deuda).get(deuda_id)
            if not deuda:
                messagebox.showerror("Error", "No se encontró la deuda")
                return
                
            # Obtener el socio
            socio = session.query(Socio).get(deuda.socio_id)
            if not socio:
                messagebox.showerror("Error", "No se encontró el socio asociado a la deuda")
                return
                
            # Obtener los detalles de la deuda
            detalles = session.query(DetalleVenta).filter_by(deuda_id=deuda_id).all()
            if not detalles:
                messagebox.showerror("Error", "No se encontraron detalles para la deuda")
                return
                
            # Abrir diálogo de pago
            dialog = PagoDialog(
                parent=self,
                socio=socio,
                deuda=deuda,
                detalles_venta=detalles
            )
            
            # Mostrar el diálogo y esperar resultado
            resultado = dialog.show()
            
            # Si el pago fue exitoso
            if resultado and resultado.get("success"):
                try:
                    # Procesar el pago
                    venta = Venta(
                        socio_id=socio.id,
                        fecha=datetime.now(timezone.utc),
                        total=resultado["total"],
                        metodo_pago=resultado["metodo"],
                        trabajador_id=EstadoApp.get_usuario_logueado_id()
                    )
                    session.add(venta)
                    
                    # Agregar los detalles de la venta y actualizar el stock
                    for detalle in resultado["detalles"]:
                        detalle_venta = DetalleVenta(
                            venta=venta,
                            producto_id=detalle["producto_id"],
                            cantidad=detalle["cantidad"],
                            precio=detalle["precio"]
                        )
                        session.add(detalle_venta)
                        
                        # Actualizar el stock del producto
                        producto = session.query(Producto).get(detalle["producto_id"])
                        if producto:
                            producto.stock_actual -= detalle["cantidad"]
                    
                    # Si es un pago parcial, crear una nueva deuda con los detalles restantes
                    if resultado.get("es_pago_parcial"):
                        nueva_deuda = Deuda(
                            socio_id=socio.id,
                            fecha=datetime.now(timezone.utc),
                            total=sum(d["precio"] * d["cantidad"] for d in resultado["detalles_restantes"]),
                            trabajador_id=EstadoApp.get_usuario_logueado_id(),
                            pagada=False,
                            pagada_parcialmente=False
                        )
                        session.add(nueva_deuda)
                        
                        # Agregar los detalles restantes a la nueva deuda
                        for detalle in resultado["detalles_restantes"]:
                            detalle_deuda = DetalleVenta(
                                deuda=nueva_deuda,
                                producto_id=detalle["producto_id"],
                                cantidad=detalle["cantidad"],
                                precio=detalle["precio"]
                            )
                            session.add(detalle_deuda)
                    
                    # Marcar la deuda original como pagada
                    deuda.pagada = True
                    deuda.pagada_parcialmente = resultado.get("es_pago_parcial", False)
                    deuda.metodo_pago = resultado["metodo"]
                    
                    # Commit los cambios
                    session.commit()
                    
                    # Actualizar la interfaz
                    self.actualizar_datos()
                    self.cargar_stock_productos()
                    self.cargar_deudas_pendientes(socio.id)
                    
                    messagebox.showinfo("Éxito", "Pago procesado correctamente")
                    
                except Exception as e:
                    session.rollback()
                    messagebox.showerror("Error", f"Error al procesar el pago: {str(e)}")
                    logger.error(f"Error al procesar el pago: {str(e)}", exc_info=True)
                
        except Exception as e:
            messagebox.showerror("Error", f"Error al procesar la deuda: {str(e)}")
            logger.error(f"Error al procesar la deuda: {str(e)}", exc_info=True)
        finally:
            session.close()

    def finalizar_compra(self, pagada=True):
        """Finaliza la compra actual."""
        try:
            if not self.productos_consumidos:
                messagebox.showwarning("Advertencia", "No hay productos consumidos")
                return
                
            if not self.socio_actual:
                messagebox.showwarning("Advertencia", "Debe seleccionar un socio")
                return
                
            # Si no es pagada, agregar directamente a deudas
            if not pagada:
                # Preparar los detalles de venta
                detalles_venta = []
                total = 0
                session = Session()
                try:
                    for producto_id, cantidad in self.productos_consumidos:
                        producto = session.query(Producto).get(producto_id)
                        if producto:
                            detalles_venta.append({
                                "producto_id": producto_id,
                                "cantidad": cantidad,
                                "precio": producto.precio
                            })
                            total += producto.precio * cantidad
                    
                    # Crear la deuda
                    deuda = Deuda(
                        socio_id=self.socio_actual.id,
                        fecha=datetime.now(timezone.utc),
                        total=total,
                        trabajador_id=EstadoApp.get_usuario_logueado_id()
                    )
                    session.add(deuda)
                    
                    # Agregar los detalles de la deuda
                    for detalle in detalles_venta:
                        detalle_venta = DetalleVenta(
                            deuda=deuda,
                            producto_id=detalle["producto_id"],
                            cantidad=detalle["cantidad"],
                            precio=detalle["precio"]
                        )
                        session.add(detalle_venta)
                        
                        # Actualizar el stock del producto
                        producto = session.query(Producto).get(detalle["producto_id"])
                        if producto:
                            producto.stock_actual -= detalle["cantidad"]
                    
                    session.commit()
                    messagebox.showinfo("Éxito", "Compra agregada a deudas correctamente")
                    self.limpiar_compra()
                    self.actualizar_datos()
                    
                except Exception as e:
                    session.rollback()
                    messagebox.showerror("Error", f"Error al crear la deuda: {str(e)}")
                    logger.error(f"Error al crear la deuda: {str(e)}", exc_info=True)
                finally:
                    session.close()
                    return

            # Si es pagada, mostrar diálogo de pago
            dialog = PagoDialog(
                self,
                socio=self.socio_actual,
                detalles_venta=self.productos_consumidos
            )
            resultado = dialog.show()
            
            if resultado and resultado.get("success"):
                # Procesar la venta
                session = Session()
                try:
                    # Crear la venta
                    venta = Venta(
                        socio_id=self.socio_actual.id,
                        fecha=datetime.now(timezone.utc),
                        total=resultado["total"],
                        metodo_pago=resultado["metodo"],
                        trabajador_id=EstadoApp.get_usuario_logueado_id()
                    )
                    session.add(venta)
                    
                    # Agregar los detalles de la venta
                    for detalle in resultado["detalles"]:
                        detalle_venta = DetalleVenta(
                            venta=venta,
                            producto_id=detalle["producto_id"],
                            cantidad=detalle["cantidad"],
                            precio=detalle["precio"]
                        )
                        session.add(detalle_venta)
                        
                        # Actualizar el stock del producto
                        producto = session.query(Producto).get(detalle["producto_id"])
                        if producto:
                            producto.stock_actual -= detalle["cantidad"]
                    
                    # Si hay detalles restantes, crear una deuda
                    if resultado.get("es_pago_parcial"):
                        deuda = Deuda(
                            socio_id=self.socio_actual.id,
                            fecha=datetime.now(timezone.utc),
                            total=sum(d["precio"] * d["cantidad"] for d in resultado["detalles_restantes"]),
                            trabajador_id=EstadoApp.get_usuario_logueado_id()
                        )
                        session.add(deuda)
                        
                        # Agregar los detalles restantes a la deuda
                        for detalle in resultado["detalles_restantes"]:
                            detalle_deuda = DetalleVenta(
                                deuda=deuda,
                                producto_id=detalle["producto_id"],
                                cantidad=detalle["cantidad"],
                                precio=detalle["precio"]
                            )
                            session.add(detalle_deuda)
                            
                            # Actualizar el stock del producto
                            producto = session.query(Producto).get(detalle["producto_id"])
                            if producto:
                                producto.stock_actual -= detalle["cantidad"]

                    session.commit()
                    messagebox.showinfo("Éxito", "Venta procesada correctamente")
                    self.limpiar_compra()
                    self.actualizar_datos()
                    
                except Exception as e:
                    session.rollback()
                    messagebox.showerror("Error", f"Error al procesar la venta: {str(e)}")
                    logger.error(f"Error al procesar la venta: {str(e)}", exc_info=True)
                finally:
                    session.close()
            else:
                messagebox.showinfo("Cancelado", "Operación cancelada")
                
        except Exception as e:
            messagebox.showerror("Error", f"Error al finalizar la compra: {str(e)}")
            logger.error(f"Error al finalizar la compra: {str(e)}", exc_info=True)
            
    def limpiar_compra(self):
        """Limpia la compra actual."""
        self.productos_consumidos = []
        self.total_consumicion = 0
        self.label_precio_total.config(text="Precio total: 0€")
        self.actualizar_lista_productos_consumidos()
        self.cargar_stock_productos()

    def actualizar_datos(self):
        """Actualiza todos los datos de la interfaz"""
        # 1. Limpia la lista de productos disponibles y productos consumidos
        self.productos_consumidos = []
        self.total_consumicion = 0
        self.actualizar_lista_productos_consumidos()
        
        # 2. Recarga el stock de productos
        self.cargar_stock_productos()

        # 3. Si hay un socio seleccionado, actualiza sus datos
        if self.socio_actual:
            self.cargar_deudas_pendientes(self.socio_actual.id)
            total_deudas = self.obtener_total_deudas_socio(self.socio_actual.id)
            deudas_info = f"Tiene deudas pendientes por un total de {total_deudas:.2f}€." if total_deudas > 0 else "No tiene deudas pendientes."
            info_text = f"Socio: {self.socio_actual.nombre}\nCorreo: {self.socio_actual.email}\n{deudas_info}"
            self.label_info_socio.config(text=info_text)

    def cargar_deudas(self):
        """Carga las deudas del socio actual"""
        if not self.socio_actual:
            return
        
        # Limpiar la lista de deudas
        for widget in self.frame_deudas.winfo_children():
            widget.destroy()
        
        session = Session()
        try:
            # Obtener las deudas no pagadas del socio
            deudas = session.query(Deuda).filter_by(
                socio_id=self.socio_actual.id,
                pagada=False
            ).all()
            
            # Mostrar las deudas
            for deuda in deudas:
                frame_deuda = ttk.Frame(self.frame_deudas)
                frame_deuda.pack(fill=tk.X, pady=2)
                
                # Fecha y total
                ttk.Label(frame_deuda, text=f"{deuda.fecha}: {deuda.total:.2f}€").pack(side=tk.LEFT)
                
                # Botón para pagar
                ttk.Button(
                    frame_deuda,
                    text="Pagar",
                    command=lambda d=deuda: self.pagar_deuda(d)
                ).pack(side=tk.RIGHT)
                
        except Exception as e:
            print(f"Error al cargar las deudas: {str(e)}")
        finally:
            session.close()

    def obtener_precio_producto(self, producto_id):
        """Obtiene el precio de un producto por su ID"""
        session = Session()
        try:
            producto = session.query(Producto).get(producto_id)
            if producto:
                return producto.precio
            return 0
        finally:
            session.close()

    def seleccionar_deuda(self, event=None):
        """Abre el diálogo para pagar una deuda seleccionada"""
        if not self.socio_actual:
            messagebox.showerror("Error", "Debe seleccionar un socio primero")
            return

        # Obtener la deuda seleccionada
        seleccion = self.lista_deudas.selection()
        if not seleccion:
            messagebox.showerror("Error", "Debe seleccionar una deuda")
            return

        # Obtener el ID de la deuda
        deuda_id = self.lista_deudas.item(seleccion[0])['values'][0]

        session = Session()
        try:
            # Obtener la deuda y sus detalles
            deuda = session.query(Deuda).get(deuda_id)
            if not deuda:
                messagebox.showerror("Error", "No se encontró la deuda")
                return

            # Obtener el socio
            socio = session.query(Socio).get(deuda.socio_id)
            if not socio:
                messagebox.showerror("Error", "No se encontró el socio asociado a la deuda")
                return

            # Obtener los detalles de la deuda
            detalles = session.query(DetalleVenta).filter_by(deuda_id=deuda_id).all()
            if not detalles:
                messagebox.showerror("Error", "No se encontraron detalles para la deuda")
                return

            # Abrir diálogo de pago
            dialog = PagoDialog(
                parent=self,
                socio=socio,
                deuda=deuda,
                detalles_venta=detalles
            )
            
            # Mostrar el diálogo y esperar resultado
            resultado = dialog.show()
            
            # Si el pago fue exitoso, actualizar la interfaz
            if resultado and resultado.get("success"):
                self.actualizar_datos()
                messagebox.showinfo("Éxito", "Pago procesado correctamente")

        except Exception as e:
            messagebox.showerror("Error", f"Error al procesar la deuda: {str(e)}")
            logger.error(f"Error al procesar la deuda: {str(e)}", exc_info=True)
        finally:
            session.close()

    def actualizar_total_deudas_socio(self):
        """Actualiza el total de deudas del socio actual"""
        if not self.socio_actual:
            self.label_info_socio.config(text="Total Deuda: 0.00€")
            return
            
        session = Session()
        try:
            # Obtener el total de deudas del socio principal
            total_deuda = session.query(func.sum(Deuda.total)).filter(
                Deuda.socio_id == self.socio_actual.id,
                Deuda.pagada == False
            ).scalar() or 0
            
            # Obtener el total de deudas de los miembros de familia
            miembros_familia = session.query(Socio).filter(
                Socio.socio_principal_id == self.socio_actual.id,
                Socio.es_principal == False
            ).all()
            
            for miembro in miembros_familia:
                deuda_miembro = session.query(func.sum(Deuda.total)).filter(
                    Deuda.socio_id == miembro.id,
                    Deuda.pagada == False
                ).scalar() or 0
                total_deuda += deuda_miembro
            
            self.label_info_socio.config(text=f"Total Deuda: {total_deuda:.2f}€")
        except Exception as e:
            print(f"Error al actualizar el total de deudas: {str(e)}")
            self.label_info_socio.config(text="Total Deuda: 0.00€")
        finally:
            session.close()

    def actualizar_deudas(self):
        """Actualiza la lista de deudas"""
        # Limpiar lista actual
        for item in self.lista_deudas.get_children():
            self.lista_deudas.delete(item)
            
        if not self.socio_actual:
            return
            
        session = Session()
        try:
            # Obtener el socio principal
            socio = session.query(Socio).get(self.socio_actual.id)
            if not socio:
                return
                
            # Obtener todos los IDs de socios (principal y familiares)
            socio_ids = [socio.id]  # Incluir el socio principal
            if socio.es_principal:
                # Obtener los IDs de los miembros de la familia
                familia_ids = [m.socio_miembro_id for m in socio.miembros]
                socio_ids.extend(familia_ids)
            
            # Obtener todas las deudas pendientes o parcialmente pagadas
            deudas = session.query(Deuda).filter(
                Deuda.socio_id.in_(socio_ids),
                (Deuda.pagada == False) | (Deuda.pagada_parcialmente == True)
            ).all()
            
            # Limpiar la lista de deudas pendientes
            self.deudas_pendientes = []
            
            for deuda in deudas:
                # Obtener los detalles de la venta que aún están asociados a la deuda
                detalles = session.query(DetalleVenta).filter(
                    DetalleVenta.deuda_id == deuda.id
                ).all()
                
                # Si no hay detalles, la deuda está completamente pagada
                if not detalles:
                    continue
                
                # Calcular el total de la deuda pendiente
                total = sum(detalle.precio * detalle.cantidad for detalle in detalles)
                
                # Obtener el nombre del socio al que pertenece la deuda
                socio_deuda = session.query(Socio).get(deuda.socio_id)
                nombre_socio = socio_deuda.nombre if socio_deuda else "Socio desconocido"
                
                # Determinar si es un miembro de familia
                es_familia = socio_deuda.es_principal == False if socio_deuda else False
                tipo_socio = "Miembro de familia" if es_familia else "Socio principal"
                
                # Determinar el estado de la deuda
                estado = "Parcialmente pagada" if deuda.pagada_parcialmente else "Pendiente"
                
                # Insertar la deuda en la lista con información adicional
                self.lista_deudas.insert('', 'end', values=(
                    deuda.id,
                    f"{deuda.fecha.strftime('%d/%m/%Y')} - {nombre_socio} ({tipo_socio}) - {estado}",
                    f"{total:.2f}€"
                ))
                
                # Almacenar la información de la deuda para uso posterior
                self.deudas_pendientes.append({
                    'id': deuda.id,
                    'socio_id': deuda.socio_id,
                    'total': total,
                    'detalles': detalles
                })
                
            # Actualizar la información del socio
            total_deudas = sum(deuda['total'] for deuda in self.deudas_pendientes)
            deudas_info = f"Tiene deudas pendientes por un total de {total_deudas:.2f}€." if total_deudas > 0 else "No tiene deudas pendientes."
            info_text = f"Socio: {socio.nombre}\nCorreo: {socio.email}\n{deudas_info}"
            self.label_info_socio.config(text=info_text)
            
        except Exception as e:
            print(f"Error al actualizar deudas: {str(e)}")
            messagebox.showerror("Error", f"Error al actualizar deudas: {str(e)}")
        finally:
            session.close()

    def procesar_pago(self, deuda, socio):
        try:
            # Obtener los detalles de la deuda
            session = Session()
            try:
                detalles = session.query(DetalleVenta).filter_by(deuda_id=deuda.id).all()
                if not detalles:
                    messagebox.showerror("Error", "No se encontraron detalles para la deuda")
                    return
                
                # Abrir diálogo de pago
                dialog = PagoDialog(
                    parent=self,
                    socio=socio,
                    deuda=deuda,
                    detalles_venta=detalles
                )
                
                # Mostrar el diálogo y esperar resultado
                resultado = dialog.show()
                
                # Si el pago fue exitoso, actualizar la interfaz
                if resultado and resultado.get("success"):
                    self.actualizar_datos()
                    messagebox.showinfo("Éxito", "Pago procesado correctamente")
            finally:
                session.close()
        except Exception as e:
            messagebox.showerror("Error", f"Error al procesar el pago: {str(e)}")
            logger.error(f"Error al procesar el pago: {str(e)}", exc_info=True)

    def agregar_producto_consumido(self, producto_id, cantidad):
        """Agrega un producto a la lista de consumidos."""
        try:
            # Obtener el producto
            session = Session()
            producto = session.query(Producto).get(producto_id)
            if not producto:
                messagebox.showerror("Error", "Producto no encontrado")
                return
                
            # Verificar stock
            if producto.stock_actual < cantidad:
                messagebox.showerror("Error", "Stock insuficiente")
                return
                
            # Agregar a la lista de consumidos
            self.productos_consumidos.append((producto_id, cantidad))
            
            # Actualizar la lista visual
            self.actualizar_lista_productos_consumidos()
            
            # Actualizar el total
            self.actualizar_total_consumo()
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al agregar producto: {str(e)}")
            logger.error(f"Error al agregar producto: {str(e)}", exc_info=True)
        finally:
            session.close()

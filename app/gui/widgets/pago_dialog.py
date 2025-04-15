import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, timezone
from app.database.connection import Session
from app.database.models import Deuda, DetalleVenta, Venta, Producto
from app.logic.EstadoApp import EstadoApp
import logging

logger = logging.getLogger(__name__)

class PagoDialog(tk.Toplevel):
    def __init__(self, parent, socio=None, deuda=None, detalles_venta=None):
        super().__init__(parent)
        self.parent = parent
        self.socio = socio
        self.deuda = deuda
        self.detalles_venta = detalles_venta
        self.resultado = None
        
        # Inicializar variables
        self.total_var = tk.StringVar()
        self.recibido_var = tk.StringVar()
        self.cambio_var = tk.StringVar()
        self.metodo_var = tk.StringVar(value="efectivo")
        
        # Configurar título y tamaño
        self.title("Procesar Pago")
        self.geometry("1000x800")  # Aumentar tamaño de la ventana
        
        # Configurar cierre de ventana
        self.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # Crear widgets
        self.setup_ui()
        
        # Centrar ventana
        self.center_window()
        
        # Esperar a que la ventana esté lista
        self.update_idletasks()
        
        # Configurar ventana modal
        self.transient(parent)
        self.focus_force()
        self.grab_set()
        
    def center_window(self):
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f'{width}x{height}+{x}+{y}')
        
    def on_closing(self):
        self.resultado = None
        self.grab_release()
        self.destroy()
        
    def setup_ui(self):
        # Frame principal con scroll
        main_frame = ttk.Frame(self)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Frame para detalles con scrollbar
        detalles_frame = ttk.LabelFrame(main_frame, text="Detalles de la Venta")
        detalles_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Crear canvas y scrollbar
        canvas = tk.Canvas(detalles_frame)
        scrollbar = ttk.Scrollbar(detalles_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Instrucciones para el usuario
        ttk.Label(scrollable_frame, text="Doble clic en un producto para modificar la cantidad a pagar", 
                 font=('Helvetica', 10, 'italic')).pack(pady=5)
        
        # Treeview para detalles
        self.tree = ttk.Treeview(scrollable_frame, columns=("producto_id", "producto_nombre", "cantidad", "precio", "total", "cantidad_seleccionada"), 
                                show="headings", height=15)
        self.tree.heading("producto_id", text="ID")
        self.tree.heading("producto_nombre", text="Producto")
        self.tree.heading("cantidad", text="Cantidad Total")
        self.tree.heading("precio", text="Precio")
        self.tree.heading("total", text="Total")
        self.tree.heading("cantidad_seleccionada", text="Cantidad a Pagar")
        
        # Ajustar anchos de columnas
        self.tree.column("producto_id", width=50, minwidth=50)
        self.tree.column("producto_nombre", width=400, minwidth=200)
        self.tree.column("cantidad", width=100, minwidth=80)
        self.tree.column("precio", width=100, minwidth=80)
        self.tree.column("total", width=100, minwidth=80)
        self.tree.column("cantidad_seleccionada", width=150, minwidth=100)
        
        # Empaquetar Treeview y scrollbar
        self.tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Cargar datos
        if self.deuda:
            self.cargar_detalles_deuda()
        else:
            self.cargar_detalles_venta()
            
        # Frame para pago
        pago_frame = ttk.LabelFrame(main_frame, text="Información de Pago")
        pago_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Grid para los campos de pago
        pago_frame.columnconfigure(1, weight=1)
        
        # Total
        ttk.Label(pago_frame, text="Total:", font=('Helvetica', 12)).grid(row=0, column=0, padx=10, pady=10, sticky="e")
        self.total_entry = ttk.Entry(pago_frame, textvariable=self.total_var, state="readonly", width=30)
        self.total_entry.grid(row=0, column=1, padx=10, pady=10, sticky="w")
        
        # Recibido
        ttk.Label(pago_frame, text="Recibido:", font=('Helvetica', 12)).grid(row=1, column=0, padx=10, pady=10, sticky="e")
        self.recibido_entry = ttk.Entry(pago_frame, textvariable=self.recibido_var, width=30)
        self.recibido_entry.grid(row=1, column=1, padx=10, pady=10, sticky="w")
        self.recibido_entry.bind('<KeyRelease>', self.calcular_cambio)
        
        # Cambio
        ttk.Label(pago_frame, text="Cambio:", font=('Helvetica', 12)).grid(row=2, column=0, padx=10, pady=10, sticky="e")
        self.cambio_entry = ttk.Entry(pago_frame, textvariable=self.cambio_var, state="readonly", width=30)
        self.cambio_entry.grid(row=2, column=1, padx=10, pady=10, sticky="w")
        
        # Método de pago
        ttk.Label(pago_frame, text="Método:", font=('Helvetica', 12)).grid(row=3, column=0, padx=10, pady=10, sticky="e")
        metodo_combo = ttk.Combobox(pago_frame, textvariable=self.metodo_var, 
                                  values=["efectivo", "tarjeta", "transferencia"], width=27)
        metodo_combo.grid(row=3, column=1, padx=10, pady=10, sticky="w")
        
        # Botones
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, padx=10, pady=20)
        
        # Estilo para botones grandes
        style = ttk.Style()
        style.configure('Large.TButton', padding=10, font=('Helvetica', 12))
        
        self.boton_procesar = ttk.Button(button_frame, text="Procesar Pago", 
                                       command=self.procesar_pago, style='Large.TButton', width=25)
        self.boton_procesar.pack(side=tk.LEFT, padx=10)
        
        ttk.Button(button_frame, text="Cancelar", command=self.on_closing, 
                  style='Large.TButton', width=25).pack(side=tk.RIGHT, padx=10)
        
        # Actualizar total
        self.actualizar_total()
        
        # Bind para edición de cantidad
        self.tree.bind('<Double-1>', self.editar_cantidad)
        
    def editar_cantidad(self, event):
        item = self.tree.selection()[0]
        values = self.tree.item(item)['values']
        cantidad_total = int(values[2])
        producto_nombre = values[1]
        precio_unitario = float(values[3])
        
        # Crear diálogo para editar cantidad
        dialog = tk.Toplevel(self)
        dialog.title("Editar Cantidad a Pagar")
        dialog.geometry("500x400")
        dialog.transient(self)
        
        # Centrar el diálogo
        dialog.update_idletasks()
        width = dialog.winfo_width()
        height = dialog.winfo_height()
        x = (dialog.winfo_screenwidth() // 2) - (width // 2)
        y = (dialog.winfo_screenheight() // 2) - (height // 2)
        dialog.geometry(f'{width}x{height}+{x}+{y}')
        
        # Frame principal
        main_frame = ttk.Frame(dialog, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Información del producto
        ttk.Label(main_frame, text=producto_nombre, font=('Helvetica', 12, 'bold')).pack(pady=5)
        ttk.Label(main_frame, text=f"Precio unitario: {precio_unitario:.2f}€", font=('Helvetica', 10)).pack(pady=5)
        ttk.Label(main_frame, text=f"Cantidad total disponible: {cantidad_total}", font=('Helvetica', 10)).pack(pady=5)
        
        # Frame para entrada y slider
        entry_frame = ttk.Frame(main_frame)
        entry_frame.pack(fill=tk.X, pady=10)
        
        ttk.Label(entry_frame, text="Cantidad a pagar:", font=('Helvetica', 10)).pack()
        
        cantidad_var = tk.StringVar(value=str(cantidad_total))
        entry = ttk.Entry(entry_frame, textvariable=cantidad_var, width=10, justify='center')
        entry.pack(pady=5)
        
        # Slider
        slider = ttk.Scale(main_frame, from_=0, to=cantidad_total, orient='horizontal')
        slider.set(cantidad_total)
        slider.pack(fill=tk.X, pady=10)
        
        # Sincronizar slider y entry
        def on_slider_change(event):
            cantidad_var.set(str(int(slider.get())))
            
        def on_entry_change(event):
            try:
                valor = int(cantidad_var.get())
                if 0 <= valor <= cantidad_total:
                    slider.set(valor)
            except ValueError:
                pass
                
        slider.bind('<Motion>', on_slider_change)
        entry.bind('<KeyRelease>', on_entry_change)
        
        # Frame para botones
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=20)
        
        def aplicar():
            try:
                cantidad = int(cantidad_var.get())
                if 0 <= cantidad <= cantidad_total:
                    self.tree.set(item, "cantidad_seleccionada", cantidad)
                    self.tree.set(item, "total", f"{cantidad * precio_unitario:.2f}")
                    self.actualizar_total()
                    dialog.destroy()
                else:
                    messagebox.showerror("Error", f"La cantidad debe estar entre 0 y {cantidad_total}")
            except ValueError:
                messagebox.showerror("Error", "Por favor, introduce un número válido")
                
        ttk.Button(button_frame, text="Aplicar", command=aplicar, style='Large.TButton').pack(side=tk.LEFT, padx=5, expand=True)
        ttk.Button(button_frame, text="Cancelar", command=dialog.destroy, style='Large.TButton').pack(side=tk.RIGHT, padx=5, expand=True)
        
        # Dar foco al entry
        entry.focus_set()
        entry.select_range(0, tk.END)
        
        # Hacer la ventana modal después de que todo esté configurado
        dialog.wait_visibility()
        dialog.grab_set()
        
    def cargar_detalles_deuda(self):
        """Carga los detalles de una deuda existente"""
        # Agrupar productos por ID
        productos_agrupados = {}
        
        for detalle in self.detalles_venta:
            if detalle.producto:
                producto_id = detalle.producto_id
                
                if producto_id in productos_agrupados:
                    # Sumar cantidades para productos existentes
                    productos_agrupados[producto_id]['cantidad'] += detalle.cantidad
                else:
                    # Crear nueva entrada para el producto
                    productos_agrupados[producto_id] = {
                        'nombre': detalle.producto.nombre,
                        'cantidad': detalle.cantidad,
                        'precio': detalle.precio
                    }
        
        # Insertar productos agrupados en el treeview
        for producto_id, info in productos_agrupados.items():
            self.tree.insert("", "end", values=(
                producto_id,
                info['nombre'],
                info['cantidad'],
                f"{info['precio']:.2f}",
                f"{info['precio'] * info['cantidad']:.2f}",
                info['cantidad']  # Inicialmente, toda la cantidad está seleccionada
            ))
            
        self.actualizar_total()

    def cargar_detalles_venta(self):
        """Carga los detalles de una venta nueva"""
        session = Session()
        try:
            for producto_id, cantidad in self.detalles_venta:
                producto = session.query(Producto).get(producto_id)
                if producto:
                    self.tree.insert("", "end", values=(
                        producto.id,
                        producto.nombre,
                        cantidad,
                        f"{producto.precio:.2f}",
                        f"{producto.precio * cantidad:.2f}",
                        cantidad
                    ))
            self.actualizar_total()
        finally:
            session.close()

    def actualizar_total(self):
        """Actualiza el total basado en las cantidades seleccionadas"""
        total = 0
        for item in self.tree.get_children():
            valores = self.tree.item(item)['values']
            precio = float(valores[3])
            cantidad_seleccionada = int(valores[5])
            subtotal = precio * cantidad_seleccionada
            total += subtotal
            # Actualizar el total en la columna
            self.tree.set(item, "total", f"{subtotal:.2f}")
        self.total_var.set(f"{total:.2f}")
        # Actualizar el cambio si hay un monto recibido
        self.calcular_cambio()

    def calcular_cambio(self, event=None):
        """Calcula el cambio basado en el monto recibido"""
        try:
            total = float(self.total_var.get())
            recibido = float(self.recibido_var.get() or 0)
            cambio = recibido - total
            self.cambio_var.set(f"{cambio:.2f}")
        except ValueError:
            self.cambio_var.set("0.00")

    def procesar_pago(self):
        """Procesa el pago y cierra el diálogo"""
        try:
            # Validar que se haya ingresado un monto recibido si el método es efectivo
            if self.metodo_var.get() == "efectivo":
                try:
                    recibido = float(self.recibido_var.get() or 0)
                    total = float(self.total_var.get())
                    if recibido < total:
                        messagebox.showerror("Error", "El monto recibido es menor que el total")
                        return
                except ValueError:
                    messagebox.showerror("Error", "Por favor ingrese un monto válido")
                    return

            # Recopilar los detalles del pago
            detalles_pago = []
            detalles_restantes = []
            total_calculado = 0
            
            for item in self.tree.get_children():
                valores = self.tree.item(item)['values']
                producto_id = valores[0]
                cantidad_total = int(valores[2])
                cantidad_seleccionada = int(valores[5])
                precio = float(valores[3])
                
                if cantidad_seleccionada > 0:
                    subtotal = precio * cantidad_seleccionada
                    total_calculado += subtotal
                    detalles_pago.append({
                        'producto_id': producto_id,
                        'cantidad': cantidad_seleccionada,
                        'precio': precio,
                        'subtotal': subtotal
                    })
                
                # Si hay cantidad restante, la agregamos a detalles_restantes
                cantidad_restante = cantidad_total - cantidad_seleccionada
                if cantidad_restante > 0:
                    detalles_restantes.append({
                        'producto_id': producto_id,
                        'cantidad': cantidad_restante,
                        'precio': precio
                    })

            if not detalles_pago:
                messagebox.showerror("Error", "No hay productos seleccionados para pagar")
                return

            # Verificar que el total calculado coincida con el mostrado
            total_mostrado = float(self.total_var.get())
            if abs(total_calculado - total_mostrado) > 0.01:  # Permitir pequeña diferencia por redondeo
                messagebox.showerror("Error", "Hay una discrepancia en el total calculado")
                return

            # Procesar el pago en la base de datos
            session = Session()
            try:
                # 1. Crear una nueva venta
                venta = Venta(
                    socio_id=self.socio.id,
                    fecha=datetime.now(),
                    total=total_calculado,
                    trabajador_id=EstadoApp.get_usuario_logueado_id(),
                    metodo_pago=self.metodo_var.get(),
                    pagada=True
                )
                session.add(venta)
                session.flush()  # Para obtener el ID de la venta
                print(f"Venta creada: ID={venta.id}, Total={venta.total}")
                
                # 2. Procesar los detalles pagados
                for detalle in detalles_pago:
                    # Crear detalle de venta
                    detalle_venta = DetalleVenta(
                        venta_id=venta.id,
                        producto_id=detalle["producto_id"],
                        cantidad=detalle["cantidad"],
                        precio=detalle["precio"]
                    )
                    session.add(detalle_venta)
                    print(f"Detalle de venta creado: Producto={detalle['producto_id']}, Cantidad={detalle['cantidad']}")
                
                # 3. Si es pago de deuda y hay detalles restantes, crear nueva deuda
                if self.deuda and detalles_restantes:
                    # Calcular total de la nueva deuda
                    total_nueva_deuda = sum(d["precio"] * d["cantidad"] for d in detalles_restantes)
                    
                    # Crear nueva deuda
                    nueva_deuda = Deuda(
                        socio_id=self.socio.id,
                        fecha=datetime.now(),
                        total=total_nueva_deuda,
                        trabajador_id=EstadoApp.get_usuario_logueado_id(),
                        pagada=False,
                        pagada_parcialmente=False,
                        metodo_pago=None
                    )
                    session.add(nueva_deuda)
                    session.flush()  # Para obtener el ID de la nueva deuda
                    print(f"Nueva deuda creada: ID={nueva_deuda.id}, Total={nueva_deuda.total}")
                    
                    # Agregar los detalles restantes a la nueva deuda
                    for detalle in detalles_restantes:
                        # Obtener el detalle original de la deuda
                        detalle_original = session.query(DetalleVenta).filter_by(
                            deuda_id=self.deuda.id,
                            producto_id=detalle["producto_id"]
                        ).first()
                        
                        if detalle_original:
                            # Crear nuevo detalle con la cantidad restante
                            detalle_deuda = DetalleVenta(
                                deuda_id=nueva_deuda.id,
                                producto_id=detalle["producto_id"],
                                cantidad=detalle["cantidad"],
                                precio=detalle_original.precio  # Usar el precio original
                            )
                            session.add(detalle_deuda)
                            print(f"Detalle de deuda creado: Producto={detalle['producto_id']}, Cantidad={detalle['cantidad']}")
                    
                    # 4. Actualizar estado de la deuda original
                    deuda_original = session.query(Deuda).get(self.deuda.id)
                    if deuda_original:
                        deuda_original.pagada = False
                        deuda_original.pagada_parcialmente = True
                        deuda_original.metodo_pago = self.metodo_var.get()
                        print("Deuda original marcada como pagada parcialmente")
                elif self.deuda:
                    # 4. Si es pago de deuda y no es parcial, marcar como pagada completamente
                    deuda_original = session.query(Deuda).get(self.deuda.id)
                    if deuda_original:
                        deuda_original.pagada = True
                        deuda_original.pagada_parcialmente = False
                        deuda_original.metodo_pago = self.metodo_var.get()
                        print("Deuda original marcada como pagada completamente")
                
                # 5. Commit los cambios
                session.commit()
                print("Cambios commitados exitosamente")
                
                # Preparar el resultado
                self.resultado = {
                    'success': True,
                    'detalles': detalles_pago,
                    'detalles_restantes': detalles_restantes,
                    'metodo': self.metodo_var.get(),
                    'total': total_calculado,
                    'recibido': float(self.recibido_var.get() or 0),
                    'es_pago_parcial': len(detalles_restantes) > 0
                }

                # Cerrar el diálogo
                self.grab_release()
                self.destroy()

            except Exception as e:
                session.rollback()
                raise e
            finally:
                session.close()

        except Exception as e:
            messagebox.showerror("Error", f"Error al procesar el pago: {str(e)}")
            logger.error(f"Error al procesar el pago: {str(e)}", exc_info=True)

    def show(self):
        """Muestra el diálogo y espera hasta que se cierre"""
        self.wait_window()
        return self.resultado 
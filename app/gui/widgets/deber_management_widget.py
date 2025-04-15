import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from app.database.connection import Session
from app.database.models import Deuda, DetalleVenta, Socio, Venta, Producto
from app.gui.widgets.pago_dialog import PagoDialog
from app.logic.deudas import obtener_deudas_agrupadas
from app.logic.EstadoApp import EstadoApp
from datetime import datetime, timezone
import logging
import sqlalchemy as sa

# Configurar logging para SQLAlchemy
logging.basicConfig(level=logging.INFO)
logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)

logger = logging.getLogger(__name__)

class DeudasWidget(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.configure(bg='#f0f0f0')  # Fondo claro para el frame

        # Inicializar variables
        self.boton_pagar = None
        self.boton_ver = None
        self.boton_actualizar = None
        self.treeview = None
        self.socio_seleccionado = None
        self.tabla_deudas = None

        style = ttk.Style()
        style.configure("Treeview", font=('Helvetica', 12), rowheight=25)
        style.configure("Treeview.Heading", font=('Helvetica', 13, 'bold'))
        style.map("TButton", foreground=[('pressed', 'white'), ('active', 'white')],
          background=[('pressed', '!disabled', '#4a69bd'), ('active', '#4a69bd')])

        self.create_widgets()

    def create_widgets(self):
        # Frame para la lista de deudas
        self.frame_lista = ttk.Frame(self)
        self.frame_lista.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Etiqueta para el título
        ttk.Label(self.frame_lista, text="Lista de Deudas Pendientes", font=('Helvetica', 14, 'bold')).pack(pady=10)
        
        # Treeview para la lista de deudas
        self.treeview = ttk.Treeview(self.frame_lista, columns=("socio_id", "nombre", "total_deuda"), show="headings")
        self.treeview.heading("socio_id", text="ID Socio")
        self.treeview.heading("nombre", text="Nombre Socio")
        self.treeview.heading("total_deuda", text="Total Deuda")
        self.treeview.pack(fill=tk.BOTH, expand=True)

        # Scrollbar para el treeview
        scrollbar = ttk.Scrollbar(self.frame_lista, orient="vertical", command=self.treeview.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.treeview.configure(yscrollcommand=scrollbar.set)

        # Botones
        self.frame_botones = ttk.Frame(self)
        self.frame_botones.pack(fill=tk.X, padx=10, pady=10)
        
        self.boton_ver = ttk.Button(self.frame_botones, text="Ver Detalle", command=self.ver_detalle_deuda)
        self.boton_ver.pack(side=tk.LEFT, padx=5)
        
        self.boton_pagar = ttk.Button(self.frame_botones, text="Pagar Deuda", command=self.marcar_como_pagado, state=tk.DISABLED)
        self.boton_pagar.pack(side=tk.LEFT, padx=5)
        
        self.boton_actualizar = ttk.Button(self.frame_botones, text="Actualizar Lista", command=self.actualizar_datos)
        self.boton_actualizar.pack(side=tk.RIGHT, padx=5)
        
        # Bind para selección
        self.treeview.bind('<<TreeviewSelect>>', self.on_treeview_select)
        
        # Cargar datos iniciales
        self.actualizar_datos()

    def actualizar_datos(self):
        """Recarga la lista de deudas desde la base de datos."""
        print("\n=== ACTUALIZANDO DATOS DE DEUDAS ===")
        logger.info("Iniciando actualización de datos de deudas")
        # Limpiar la lista actual
        for item in self.treeview.get_children():
            self.treeview.delete(item)
            
        # Obtener las deudas agrupadas
        deudas_agrupadas = obtener_deudas_agrupadas()
        print(f"Deudas agrupadas obtenidas: {len(deudas_agrupadas)}")
        logger.info(f"Deudas agrupadas obtenidas: {len(deudas_agrupadas)}")
        
        # Insertar las deudas en el treeview
        for deuda in deudas_agrupadas:
            print(f"Insertando deuda: {deuda}")
            logger.debug(f"Insertando deuda: {deuda}")
            self.treeview.insert('', tk.END, values=(
                deuda['socio_id'], 
                deuda['nombre'], 
                f"{deuda['total_deuda']:.2f} €"
            ))
            
        # Deshabilitar el botón de pagar si no hay selección
        if self.boton_pagar:
            self.boton_pagar['state'] = tk.DISABLED
        print("Actualización de datos completada")
        logger.info("Actualización de datos completada")

    def ver_detalle_deuda(self, event=None):
        """Muestra el detalle de la deuda seleccionada y permite pagarla"""
        if not self.treeview.selection():
            messagebox.showwarning("Advertencia", "Por favor, seleccione una deuda para ver su detalle")
            return
            
        item_id = self.treeview.selection()[0]
        socio_id = self.treeview.item(item_id, 'values')[0]
        print(f"\n=== VER DETALLE DE DEUDA PARA SOCIO ID: {socio_id} ===")
        logger.info(f"Ver detalle de deuda para socio ID: {socio_id}")
        
        session = Session()
        try:
            # Obtener el socio
            socio = session.query(Socio).get(socio_id)
            if not socio:
                print(f"ERROR: No se encontró el socio con ID: {socio_id}")
                logger.error(f"No se encontró el socio con ID: {socio_id}")
                messagebox.showerror("Error", "No se encontró el socio")
                return
            print(f"Socio encontrado: {socio.nombre} (ID: {socio.id})")
            logger.info(f"Socio encontrado: {socio.nombre} (ID: {socio.id})")
                
            # Obtener las deudas no pagadas del socio
            deudas = session.query(Deuda).filter(
                Deuda.socio_id == socio_id,
                Deuda.pagada == False
            ).all()
            print(f"Deudas no pagadas encontradas: {len(deudas)}")
            logger.info(f"Deudas no pagadas encontradas: {len(deudas)}")
            
            if not deudas:
                print(f"No hay deudas pendientes para el socio {socio.nombre}")
                logger.info(f"No hay deudas pendientes para el socio {socio.nombre}")
                messagebox.showinfo("Info", "El socio no tiene deudas pendientes")
                return
                
            # Obtener los detalles de la primera deuda
            deuda = deudas[0]
            detalles = session.query(DetalleVenta).filter_by(deuda_id=deuda.id).all()
            print(f"Detalles de deuda encontrados: {len(detalles)}")
            logger.info(f"Detalles de deuda encontrados: {len(detalles)}")
            
            if not detalles:
                print(f"ERROR: No se encontraron detalles para la deuda ID: {deuda.id}")
                logger.error(f"No se encontraron detalles para la deuda ID: {deuda.id}")
                messagebox.showerror("Error", "No se encontraron detalles para la deuda")
                return
                
            # Abrir diálogo de pago
            print("Abriendo diálogo de pago")
            logger.info("Abriendo diálogo de pago")
            dialog = PagoDialog(
                parent=self,
                socio=socio,
                deuda=deuda,
                detalles_venta=detalles
            )
            
            # Mostrar el diálogo y esperar resultado
            resultado = dialog.show()
            print(f"Resultado del diálogo de pago: {resultado}")
            logger.info(f"Resultado del diálogo de pago: {resultado}")
            
            # Si el pago fue exitoso, actualizar la interfaz
            if resultado and resultado.get("success"):
                print("Procesando pago exitoso")
                logger.info("Procesando pago exitoso")
                # Procesar el pago en la base de datos
                self.procesar_pago_en_db(socio_id, deuda.id, resultado)
                # Actualizar la lista de deudas
                self.actualizar_datos()
                messagebox.showinfo("Éxito", "Pago procesado correctamente")
                
        except Exception as e:
            print(f"ERROR al procesar la deuda: {str(e)}")
            logger.error(f"Error al procesar la deuda: {str(e)}", exc_info=True)
            messagebox.showerror("Error", f"Error al procesar la deuda: {str(e)}")
        finally:
            session.close()

    def procesar_pago_en_db(self, socio_id, deuda_id, resultado):
        """Procesa el pago en la base de datos"""
        print(f"\n=== PROCESANDO PAGO EN DB PARA SOCIO ID: {socio_id}, DEUDA ID: {deuda_id} ===")
        logger.info(f"Procesando pago en DB para socio ID: {socio_id}, deuda ID: {deuda_id}")
        
        session = Session()
        try:
            # 1. Obtener la deuda y sus detalles actuales
            deuda = session.query(Deuda).get(deuda_id)
            detalles_actuales = session.query(DetalleVenta).filter_by(deuda_id=deuda_id).all()
            
            if not deuda or not detalles_actuales:
                raise Exception("No se encontró la deuda o sus detalles")
            
            print(f"Deuda encontrada: ID={deuda.id}, Total={deuda.total}")
            print(f"Detalles actuales: {len(detalles_actuales)}")
            
            # 2. Crear una nueva venta
            venta = Venta(
                socio_id=socio_id,
                fecha=datetime.now(),
                total=resultado["total"],
                trabajador_id=EstadoApp.get_usuario_logueado_id(),
                metodo_pago=resultado["metodo"],
                pagada=True
            )
            session.add(venta)
            session.flush()  # Para obtener el ID de la venta
            print(f"Venta creada: ID={venta.id}, Total={venta.total}")
            
            # 3. Procesar los detalles pagados
            for detalle in resultado["detalles"]:
                # Crear detalle de venta
                detalle_venta = DetalleVenta(
                    venta_id=venta.id,
                    producto_id=detalle["producto_id"],
                    cantidad=detalle["cantidad"],
                    precio=detalle["precio"]
                )
                session.add(detalle_venta)
                print(f"Detalle de venta creado: Producto={detalle['producto_id']}, Cantidad={detalle['cantidad']}")
            
            # 4. Si es pago parcial, crear nueva deuda con los detalles restantes
            if resultado["es_pago_parcial"]:
                # Calcular total de la nueva deuda
                total_nueva_deuda = sum(d["precio"] * d["cantidad"] for d in resultado["detalles_restantes"])
                
                # Crear nueva deuda
                nueva_deuda = Deuda(
                    socio_id=socio_id,
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
                for detalle in resultado["detalles_restantes"]:
                    detalle_deuda = DetalleVenta(
                        deuda_id=nueva_deuda.id,
                        producto_id=detalle["producto_id"],
                        cantidad=detalle["cantidad"],
                        precio=detalle["precio"]
                    )
                    session.add(detalle_deuda)
                    print(f"Detalle de deuda creado: Producto={detalle['producto_id']}, Cantidad={detalle['cantidad']}")
                
                # 5. Actualizar estado de la deuda original
                deuda.pagada = False
                deuda.pagada_parcialmente = True
                deuda.metodo_pago = resultado["metodo"]
                print("Deuda original marcada como pagada parcialmente")
            else:
                # 5. Si no es parcial, marcar como pagada completamente
                deuda.pagada = True
                deuda.pagada_parcialmente = False
                deuda.metodo_pago = resultado["metodo"]
                print("Deuda original marcada como pagada completamente")
            
            # 6. Commit los cambios
            session.commit()
            print("Cambios commitados exitosamente")
            logger.info("Cambios commitados exitosamente")
            
        except Exception as e:
            print(f"ERROR al procesar el pago en la base de datos: {str(e)}")
            logger.error(f"Error al procesar el pago en la base de datos: {str(e)}", exc_info=True)
            session.rollback()
            raise Exception(f"Error al procesar el pago en la base de datos: {str(e)}")
        finally:
            session.close()

    def on_treeview_select(self, event):
        """Habilita el botón de pagar cuando hay una selección."""
        if self.boton_pagar:
            self.boton_pagar['state'] = tk.NORMAL if self.treeview.selection() else tk.DISABLED

    def marcar_como_pagado(self):
        """Procesa el pago de la deuda seleccionada"""
        if not self.treeview.selection():
            messagebox.showwarning("Advertencia", "Por favor, seleccione una deuda para pagar")
            return
            
        item_id = self.treeview.selection()[0]
        socio_id = int(self.treeview.item(item_id, 'values')[0])
        print(f"\n=== MARCANDO COMO PAGADA DEUDA PARA SOCIO ID: {socio_id} ===")
        logger.info(f"Marcando como pagada deuda para socio ID: {socio_id}")
        
        session = Session()
        try:
            # Obtener el socio
            socio = session.query(Socio).get(socio_id)
            if not socio:
                print(f"ERROR: No se encontró el socio con ID: {socio_id}")
                logger.error(f"No se encontró el socio con ID: {socio_id}")
                messagebox.showerror("Error", "No se encontró el socio")
                return
            print(f"Socio encontrado: {socio.nombre}")
            logger.info(f"Socio encontrado: {socio.nombre}")
                
            # Obtener las deudas no pagadas del socio
            deudas = session.query(Deuda).filter(
                Deuda.socio_id == socio_id,
                Deuda.pagada == False
            ).all()
            print(f"Deudas no pagadas encontradas: {len(deudas)}")
            logger.info(f"Deudas no pagadas encontradas: {len(deudas)}")
            
            if not deudas:
                print(f"No hay deudas pendientes para el socio {socio.nombre}")
                logger.info(f"No hay deudas pendientes para el socio {socio.nombre}")
                messagebox.showinfo("Info", "El socio no tiene deudas pendientes")
                return
                
            # Obtener los detalles de la primera deuda
            deuda = deudas[0]
            detalles = session.query(DetalleVenta).filter_by(deuda_id=deuda.id).all()
            print(f"Detalles de deuda encontrados: {len(detalles)}")
            logger.info(f"Detalles de deuda encontrados: {len(detalles)}")
            
            if not detalles:
                print(f"ERROR: No se encontraron detalles para la deuda ID: {deuda.id}")
                logger.error(f"No se encontraron detalles para la deuda ID: {deuda.id}")
                messagebox.showerror("Error", "No se encontraron detalles para la deuda")
                return
                
            # Abrir diálogo de pago
            print("Abriendo diálogo de pago")
            logger.info("Abriendo diálogo de pago")
            dialog = PagoDialog(
                parent=self,
                socio=socio,
                deuda=deuda,
                detalles_venta=detalles
            )
            
            # Mostrar el diálogo y esperar resultado
            resultado = dialog.show()
            print(f"Resultado del diálogo de pago: {resultado}")
            logger.info(f"Resultado del diálogo de pago: {resultado}")
            
            # Si el pago fue exitoso, actualizar la interfaz
            if resultado and resultado.get("success"):
                print("Procesando pago exitoso")
                logger.info("Procesando pago exitoso")
                try:
                    # Procesar el pago en la base de datos
                    self.procesar_pago_en_db(socio_id, deuda.id, resultado)
                    # Actualizar la lista de deudas
                    self.actualizar_datos()
                    messagebox.showinfo("Éxito", "Pago procesado correctamente")
                except Exception as e:
                    print(f"ERROR al procesar el pago: {str(e)}")
                    logger.error(f"Error al procesar el pago: {str(e)}", exc_info=True)
                    messagebox.showerror("Error", f"Error al procesar el pago: {str(e)}")
                    raise
                
        except Exception as e:
            print(f"ERROR al procesar la deuda: {str(e)}")
            logger.error(f"Error al procesar la deuda: {str(e)}", exc_info=True)
            messagebox.showerror("Error", f"Error al procesar la deuda: {str(e)}")
            session.rollback()
        finally:
            session.close()

    def cargar_deudas(self):
        """Carga las deudas del socio seleccionado"""
        if not self.socio_seleccionado:
            return
            
        session = Session()
        try:
            # Obtener solo deudas pendientes (no pagadas y no pagadas parcialmente)
            deudas = session.query(Deuda).filter(
                Deuda.socio_id == self.socio_seleccionado.id,
                Deuda.pagada == False,
                Deuda.pagada_parcialmente == False
            ).all()
            
            # Limpiar tabla
            for item in self.tabla_deudas.get_children():
                self.tabla_deudas.delete(item)
                
            # Insertar deudas
            for deuda in deudas:
                self.tabla_deudas.insert("", "end", values=(
                    deuda.id,
                    deuda.fecha.strftime("%d/%m/%Y"),
                    f"{deuda.total:.2f}€",
                    "Pendiente"
                ))
                
        except Exception as e:
            messagebox.showerror("Error", f"Error al cargar deudas: {str(e)}")
            logger.error(f"Error al cargar deudas: {str(e)}", exc_info=True)
        finally:
            session.close()


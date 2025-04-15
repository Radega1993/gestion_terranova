# Ventana principal de la aplicación
import tkinter as tk
from tkinter import messagebox, ttk, filedialog
import logging
import shutil
import os
import traceback
from datetime import datetime

# Configuración del logging
log_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'logs')
os.makedirs(log_dir, exist_ok=True)
log_file = os.path.join(log_dir, f'app_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log')

# Configurar el logger
logger = logging.getLogger('GestionTerranova')
logger.setLevel(logging.DEBUG)

# Handler para archivo
file_handler = logging.FileHandler(log_file)
file_handler.setLevel(logging.DEBUG)
file_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
file_handler.setFormatter(file_formatter)
logger.addHandler(file_handler)

# Handler para consola
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
console_formatter = logging.Formatter('%(levelname)s: %(message)s')
console_handler.setFormatter(console_formatter)
logger.addHandler(console_handler)

# Importaciones de los widgets que necesitas
from app.gui.widgets.deber_management_widget import DeudasWidget
from app.gui.widgets.recaudaciones_management import RecaudacionesManagementWidget
from app.gui.widgets.servicios_management import ServicioManagementWidget
from app.gui.widgets.user_login_widget import UserLoginWidget
from app.gui.widgets.user_management_widget import UserManagementWidget
from app.gui.widgets.product_management_widget import ProductManagementWidget
from app.gui.widgets.socio_management_widget import SocioManagementWidget
from app.gui.widgets.bar_cobros_widget import BarCobrosWidget
from app.gui.widgets.reservas_widget import ReservasWidget
from app.database.database import DATABASE_PATH

class MainWindow(tk.Tk):
    def __init__(self):
        super().__init__()
        logger.info("Inicializando MainWindow")
        
        self.title("Gestión Terranova")
        root = tk.Tk()
        width = root.winfo_screenwidth()
        height = root.winfo_screenheight()
        root.destroy()
        self.geometry(f"{width}x{height}")
        logger.debug(f"Tamaño de ventana configurado: {width}x{height}")

        self.current_user = None
        
        # Inicializa un notebook de Tkinter que funcionará como nuestro contenedor de pestañas
        self.tab_control = ttk.Notebook(self)
        self.tab_control.pack(expand=1, fill="both")
        self.tab_control.pack_forget()  # Ocultar hasta el login exitoso
        logger.debug("Control de pestañas inicializado")

        # Crea los widgets/tab para cada sección de la aplicación
        self.create_login_widget()
        logger.info("MainWindow inicializada correctamente")

    def create_login_widget(self):
        logger.debug("Creando widget de login")
        # Solo inicializa y muestra el widget de login
        self.user_login_tab = tk.Frame(self)
        self.user_login_widget = UserLoginWidget(self.user_login_tab, self.login_success)
        self.user_login_widget.pack(expand=True, fill='both')
        self.user_login_tab.pack(expand=True, fill='both')
        logger.debug("Widget de login creado y mostrado")

    def login_success(self, user):
        logger.info(f"Login exitoso para usuario: {user.nombre}")
        # Muestra el resto de la aplicación después del login exitoso
        self.current_user = user
        messagebox.showinfo("Bienvenido", f"Bienvenido {user.nombre}")
        self.user_login_tab.destroy() 

        # Muestra el control de pestañas y añade el resto de pestañas
        logger.debug("Mostrando control de pestañas")
        self.tab_control.pack(expand=1, fill="both")
        self.add_rest_of_the_tabs() 
        self.create_logout_option()
        logger.info("Todas las pestañas añadidas")
    
    def add_rest_of_the_tabs(self):
        logger.info("Añadiendo pestañas a la aplicación")
        try:
            # Pestaña de gestión de usuarios
            logger.debug("Creando pestaña de gestión de usuarios")
            self.user_management_tab = tk.Frame(self.tab_control)
            self.tab_control.add(self.user_management_tab, text="Gestión de Clientes")
            self.user_management_widget = UserManagementWidget(self.user_management_tab)
            self.user_management_widget.pack(expand=True, fill='both')

            # Pestaña de gestión de Socios
            logger.debug("Creando pestaña de gestión de socios")
            self.socio_manager_tab = tk.Frame(self.tab_control)
            self.tab_control.add(self.socio_manager_tab, text="Gestión de Socios")
            self.socio_management_widget = SocioManagementWidget(self.socio_manager_tab)
            self.socio_management_widget.pack(expand=True, fill='both')

            # Pestaña de cobros en el bar
            logger.debug("Creando pestaña de bar")
            self.bar_cobros_tab = tk.Frame(self.tab_control)
            self.tab_control.add(self.bar_cobros_tab, text="Bar")
            self.bar_cobros_widget = BarCobrosWidget(self.bar_cobros_tab)
            self.bar_cobros_widget.pack(expand=True, fill='both')

            # Pestaña de deber
            logger.debug("Creando pestaña de deber")
            self.deber_tab = tk.Frame(self.tab_control)
            self.tab_control.add(self.deber_tab, text="Deber")
            self.deber_widget = DeudasWidget(self.deber_tab)
            self.deber_widget.pack(expand=True, fill='both')

            # Pestaña de gestión de productos
            logger.debug("Creando pestaña de gestión de productos")
            self.product_management_tab = tk.Frame(self.tab_control)
            self.tab_control.add(self.product_management_tab, text="Gestión de Productos")
            self.product_management_widget = ProductManagementWidget(self.product_management_tab)
            self.product_management_widget.pack(expand=True, fill='both')
            
            # Pestaña de gestión de reservas
            logger.debug("Creando pestaña de gestión de reservas")
            try:
                self.reservas_management_tab = tk.Frame(self.tab_control)
                self.tab_control.add(self.reservas_management_tab, text="Gestión de Reservas")
                self.reservas_management_widget = ReservasWidget(self.reservas_management_tab)
                self.reservas_management_widget.pack(expand=True, fill='both')
                logger.debug("Pestaña de reservas creada correctamente")
            except Exception as e:
                logger.error(f"Error al crear pestaña de reservas: {str(e)}", exc_info=True)
                messagebox.showerror("Error", f"Error al cargar la pestaña de reservas: {str(e)}")

            # Pestaña de gestión de servicios
            logger.debug("Creando pestaña de gestión de servicios")
            try:
                self.servicios_management_tab = tk.Frame(self.tab_control)
                self.tab_control.add(self.servicios_management_tab, text="Gestión de Servicios")
                self.servicios_management_widget = ServicioManagementWidget(self.servicios_management_tab)
                self.servicios_management_widget.pack(expand=True, fill='both')
                logger.debug("Pestaña de servicios creada correctamente")
            except Exception as e:
                logger.error(f"Error al crear pestaña de servicios: {str(e)}", exc_info=True)
                messagebox.showerror("Error", f"Error al cargar la pestaña de servicios: {str(e)}")
            
            # Pestaña de recaudaciones
            logger.debug("Creando pestaña de recaudaciones")
            try:
                self.recaudaciones_management_tab = tk.Frame(self.tab_control)
                self.tab_control.add(self.recaudaciones_management_tab, text="Recaudaciones")
                self.recaudaciones_management_widget = RecaudacionesManagementWidget(self.recaudaciones_management_tab)
                self.recaudaciones_management_widget.pack(expand=True, fill='both')
                logger.debug("Pestaña de recaudaciones creada correctamente")
            except Exception as e:
                logger.error(f"Error al crear pestaña de recaudaciones: {str(e)}", exc_info=True)
                messagebox.showerror("Error", f"Error al cargar la pestaña de recaudaciones: {str(e)}")

            self.tab_control.bind("<<NotebookTabChanged>>", self.on_tab_change)
            logger.info("Todas las pestañas creadas correctamente")
        except Exception as e:
            logger.error(f"Error al crear las pestañas: {str(e)}", exc_info=True)
            messagebox.showerror("Error", f"Error al crear las pestañas: {str(e)}")

    def create_logout_option(self):
        logger.info("Creando pestaña de ajustes")
        try:
            # Agregar una pestaña para ajustes y cerrar sesión
            settings_tab = tk.Frame(self.tab_control)
            
            # Frame para la gestión de base de datos
            db_frame = ttk.LabelFrame(settings_tab, text="Gestión de Base de Datos")
            db_frame.pack(fill=tk.X, padx=5, pady=5)

            export_button = ttk.Button(db_frame, text="Exportar Base de Datos", command=self.export_database)
            export_button.pack(side=tk.LEFT, padx=5, pady=5)

            import_button = ttk.Button(db_frame, text="Importar Base de Datos", command=self.import_database)
            import_button.pack(side=tk.LEFT, padx=5, pady=5)

            # Frame para cerrar sesión
            logout_frame = ttk.LabelFrame(settings_tab, text="Sesión")
            logout_frame.pack(fill=tk.X, padx=5, pady=5)
            
            logout_button = ttk.Button(logout_frame, text="Cerrar sesión", command=self.logout)
            logout_button.pack(pady=10)

            self.tab_control.add(settings_tab, text="Ajustes")
            logger.info("Pestaña de ajustes creada correctamente")
        except Exception as e:
            logger.error(f"Error al crear la pestaña de ajustes: {str(e)}", exc_info=True)
            messagebox.showerror("Error", f"Error al crear la pestaña de ajustes: {str(e)}")

    def export_database(self):
        """Exporta la base de datos a un archivo .db"""
        logger.info("Iniciando exportación de base de datos")
        try:
            # Preguntar al usuario dónde guardar el archivo
            file_path = filedialog.asksaveasfilename(
                defaultextension=".db",
                filetypes=[("SQLite Database", "*.db")],
                initialfile="gestion_terranova_backup.db"
            )
            
            if file_path:
                logger.debug(f"Ruta de exportación seleccionada: {file_path}")
                # Copiar el archivo de la base de datos
                shutil.copy2(DATABASE_PATH, file_path)
                logger.info("Base de datos exportada correctamente")
                messagebox.showinfo("Éxito", "Base de datos exportada correctamente")
        except Exception as e:
            logger.error(f"Error al exportar la base de datos: {str(e)}", exc_info=True)
            messagebox.showerror("Error", f"Error al exportar la base de datos: {str(e)}")

    def import_database(self):
        """Importa una base de datos desde un archivo .db"""
        logger.info("Iniciando importación de base de datos")
        try:
            # Preguntar al usuario qué archivo importar
            file_path = filedialog.askopenfilename(
                filetypes=[("SQLite Database", "*.db")],
                title="Seleccionar base de datos a importar"
            )
            
            if file_path:
                logger.debug(f"Ruta de importación seleccionada: {file_path}")
                # Confirmar con el usuario
                if messagebox.askyesno("Confirmar", 
                    "La importación de una base de datos puede sobrescribir datos existentes. ¿Desea continuar?"):
                    
                    # Hacer una copia de seguridad de la base de datos actual
                    backup_path = DATABASE_PATH + ".backup"
                    logger.debug(f"Creando copia de seguridad en: {backup_path}")
                    shutil.copy2(DATABASE_PATH, backup_path)
                    
                    try:
                        # Copiar la nueva base de datos
                        logger.debug(f"Copiando nueva base de datos desde: {file_path}")
                        shutil.copy2(file_path, DATABASE_PATH)
                        logger.info("Base de datos importada correctamente")
                        messagebox.showinfo("Éxito", "Base de datos importada correctamente")
                    except Exception as e:
                        # Si hay error, restaurar la copia de seguridad
                        logger.error(f"Error durante la importación: {str(e)}", exc_info=True)
                        logger.debug("Restaurando copia de seguridad")
                        shutil.copy2(backup_path, DATABASE_PATH)
                        raise e
                    finally:
                        # Eliminar la copia de seguridad
                        if os.path.exists(backup_path):
                            logger.debug("Eliminando copia de seguridad")
                            os.remove(backup_path)
        except Exception as e:
            logger.error(f"Error al importar la base de datos: {str(e)}", exc_info=True)
            messagebox.showerror("Error", f"Error al importar la base de datos: {str(e)}")
    
    def logout(self):
        logger.info("Cerrando sesión")
        # Manejar el cierre de sesión
        self.tab_control.pack_forget()
        self.current_user = None
        self.create_login_widget()
        logger.info("Sesión cerrada correctamente")
    
    def construir_widget_en_tab(self, tab_frame, widget_class):
        logger.debug(f"Construyendo widget en tab: {widget_class.__name__}")
        try:
            for widget in tab_frame.winfo_children():
                widget.destroy()
            widget = widget_class(tab_frame)
            widget.pack(expand=True, fill='both')
            logger.debug(f"Widget {widget_class.__name__} construido correctamente")
            return widget
        except Exception as e:
            logger.error(f"Error al construir widget {widget_class.__name__}: {str(e)}", exc_info=True)
            messagebox.showerror("Error", f"Error al cargar la pestaña: {str(e)}")
            return None
    
    def on_tab_change(self, event):
        selected_tab = event.widget.select()
        tab_frame = self.tab_control.nametowidget(selected_tab)
        logger.debug(f"Cambiando a pestaña: {self.tab_control.tab(selected_tab, 'text')}")

        try:
            # Gestion de Usuarios
            if tab_frame == self.user_management_tab:
                self.user_management_widget = self.construir_widget_en_tab(tab_frame, UserManagementWidget)
            # Gestion de Socios
            elif tab_frame == self.socio_manager_tab:
                self.socio_management_widget = self.construir_widget_en_tab(tab_frame, SocioManagementWidget)
            # Cobros en el Bar
            elif tab_frame == self.bar_cobros_tab:
                self.bar_cobros_widget = self.construir_widget_en_tab(tab_frame, BarCobrosWidget)
            # Gestión de Deudas
            elif tab_frame == self.deber_tab:
                self.deber_widget = self.construir_widget_en_tab(tab_frame, DeudasWidget)
            # Gestión de Productos
            elif tab_frame == self.product_management_tab:
                self.product_management_widget = self.construir_widget_en_tab(tab_frame, ProductManagementWidget)
            # Gestión de Reservas
            elif tab_frame == self.reservas_management_tab:
                self.reservas_management_widget = self.construir_widget_en_tab(tab_frame, ReservasWidget)
            # Gestión de Servicios
            elif tab_frame == self.servicios_management_tab:
                self.servicios_management_widget = self.construir_widget_en_tab(tab_frame, ServicioManagementWidget)
            # Gestión de Recaudaciones
            elif tab_frame == self.recaudaciones_management_tab:
                self.recaudaciones_management_widget = self.construir_widget_en_tab(tab_frame, RecaudacionesManagementWidget)
        except Exception as e:
            logger.error(f"Error al cambiar de pestaña: {str(e)}", exc_info=True)
            messagebox.showerror("Error", f"Error al cambiar de pestaña: {str(e)}")

if __name__ == "__main__":
    try:
        logger.info("Iniciando aplicación")
        app = MainWindow()
        app.mainloop()
    except Exception as e:
        logger.critical(f"Error crítico en la aplicación: {str(e)}", exc_info=True)
        messagebox.showerror("Error Crítico", f"Ha ocurrido un error crítico: {str(e)}\nRevisa el archivo de log para más detalles.")

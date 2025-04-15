# Ventana principal de la aplicación
import tkinter as tk
from tkinter import messagebox, ttk, filedialog
import logging
import shutil
import os

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

class MainWindow(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Gestión Terranova")
        root = tk.Tk()
        width = root.winfo_screenwidth()
        height = root.winfo_screenheight()
        root.destroy()
        self.geometry(f"{width}x{height}")

        self.current_user = None
        
        # Inicializa un notebook de Tkinter que funcionará como nuestro contenedor de pestañas
        self.tab_control = ttk.Notebook(self)
        self.tab_control.pack(expand=1, fill="both")
        self.tab_control.pack_forget()  # Ocultar hasta el login exitoso

        # Crea los widgets/tab para cada sección de la aplicación
        self.create_login_widget()

    def create_login_widget(self):
        # Solo inicializa y muestra el widget de login
        self.user_login_tab = tk.Frame(self)
        self.user_login_widget = UserLoginWidget(self.user_login_tab, self.login_success)
        self.user_login_widget.pack(expand=True, fill='both')
        self.user_login_tab.pack(expand=True, fill='both')

    def login_success(self, user):
        # Muestra el resto de la aplicación después del login exitoso
        self.current_user = user
        messagebox.showinfo("Bienvenido", f"Bienvenido {user.nombre}")
        self.user_login_tab.destroy() 

        # Muestra el control de pestañas y añade el resto de pestañas
        self.tab_control.pack(expand=1, fill="both")
        self.add_rest_of_the_tabs() 
        self.create_logout_option()
    
    def add_rest_of_the_tabs(self):
        # Pestaña de gestión de usuarios
        self.user_management_tab = tk.Frame(self.tab_control)
        self.tab_control.add(self.user_management_tab, text="Gestión de Clientes")
        self.user_management_widget = UserManagementWidget(self.user_management_tab)
        self.user_management_widget.pack(expand=True, fill='both')

        # Pestaña de gestión de Socios
        self.socio_manager_tab = tk.Frame(self.tab_control)
        self.tab_control.add(self.socio_manager_tab, text="Gestión de Socios")
        self.user_management_widget = SocioManagementWidget(self.socio_manager_tab)
        self.user_management_widget.pack(expand=True, fill='both')

        # Pestaña de cobros en el bar
        self.bar_cobros_tab = tk.Frame(self.tab_control)
        self.tab_control.add(self.bar_cobros_tab, text="Bar")
        self.bar_cobros_widget = BarCobrosWidget(self.bar_cobros_tab)
        self.bar_cobros_widget.pack(expand=True, fill='both')

        # Pestaña de deber
        self.deber_tab = tk.Frame(self.tab_control)
        self.tab_control.add(self.deber_tab, text="Deber")
        self.deber_widget = DeudasWidget(self.deber_tab)
        self.deber_widget.pack(expand=True, fill='both')

        # Pestaña de gestión de productos
        self.product_management_tab = tk.Frame(self.tab_control)
        self.tab_control.add(self.product_management_tab, text="Gestión de Productos")
        self.product_management_widget = ProductManagementWidget(self.product_management_tab)
        self.product_management_widget.pack(expand=True, fill='both')
        
        # Pestaña de gestión de reseras
        self.reservas_management_tab = tk.Frame(self.tab_control)
        self.tab_control.add(self.reservas_management_tab, text="Gestión de Reservas")
        self.reservas_management_widget = ReservasWidget(self.reservas_management_tab)
        self.reservas_management_widget.pack(expand=True, fill='both')

        # Pestaña de gestión de servicios
        self.servicios_management_tab = tk.Frame(self.tab_control)
        self.tab_control.add(self.servicios_management_tab, text="Gestión de Servicios")
        self.servicios_management_widget = ServicioManagementWidget(self.servicios_management_tab)
        self.servicios_management_widget.pack(expand=True, fill='both')
        
        # Pestaña de gestión de servicios
        self.recaudaciones_management_tab = tk.Frame(self.tab_control)
        self.tab_control.add(self.recaudaciones_management_tab, text="Recaudaciones")
        self.recaudaciones_management_widget = RecaudacionesManagementWidget(self.recaudaciones_management_tab)
        self.recaudaciones_management_widget.pack(expand=True, fill='both')

        self.tab_control.bind("<<NotebookTabChanged>>", self.on_tab_change)
        self.tab_control.add(self.user_management_tab, text="Gestión de Clientes")
        self.tab_control.add(self.socio_manager_tab, text="Gestión de Socios")
        self.tab_control.add(self.bar_cobros_tab, text="Bar")
        self.tab_control.add(self.deber_tab, text="Deber")
        self.tab_control.add(self.product_management_tab, text="Gestión de Productos")
        self.tab_control.add(self.reservas_management_tab, text="Gestión de Reservas")
        self.tab_control.add(self.servicios_management_tab, text="Gestión de Servicios")
        self.tab_control.add(self.recaudaciones_management_tab, text="Recaudaciones")


    def create_logout_option(self):
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

    def export_database(self):
        """Exporta la base de datos a un archivo .db"""
        try:
            # Preguntar al usuario dónde guardar el archivo
            file_path = filedialog.asksaveasfilename(
                defaultextension=".db",
                filetypes=[("SQLite Database", "*.db")],
                initialfile="gestion_terranova_backup.db"
            )
            
            if file_path:
                # Copiar el archivo de la base de datos
                shutil.copy2(DATABASE_PATH, file_path)
                messagebox.showinfo("Éxito", "Base de datos exportada correctamente")
        except Exception as e:
            messagebox.showerror("Error", f"Error al exportar la base de datos: {str(e)}")

    def import_database(self):
        """Importa una base de datos desde un archivo .db"""
        try:
            # Preguntar al usuario qué archivo importar
            file_path = filedialog.askopenfilename(
                filetypes=[("SQLite Database", "*.db")],
                title="Seleccionar base de datos a importar"
            )
            
            if file_path:
                # Confirmar con el usuario
                if messagebox.askyesno("Confirmar", 
                    "La importación de una base de datos puede sobrescribir datos existentes. ¿Desea continuar?"):
                    
                    # Hacer una copia de seguridad de la base de datos actual
                    backup_path = DATABASE_PATH + ".backup"
                    shutil.copy2(DATABASE_PATH, backup_path)
                    
                    try:
                        # Copiar la nueva base de datos
                        shutil.copy2(file_path, DATABASE_PATH)
                        messagebox.showinfo("Éxito", "Base de datos importada correctamente")
                    except Exception as e:
                        # Si hay error, restaurar la copia de seguridad
                        shutil.copy2(backup_path, DATABASE_PATH)
                        raise e
                    finally:
                        # Eliminar la copia de seguridad
                        if os.path.exists(backup_path):
                            os.remove(backup_path)
        except Exception as e:
            messagebox.showerror("Error", f"Error al importar la base de datos: {str(e)}")
    
    def logout(self):
        # Manejar el cierre de sesión
        self.tab_control.pack_forget()
        self.current_user = None
        self.create_login_widget()
    
    def construir_widget_en_tab(self, tab_frame, widget_class):
        for widget in tab_frame.winfo_children():
            widget.destroy()
        widget = widget_class(tab_frame)
        widget.pack(expand=True, fill='both')
        return widget
    
    def on_tab_change(self, event):
        selected_tab = event.widget.select()
        tab_frame = self.tab_control.nametowidget(selected_tab)

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
            # Gestión de Reservas
        elif tab_frame == self.servicios_management_tab:
            self.servicios_management_widget = self.construir_widget_en_tab(tab_frame, ServicioManagementWidget)
            # Gestión de Reservas
        elif tab_frame == self.reservas_management_tab:
            self.reservas_management_widget = self.construir_widget_en_tab(tab_frame, RecaudacionesManagementWidget)

if __name__ == "__main__":
    app = MainWindow()
    app.mainloop()

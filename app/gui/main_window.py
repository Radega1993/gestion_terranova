# Ventana principal de la aplicación
import tkinter as tk
from tkinter import messagebox, ttk
import logging

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
        # Agregar una pestaña o botón para cerrar sesión
        logout_tab = tk.Frame(self.tab_control)
        logout_button = tk.Button(logout_tab, text="Cerrar sesión", command=self.logout)
        logout_button.pack(pady=10)

        self.tab_control.add(logout_tab, text="Opciones Usuario")
    
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

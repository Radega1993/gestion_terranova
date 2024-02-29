# Ventana principal de la aplicación
import tkinter as tk
from tkinter import messagebox, ttk

# Importaciones de los widgets que necesitas
from app.gui.widgets.user_login_widget import UserLoginWidget
from app.gui.widgets.user_management_widget import UserManagementWidget
from app.gui.widgets.product_management_widget import ProductManagementWidget

class MainWindow(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Gestión Terranova")
        self.geometry("800x600")  # Configura el tamaño de la ventana aquí

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

        # Pestaña de gestión de productos
        self.product_management_tab = tk.Frame(self.tab_control)
        self.tab_control.add(self.product_management_tab, text="Gestión de Productos")
        self.product_management_widget = ProductManagementWidget(self.product_management_tab)
        self.product_management_widget.pack(expand=True, fill='both')

        
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

if __name__ == "__main__":
    app = MainWindow()
    app.mainloop()

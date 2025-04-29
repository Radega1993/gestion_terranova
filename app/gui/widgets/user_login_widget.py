import tkinter as tk
from tkinter import messagebox
from app.database.connection import Session
from app.database.models import Usuario
from app.logic.users import crear_usuario
from werkzeug.security import check_password_hash
from app.logic.EstadoApp import EstadoApp 

class UserLoginWidget(tk.Frame):
    def __init__(self, parent, login_success_callback):
        super().__init__(parent, bg="#f0f0f0")
        self.login_success_callback = login_success_callback
        self.configure(bg="#f0f0f0")
        self.grid_columnconfigure(0, weight=1)
        
        # Inicializa los widgets de login y registro al inicio
        self.create_login_widgets()
        self.create_register_widgets()
        
        # Inicialmente, solo muestra los widgets de login
        self.show_login_widgets()

    def create_widgets_common_style(self, widget):
        if isinstance(widget, tk.Entry):
            widget.configure(bg="white")
        widget.configure(bg="#f0f0f0", fg="#333", font=("Arial", 12))
        return widget

    def destroy_widgets(self):
        # Destruye todos los widgets en el Frame actual.
        for widget in self.winfo_children():
            widget.destroy()

    def create_login_widgets(self):
        # Marco para el formulario con borde y padding
        login_frame = tk.LabelFrame(self, text="Inicio de Sesión", bg="#f0f0f0", font=("Arial", 14, "bold"), labelanchor="n", padx=20, pady=20)
        login_frame.grid(padx=100, pady=60, sticky="nsew")

        # Crear y configurar widgets aquí antes de posicionarlos
        self.lbl_user_login = self.create_widgets_common_style(tk.Label(login_frame, text="Usuario:"))
        self.user_login_entry = tk.Entry(login_frame)
        self.lbl_password_login = self.create_widgets_common_style(tk.Label(login_frame, text="Contraseña:"))
        self.password_login_entry = tk.Entry(login_frame, show="*")
        self.login_button = self.create_widgets_common_style(tk.Button(login_frame, text="Iniciar sesión", command=self.login))
        self.register_screen_button = self.create_widgets_common_style(tk.Button(login_frame, text="Registrarse", command=self.show_register_widgets))

        # Posicionamiento con .grid() para un layout más preciso
        self.lbl_user_login.grid(row=0, column=0, sticky="w", padx=10, pady=10)
        self.user_login_entry.grid(row=0, column=1, pady=10, padx=10, sticky="ew")
        self.lbl_password_login.grid(row=1, column=0, sticky="w", padx=10, pady=10)
        self.password_login_entry.grid(row=1, column=1, pady=10, padx=10, sticky="ew")
        self.login_button.grid(row=2, column=0, columnspan=2, pady=20, padx=10, sticky="ew")
        self.register_screen_button.grid(row=3, column=0, columnspan=2, padx=10, sticky="ew")

        # Ajustar el grid del frame principal para que los elementos se centren
        login_frame.columnconfigure(1, weight=1)

    def create_register_widgets(self):
        # Marco para el formulario con borde y padding
        register_frame = tk.LabelFrame(self, text="Registro", bg="#f0f0f0", font=("Arial", 14, "bold"), labelanchor="n", padx=20, pady=20)
        register_frame.grid(padx=100, pady=60, sticky="nsew")
 
        self.lbl_nombre_register = self.create_widgets_common_style(tk.Label(register_frame, text="Nombre completo:"))
        self.nombre_register_entry = tk.Entry(register_frame, bg="white")
        self.lbl_user_register = self.create_widgets_common_style(tk.Label(register_frame, text="Usuario:"))
        self.user_register_entry = tk.Entry(register_frame, bg="white")
        self.lbl_password_register = self.create_widgets_common_style(tk.Label(register_frame, text="Contraseña:"))
        self.password_register_entry = tk.Entry(register_frame, show="*", bg="white")
        self.register_button = self.create_widgets_common_style(tk.Button(register_frame, text="Registrar", command=self.register))
        self.login_screen_button = self.create_widgets_common_style(tk.Button(register_frame, text="Volver a inicio de sesión", command=self.show_login_widgets))

        self.lbl_nombre_register.grid(in_=register_frame, row=0, column=0, sticky="w", padx=10, pady=5)
        self.nombre_register_entry.grid(in_=register_frame, row=0, column=1, sticky="ew", padx=10, pady=5)
        self.lbl_user_register.grid(in_=register_frame, row=1, column=0, sticky="w", padx=10, pady=5)
        self.user_register_entry.grid(in_=register_frame, row=1, column=1, sticky="ew", padx=10, pady=5)
        self.lbl_password_register.grid(in_=register_frame, row=2, column=0, sticky="w", padx=10, pady=5)
        self.password_register_entry.grid(in_=register_frame, row=2, column=1, sticky="ew", padx=10, pady=5)
        self.register_button.grid(in_=register_frame, row=3, column=0, columnspan=2, sticky="ew", padx=10, pady=10)
        self.login_screen_button.grid(in_=register_frame, row=4, column=0, columnspan=2, sticky="ew", padx=10, pady=10)

        # Asegúrate de que el contenedor de registro ajuste su tamaño según el contenido
        register_frame.columnconfigure(1, weight=1)

    def show_login_widgets(self):
        self.destroy_widgets()
        self.create_login_widgets()
        
    def show_register_widgets(self):
        self.destroy_widgets()
        self.create_register_widgets()

    def login(self):
        user = self.user_login_entry.get()
        password = self.password_login_entry.get()
        with Session() as session:
            usuario = session.query(Usuario).filter_by(user=user).first()
            if usuario and check_password_hash(usuario.contrasena_hash, password):
                if not usuario.validado:
                    messagebox.showerror("Error", "Tu cuenta aún no ha sido validada por un administrador.")
                    return
                EstadoApp.set_usuario_logueado_id(usuario.id)
                self.login_success_callback(usuario)
            else:
                messagebox.showerror("Error", "Inicio de sesión fallido. Verifica tu usuario y contraseña.")


    def register(self):
        nombre = self.nombre_register_entry.get()
        user = self.user_register_entry.get()
        password = self.password_register_entry.get()
        if nombre and user and password:
            try:
                crear_usuario(nombre, user, "cliente", password)  # Asume que ya tienes esta función
                messagebox.showinfo("Registro", "Usuario registrado con éxito. Por favor, inicia sesión.")
                self.show_login_widgets()
            except Exception as e:
                messagebox.showerror("Registro", str(e))
        else:
            messagebox.showerror("Registro Incompleto", "Todos los campos son obligatorios.")

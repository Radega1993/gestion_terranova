import tkinter as tk
from tkinter import messagebox
from app.database.connection import Session
from app.database.models import Usuario
from app.logic.users import crear_usuario, obtener_usuario_por_correo
from werkzeug.security import check_password_hash

class UserLoginWidget(tk.Frame):
    def __init__(self, parent, login_success_callback):
        super().__init__(parent, bg="#f0f0f0")
        self.login_success_callback = login_success_callback
        self.configure(bg="#f0f0f0")
        self.grid_columnconfigure(0, weight=1)  # Centrar contenido
        self.create_login_widgets()
        self.create_register_widgets()

    def create_widgets_common_style(self, widget):
        widget.configure(
            bg="#f0f0f0",
            fg="#333",
            font=("Arial", 12)
        )
        return widget

    def create_login_widgets(self):
        # Marco para el formulario con borde y padding
        login_frame = tk.LabelFrame(self, text="Inicio de Sesión", bg="#f0f0f0", font=("Arial", 14, "bold"), labelanchor="n", padx=20, pady=20)
        login_frame.grid(padx=100, pady=60, sticky="nsew")

        # Crear y configurar widgets aquí antes de posicionarlos
        self.lbl_email_login = self.create_widgets_common_style(tk.Label(login_frame, text="Correo electrónico:"))
        self.email_login_entry = tk.Entry(login_frame)
        self.lbl_password_login = self.create_widgets_common_style(tk.Label(login_frame, text="Contraseña:"))
        self.password_login_entry = tk.Entry(login_frame, show="*")
        self.login_button = self.create_widgets_common_style(tk.Button(login_frame, text="Iniciar sesión", command=self.login))
        self.register_screen_button = self.create_widgets_common_style(tk.Button(login_frame, text="Registrarse", command=self.show_register_widgets))

        # Posicionamiento con .grid() para un layout más preciso
        self.lbl_email_login.grid(row=0, column=0, sticky="w", padx=10, pady=10)
        self.email_login_entry.grid(row=0, column=1, pady=10, padx=10, sticky="ew")
        self.lbl_password_login.grid(row=1, column=0, sticky="w", padx=10, pady=10)
        self.password_login_entry.grid(row=1, column=1, pady=10, padx=10, sticky="ew")
        self.login_button.grid(row=2, column=0, columnspan=2, pady=20, padx=10, sticky="ew")
        self.register_screen_button.grid(row=3, column=0, columnspan=2, padx=10, sticky="ew")

        # Ajustar el grid del frame principal para que los elementos se centren
        login_frame.columnconfigure(1, weight=1)

    def create_register_widgets(self):
        self.lbl_nombre_register = self.create_widgets_common_style(tk.Label(self, text="Nombre completo:"))
        self.nombre_register_entry = self.create_widgets_common_style(tk.Entry(self))

        self.lbl_email_register = self.create_widgets_common_style(tk.Label(self, text="Correo electrónico:"))
        self.email_register_entry = self.create_widgets_common_style(tk.Entry(self))

        self.lbl_password_register = self.create_widgets_common_style(tk.Label(self, text="Contraseña:"))
        self.password_register_entry = self.create_widgets_common_style(tk.Entry(self, show="*"))
        self.register_button = self.create_widgets_common_style(tk.Button(self, text="Registrar", command=self.register))
        self.login_screen_button = self.create_widgets_common_style(tk.Button(self, text="Volver a inicio de sesión", command=self.show_login_widgets))

        # Esconder por defecto
        for widget in [self.nombre_register_entry, self.email_register_entry, self.password_register_entry, self.register_button, self.login_screen_button]:
            widget.pack_forget()

    def show_login_widgets(self):
        # Ocultar widgets de registro
        for widget in [self.lbl_nombre_register, self.nombre_register_entry, self.lbl_email_register, self.email_register_entry, self.lbl_password_register, self.password_register_entry, self.register_button, self.login_screen_button]:
            widget.grid_remove() 
        # Mostrar widgets de login
        self.email_login_entry.pack()
        self.password_login_entry.pack()
        self.login_button.pack()
        self.register_screen_button.pack()

        # Esconder widgets de registro
        self.nombre_register_entry.pack_forget()
        self.email_register_entry.pack_forget()
        self.password_register_entry.pack_forget()
        self.register_button.pack_forget()
        self.login_screen_button.pack_forget()

    def show_register_widgets(self):
        # Ocultar widgets de login
        for widget in [self.lbl_email_login, self.email_login_entry, self.lbl_password_login, self.password_login_entry, self.login_button, self.register_screen_button]:
            widget.grid_remove()  # Usa grid_remove para ocultar los widgets

            # Mostrar widgets de registro usando .grid()
            self.lbl_nombre_register.grid(row=0, column=0, sticky="w", padx=10, pady=10)
            self.nombre_register_entry.grid(row=0, column=1, pady=10, padx=10, sticky="ew")
            self.lbl_email_register.grid(row=1, column=0, sticky="w", padx=10, pady=10)
            self.email_register_entry.grid(row=1, column=1, pady=10, padx=10, sticky="ew")
            self.lbl_password_register.grid(row=2, column=0, sticky="w", padx=10, pady=10)
            self.password_register_entry.grid(row=2, column=1, pady=10, padx=10, sticky="ew")
            self.register_button.grid(row=3, column=0, columnspan=2, pady=20, padx=10, sticky="ew")
            self.login_screen_button.grid(row=4, column=0, columnspan=2, padx=10, sticky="ew")


    def login(self):
        email = self.email_login_entry.get()
        password = self.password_login_entry.get()
        with Session() as session:
            usuario = session.query(Usuario).filter_by(correo_electronico=email).first()
            if usuario and check_password_hash(usuario.contrasena_hash, password):
                self.login_success_callback(usuario)
            else:
                messagebox.showerror("Error", "Inicio de sesión fallido. Verifica tu correo electrónico y contraseña.")


    def register(self):
        nombre = self.nombre_register_entry.get()
        email = self.email_register_entry.get()
        password = self.password_register_entry.get()
        if nombre and email and password:
            try:
                crear_usuario(nombre, email, "cliente", password)  # Asume que ya tienes esta función
                messagebox.showinfo("Registro", "Usuario registrado con éxito. Por favor, inicia sesión.")
                self.show_login_widgets()
            except Exception as e:
                messagebox.showerror("Registro", str(e))
        else:
            messagebox.showerror("Registro Incompleto", "Todos los campos son obligatorios.")

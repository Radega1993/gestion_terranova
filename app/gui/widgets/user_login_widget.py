import tkinter as tk
from tkinter import messagebox
from app.database.connection import Session
from app.database.models import Usuario
from app.logic.users import crear_usuario, obtener_usuario_por_correo
from werkzeug.security import check_password_hash

class UserLoginWidget(tk.Frame):
    def __init__(self, parent, login_success_callback):
        super().__init__(parent)
        self.login_success_callback = login_success_callback
        self.create_login_widgets()
        self.create_register_widgets()

        # Inicialmente, solo mostrar widgets de login
        self.show_login_widgets()

    def create_login_widgets(self):
        self.email_login_entry = tk.Entry(self)
        self.password_login_entry = tk.Entry(self, show="*")
        self.login_button = tk.Button(self, text="Iniciar sesión", command=self.login)
        self.register_screen_button = tk.Button(self, text="Registrarse", command=self.show_register_widgets)

    def create_register_widgets(self):
        # Widgets de registro
        self.nombre_register_entry = tk.Entry(self)
        self.email_register_entry = tk.Entry(self)
        self.password_register_entry = tk.Entry(self, show="*")
        self.register_button = tk.Button(self, text="Registrar", command=self.register)
        self.login_screen_button = tk.Button(self, text="Volver a inicio de sesión", command=self.show_login_widgets)

        # Esconder por defecto
        self.nombre_register_entry.pack_forget()
        self.email_register_entry.pack_forget()
        self.password_register_entry.pack_forget()
        self.register_button.pack_forget()
        self.login_screen_button.pack_forget()

    def show_login_widgets(self):
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
        # Esconder widgets de login
        self.email_login_entry.pack_forget()
        self.password_login_entry.pack_forget()
        self.login_button.pack_forget()
        self.register_screen_button.pack_forget()

        # Mostrar widgets de registro
        self.nombre_register_entry.pack()
        self.email_register_entry.pack()
        self.password_register_entry.pack()
        self.register_button.pack()
        self.login_screen_button.pack()

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

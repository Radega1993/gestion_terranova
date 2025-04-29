import tkinter as tk
from tkinter import messagebox
from app.logic.users import crear_usuario
from app.database.models import Usuario

class RegistrationForm(tk.Toplevel):
    def __init__(self):
        super().__init__()
        self.title("Formulario de Registro")

        # Configura el tamaño y posición del formulario en la pantalla
        self.geometry("300x200")

        # Nombre
        self.lbl_nombre = tk.Label(self, text="Nombre:")
        self.lbl_nombre.pack(pady=(10, 0))
        self.entry_nombre = tk.Entry(self)
        self.entry_nombre.pack()

        # Correo Electrónico
        self.lbl_email = tk.Label(self, text="Correo electrónico:")
        self.lbl_email.pack(pady=(10, 0))
        self.entry_email = tk.Entry(self)
        self.entry_email.pack()

        # Contraseña
        self.lbl_password = tk.Label(self, text="Contraseña:")
        self.lbl_password.pack(pady=(10, 0))
        self.entry_password = tk.Entry(self, show="*")
        self.entry_password.pack()

        # Botón de Registro
        self.btn_register = tk.Button(self, text="Registrar", command=self.register)
        self.btn_register.pack(pady=(10, 0))

    def register(self):
        nombre = self.entry_nombre.get()
        email = self.entry_email.get()
        password = self.entry_password.get()

        if nombre and email and password:
            try:
                crear_usuario(nombre, email, Usuario.TIPOS_USUARIO[0], password, validado=False)
                messagebox.showinfo("Registro", "Usuario registrado con éxito. Por favor, espera a que un administrador valide tu cuenta.")
                self.destroy()  # Cierra la ventana de registro tras el éxito
            except Exception as e:
                messagebox.showerror("Registro", str(e))
        else:
            messagebox.showerror("Registro Incompleto", "Todos los campos son obligatorios.")

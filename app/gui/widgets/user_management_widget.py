# En gui/widgets/user_management_widget.py
import tkinter as tk
from tkinter import messagebox
from app.logic.users import crear_usuario

class UserManagementWidget(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.create_widgets()

    def create_widgets(self):
        # Componentes de la UI para crear un nuevo usuario, como nombre, correo electrónico, tipo de usuario, etc.
        self.name_entry = tk.Entry(self)
        self.name_entry.pack()

        self.email_entry = tk.Entry(self)
        self.email_entry.pack()
        
        # Asumiendo que 'tipo_usuario' es un dropdown o similar
        self.type_entry = tk.Entry(self)
        self.type_entry.pack()

        self.create_button = tk.Button(self, text="Crear Usuario", command=self.create_user)
        self.create_button.pack()

    def create_user(self):
        name = self.name_entry.get()
        email = self.email_entry.get()
        user_type = self.type_entry.get()  # 'trabajador' o 'cliente'
        try:
            user_id = crear_usuario(name, email, user_type)
            messagebox.showinfo("Usuario", f"Usuario creado con éxito. ID: {user_id}")
        except Exception as e:
            messagebox.showerror("Error", str(e))

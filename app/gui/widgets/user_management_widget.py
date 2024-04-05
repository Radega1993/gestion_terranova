import tkinter as tk
from tkinter import messagebox, ttk
from app.database.connection import Session
from app.database.models import Usuario
from app.logic.users import crear_usuario, obtener_usuarios, actualizar_usuario, eliminar_usuario

class UserManagementWidget(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.selected_user = None  # Para almacenar el usuario seleccionado de la lista
        self.create_widgets()
        self.load_users()

    def create_widgets(self):
        self.user_listbox = tk.Listbox(self)
        self.user_listbox.pack(fill=tk.BOTH, expand=True)
        self.user_listbox.bind('<<ListboxSelect>>', self.on_user_select)

        self.name_entry = tk.Entry(self)
        self.name_entry.pack()

        # Cambiar el Entry de user por un Label para visualización
        self.user_label = tk.Label(self, text="Usuario: ")
        self.user_label.pack()

        self.tipo_usuario_options = ['Trabajador', 'Administrador', 'Junta']
        self.type_combobox = ttk.Combobox(self, values=self.tipo_usuario_options, state="readonly")
        self.type_combobox.pack()

        self.create_button = tk.Button(self, text="Crear/Actualizar Usuario", command=self.create_or_update_user)
        self.create_button.pack()

        self.delete_button = tk.Button(self, text="Eliminar Usuario", command=self.delete_user)
        self.delete_button.pack()

    def load_users(self):
        self.user_listbox.delete(0, tk.END)  # Limpiar la lista antes de cargar
        try:
            for user in obtener_usuarios():
                user_info = f"{user['id']}: {user['nombre']} - {user['user']} - {user['tipo_usuario']}"
                self.user_listbox.insert(tk.END, user_info)
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def on_user_select(self, event):
        selection = event.widget.curselection()
        if selection:
            index = selection[0]
            data = event.widget.get(index)
            user_id, user_info = data.split(':', 1)
            name, user, user_type = user_info.split(' - ')
            self.selected_user = user_id.strip()
            self.name_entry.delete(0, tk.END)
            self.name_entry.insert(0, name.strip())
            # Mostrar el usuario seleccionado como texto en lugar de permitir su edición
            self.user_label.config(text=f"Usuario: {user.strip()}")
            self.type_combobox.set(user_type.strip())

    def create_or_update_user(self):
        name = self.name_entry.get()
        user_type = self.type_combobox.get()  # Obtener el valor seleccionado del Combobox
        try:
            if self.selected_user:
                # Actualizar solo nombre y tipo de usuario, ya que 'user' no se puede modificar
                actualizar_usuario(self.selected_user, name, user_type)
                messagebox.showinfo("Usuario", "Usuario actualizado con éxito.")
            else:
                messagebox.showerror("Error", "La creación de nuevos usuarios no se maneja aquí.")
            self.load_users()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def delete_user(self):
        if self.selected_user:
            try:
                eliminar_usuario(self.selected_user)
                messagebox.showinfo("Usuario", "Usuario eliminado con éxito.")
                self.load_users()
            except Exception as e:
                messagebox.showerror("Error", str(e))
        else:
            messagebox.showwarning("Seleccionar usuario", "Por favor, selecciona un usuario para eliminar.")

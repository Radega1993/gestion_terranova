import tkinter as tk
from tkinter import messagebox, ttk
from app.database.connection import Session
from app.database.models import Usuario
from app.logic.users import crear_usuario, obtener_usuarios, actualizar_usuario, eliminar_usuario, toggle_validacion_usuario, obtener_usuario_por_id

class PasswordDialog(tk.Toplevel):
    def __init__(self, parent, title="Crear Contraseña"):
        super().__init__(parent)
        self.title(title)
        self.password = None
        
        # Configura el tamaño y posición
        self.geometry("300x150")
        self.resizable(False, False)
        
        # Contraseña
        self.lbl_password = tk.Label(self, text="Contraseña:")
        self.lbl_password.pack(pady=(10, 0))
        self.entry_password = tk.Entry(self, show="*")
        self.entry_password.pack()
        
        # Confirmar Contraseña
        self.lbl_confirm = tk.Label(self, text="Confirmar Contraseña:")
        self.lbl_confirm.pack(pady=(10, 0))
        self.entry_confirm = tk.Entry(self, show="*")
        self.entry_confirm.pack()
        
        # Botón Aceptar
        self.btn_accept = tk.Button(self, text="Aceptar", command=self.accept)
        self.btn_accept.pack(pady=(10, 0))
        
        # Hacer modal
        self.transient(parent)
        self.grab_set()
        
    def accept(self):
        if self.entry_password.get() != self.entry_confirm.get():
            messagebox.showerror("Error", "Las contraseñas no coinciden")
            return
        
        if not self.entry_password.get():
            messagebox.showerror("Error", "La contraseña no puede estar vacía")
            return
            
        self.password = self.entry_password.get()
        self.destroy()

class UserManagementWidget(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        
        # Frame para la lista de usuarios
        self.list_frame = ttk.Frame(self)
        self.list_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Lista de usuarios
        self.user_list = ttk.Treeview(self.list_frame, columns=("ID", "Nombre", "Email", "Tipo", "Validado"), show="headings")
        self.user_list.heading("ID", text="ID")
        self.user_list.heading("Nombre", text="Nombre")
        self.user_list.heading("Email", text="Email")
        self.user_list.heading("Tipo", text="Tipo")
        self.user_list.heading("Validado", text="Validado")
        self.user_list.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Scrollbar para la lista
        scrollbar = ttk.Scrollbar(self.list_frame, orient=tk.VERTICAL, command=self.user_list.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.user_list.configure(yscrollcommand=scrollbar.set)
        
        # Frame para el formulario
        self.form_frame = ttk.Frame(self)
        self.form_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Campos del formulario
        self.lbl_usuario = ttk.Label(self.form_frame, text="Usuario:")
        self.lbl_usuario.pack(pady=(0, 5))
        self.entry_usuario = ttk.Entry(self.form_frame)
        self.entry_usuario.pack(fill=tk.X, pady=(0, 10))
        
        self.lbl_email = ttk.Label(self.form_frame, text="Email:")
        self.lbl_email.pack(pady=(0, 5))
        self.entry_email = ttk.Entry(self.form_frame)
        self.entry_email.pack(fill=tk.X, pady=(0, 10))
        
        self.lbl_tipo = ttk.Label(self.form_frame, text="Tipo:")
        self.lbl_tipo.pack(pady=(0, 5))
        self.combo_tipo = ttk.Combobox(self.form_frame, values=Usuario.TIPOS_USUARIO, state="readonly")
        self.combo_tipo.pack(fill=tk.X, pady=(0, 10))
        self.combo_tipo.set(Usuario.TIPOS_USUARIO[0])  # Valor por defecto
        
        # Frame para los botones
        self.button_frame = ttk.Frame(self.form_frame)
        self.button_frame.pack(fill=tk.X, pady=10)
        
        # Botones
        self.btn_create = ttk.Button(self.button_frame, text="Crear Usuario", command=self.create_user)
        self.btn_create.pack(side=tk.LEFT, padx=5)
        
        self.btn_update = ttk.Button(self.button_frame, text="Actualizar Usuario", command=self.update_user, state=tk.DISABLED)
        self.btn_update.pack(side=tk.LEFT, padx=5)
        
        self.btn_change_password = ttk.Button(self.button_frame, text="Cambiar Contraseña", command=self.change_password, state=tk.DISABLED)
        self.btn_change_password.pack(side=tk.LEFT, padx=5)
        
        self.btn_clear = ttk.Button(self.button_frame, text="Limpiar", command=self.clear_selection)
        self.btn_clear.pack(side=tk.LEFT, padx=5)
        
        # Botón de validación
        self.btn_validate = ttk.Button(self.button_frame, text="Validar/Invalidar", command=self.toggle_validation)
        self.btn_validate.pack(side=tk.LEFT, padx=5)
        
        # Evento de selección
        self.user_list.bind('<<TreeviewSelect>>', self.on_user_select)
        
        # Variable para almacenar el ID del usuario seleccionado
        self.selected_user_id = None
        
        # Cargar usuarios
        self.load_users()
    
    def load_users(self):
        # Limpiar lista actual
        for item in self.user_list.get_children():
            self.user_list.delete(item)
        
        # Cargar usuarios desde la base de datos
        users = obtener_usuarios()
        for user in users:
            self.user_list.insert("", tk.END, values=(user.id, user.nombre, user.user, user.tipo_usuario, "Sí" if user.validado else "No"))
    
    def on_user_select(self, event):
        selected_items = self.user_list.selection()
        if not selected_items:
            return
        
        # Obtener datos del usuario seleccionado
        item = selected_items[0]
        user_id = self.user_list.item(item)['values'][0]
        user = obtener_usuario_por_id(user_id)
        
        # Actualizar campos del formulario
        self.entry_usuario.delete(0, tk.END)
        self.entry_usuario.insert(0, user.nombre)
        self.entry_usuario.config(state='readonly')
        
        self.entry_email.delete(0, tk.END)
        self.entry_email.insert(0, user.user)
        
        self.combo_tipo.set(user.tipo_usuario)
        
        # Actualizar estado de los botones
        self.btn_create.config(state=tk.DISABLED)
        self.btn_update.config(state=tk.NORMAL)
        self.btn_change_password.config(state=tk.NORMAL)
        
        # Guardar ID del usuario seleccionado
        self.selected_user_id = user_id
    
    def clear_selection(self):
        # Limpiar selección en la lista
        for item in self.user_list.selection():
            self.user_list.selection_remove(item)
        
        # Limpiar campos del formulario
        self.entry_usuario.config(state='normal')
        self.entry_usuario.delete(0, tk.END)
        self.entry_email.delete(0, tk.END)
        self.combo_tipo.set(Usuario.TIPOS_USUARIO[0])
        
        # Actualizar estado de los botones
        self.btn_create.config(state=tk.NORMAL)
        self.btn_update.config(state=tk.DISABLED)
        self.btn_change_password.config(state=tk.DISABLED)
        
        # Limpiar ID del usuario seleccionado
        self.selected_user_id = None
    
    def create_user(self):
        # Validar campos
        nombre = self.entry_usuario.get().strip()
        user = self.entry_email.get().strip()
        tipo = self.combo_tipo.get()
        
        if not nombre or not user or not tipo:
            messagebox.showerror("Error", "Todos los campos son obligatorios")
            return
        
        # Mostrar diálogo de contraseña
        dialog = PasswordDialog(self)
        self.wait_window(dialog)
        
        if dialog.password:
            try:
                crear_usuario(nombre, user, tipo, dialog.password, validado=True)
                messagebox.showinfo("Éxito", "Usuario creado correctamente")
                self.load_users()
                self.clear_selection()
            except Exception as e:
                messagebox.showerror("Error", str(e))
    
    def update_user(self):
        if not self.selected_user_id:
            return
        
        # Validar campos
        user = self.entry_email.get().strip()
        tipo = self.combo_tipo.get()
        
        if not user or not tipo:
            messagebox.showerror("Error", "Todos los campos son obligatorios")
            return
        
        try:
            actualizar_usuario(self.selected_user_id, user=user, tipo_usuario=tipo)
            messagebox.showinfo("Éxito", "Usuario actualizado correctamente")
            self.load_users()
            self.clear_selection()
        except Exception as e:
            messagebox.showerror("Error", str(e))
    
    def change_password(self):
        if not self.selected_user_id:
            return
        
        # Mostrar diálogo de contraseña
        dialog = PasswordDialog(self, title="Cambiar Contraseña")
        self.wait_window(dialog)
        
        if dialog.password:
            try:
                actualizar_usuario(self.selected_user_id, password=dialog.password)
                messagebox.showinfo("Éxito", "Contraseña actualizada correctamente")
            except Exception as e:
                messagebox.showerror("Error", str(e))
    
    def toggle_validation(self):
        if not self.selected_user_id:
            return
        
        try:
            # Obtener el usuario actual
            user = obtener_usuario_por_id(self.selected_user_id)
            
            # No permitir invalidar administradores
            if user.tipo_usuario == Usuario.TIPOS_USUARIO[1]:  # Administrador
                messagebox.showerror("Error", "No se puede invalidar a un administrador")
                return
            
            # Si vamos a invalidar, verificar que quede al menos un administrador válido
            if user.validado:
                # Obtener todos los usuarios
                users = obtener_usuarios()
                # Contar administradores válidos
                valid_admins = sum(1 for u in users if u.tipo_usuario == Usuario.TIPOS_USUARIO[1] and u.validado and u.id != user.id)
                
                if valid_admins == 0:
                    messagebox.showerror("Error", "No se puede invalidar al usuario. Debe haber al menos un administrador válido en el sistema.")
                    return
            
            toggle_validacion_usuario(self.selected_user_id)
            messagebox.showinfo("Éxito", "Estado de validación actualizado correctamente")
            self.load_users()
        except Exception as e:
            messagebox.showerror("Error", str(e))

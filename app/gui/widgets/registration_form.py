from app.database.models import Usuario

class RegistrationForm(ttk.Frame):
    def __init__(self, parent, on_register=None):
        super().__init__(parent)
        self.on_register = on_register
        self.create_widgets()

    def register(self):
        # Obtener los valores de los campos
        usuario = self.username_entry.get()
        nombre = self.name_entry.get()
        apellidos = self.surname_entry.get()
        password = self.password_entry.get()
        confirm_password = self.confirm_password_entry.get()

        # Validar que todos los campos estén llenos
        if not all([usuario, nombre, apellidos, password, confirm_password]):
            messagebox.showerror("Error", "Por favor, rellene todos los campos.")
            return

        # Validar que las contraseñas coincidan
        if password != confirm_password:
            messagebox.showerror("Error", "Las contraseñas no coinciden.")
            return

        try:
            # Crear el usuario con tipo "Trabajador"
            crear_usuario(usuario, nombre, apellidos, password, Usuario.TIPOS_USUARIO[0], validado=False)
            messagebox.showinfo("Éxito", "Usuario registrado correctamente. Un administrador debe validar su cuenta antes de poder acceder.")
            if self.on_register:
                self.on_register()
        except Exception as e:
            messagebox.showerror("Error", str(e)) 
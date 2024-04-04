import tkinter as tk
from tkinter import messagebox, ttk

class DialogoServicio(tk.Toplevel):
    def __init__(self, parent, servicio=None):
        super().__init__(parent)
        self.transient(parent)
        self.title("Servicio")

        self.resultado = None

        tk.Label(self, text="Nombre:").grid(row=0, column=0)
        self.nombre_entry = tk.Entry(self)
        self.nombre_entry.grid(row=0, column=1)
        if servicio:
            self.nombre_entry.insert(0, servicio.nombre)

        tk.Label(self, text="Precio:").grid(row=1, column=0)
        self.precio_entry = tk.Entry(self)
        self.precio_entry.grid(row=1, column=1)
        if servicio:
            self.precio_entry.insert(0, str(servicio.precio))

        # Nuevo campo para el tipo de servicio
        tk.Label(self, text="Tipo:").grid(row=2, column=0)
        self.tipo_var = tk.StringVar(self)
        self.tipo_combobox = ttk.Combobox(self, textvariable=self.tipo_var, values=["servicio", "suplemento"], state="readonly")
        self.tipo_combobox.grid(row=2, column=1)
        if servicio and hasattr(servicio, 'tipo'):
            self.tipo_combobox.set(servicio.tipo)
        else:
            self.tipo_combobox.set("servicio")  # Valor predeterminado

        tk.Button(self, text="Confirmar", command=self.confirmar).grid(row=3, column=0, columnspan=2)

        self.grab_set()
        self.wait_window(self)

    def confirmar(self):
        nombre = self.nombre_entry.get()
        tipo = self.tipo_var.get()
        try:
            precio = float(self.precio_entry.get())
            self.resultado = (nombre, precio, tipo)
            self.destroy()
        except ValueError:
            messagebox.showerror("Error", "El precio debe ser un número.")

def abrir_dialogo_servicio(parent, servicio=None):
    dialogo = DialogoServicio(parent, servicio)
    return dialogo.resultado

import tkinter as tk
from tkinter import simpledialog

class SocioDialog(tk.Toplevel):
    def __init__(self, parent, socio=None):
        super().__init__(parent)
        self.transient(parent)
        self.socio = socio
        self.title("Socio")

        tk.Label(self, text="Nombre:").grid(row=0, column=0)
        self.nombre_entry = tk.Entry(self)
        self.nombre_entry.grid(row=0, column=1)

        tk.Label(self, text="Correo Electrónico:").grid(row=1, column=0)
        self.correo_entry = tk.Entry(self)
        self.correo_entry.grid(row=1, column=1)

        if socio:
            self.nombre_entry.insert(0, socio.nombre)
            self.correo_entry.insert(0, socio.correo_electronico)

        tk.Button(self, text="Guardar", command=self.guardar).grid(row=3, column=0, columnspan=2)

        self.grab_set()
        self.wait_window(self)
        
    def guardar(self):
        self.nombre = self.nombre_entry.get()
        self.correo = self.correo_entry.get()
        self.destroy()

def abrir_dialogo_socio(parent, socio=None):
    dialogo = SocioDialog(parent, socio)
    if hasattr(dialogo, 'nombre'):
        return dialogo.nombre, dialogo.correo
    else:
        return None, None

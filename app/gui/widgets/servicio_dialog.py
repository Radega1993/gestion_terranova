import tkinter as tk
from tkinter import messagebox

class DialogoServicio(tk.Toplevel):
    def __init__(self, parent, servicio=None):
        super().__init__(parent)
        self.transient(parent)  # Configura este diálogo como una ventana secundaria de la ventana 'parent'
        self.title("Servicio")

        self.resultado = None  # Para almacenar el resultado de este diálogo

        # Creación de widgets dentro del diálogo
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

        # Botón de confirmar que llama al método interno confirmar
        tk.Button(self, text="Confirmar", command=self.confirmar).grid(row=2, column=0, columnspan=2)

        self.grab_set()  # Prevenir el acceso a otras ventanas mientras esta esté abierta
        self.wait_window(self)  # Esperar que este diálogo se cierre antes de continuar

    def confirmar(self):
        # Intenta capturar y validar los datos aquí
        nombre = self.nombre_entry.get()
        try:
            precio = float(self.precio_entry.get())
            self.resultado = (nombre, precio)
            self.destroy()  # Cierra el diálogo solo después de capturar los datos
        except ValueError:
            messagebox.showerror("Error", "El precio debe ser un número.")

def abrir_dialogo_servicio(parent, servicio=None):
    dialogo = DialogoServicio(parent, servicio)
    return dialogo.resultado  # Devuelve el resultado después de que el diálogo se haya cerrado

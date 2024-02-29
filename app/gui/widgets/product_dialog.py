import tkinter as tk

class ProductDialog(tk.Toplevel):
    def __init__(self, parent, producto=None):
        super().__init__(parent)
        self.transient(parent)  # Configura este diálogo como una ventana secundaria de la ventana 'parent'
        self.producto = producto
        self.title("Producto")

        # Campos del formulario
        tk.Label(self, text="Nombre:").grid(row=0, column=0)
        self.nombre_entry = tk.Entry(self)
        self.nombre_entry.grid(row=0, column=1)

        tk.Label(self, text="Precio:").grid(row=1, column=0)
        self.precio_entry = tk.Entry(self)
        self.precio_entry.grid(row=1, column=1)

        tk.Label(self, text="Stock:").grid(row=2, column=0)
        self.stock_entry = tk.Entry(self)
        self.stock_entry.grid(row=2, column=1)

        if producto:
            # Si se está actualizando un producto, prellenar los campos
            self.nombre_entry.insert(0, producto.nombre)
            self.precio_entry.insert(0, str(producto.precio))
            self.stock_entry.insert(0, str(producto.stock_actual))

        tk.Button(self, text="Guardar", command=self.guardar).grid(row=3, column=0, columnspan=2)

        self.grab_set()  # Hace que este diálogo capture todo el input hacia la aplicación
        self.wait_window(self)  # Espera hasta que este diálogo se cierre

    def guardar(self):
        self.nombre = self.nombre_entry.get()
        self.precio = float(self.precio_entry.get())
        self.stock = int(self.stock_entry.get())
        self.destroy()  # Cierra el diálogo

def abrir_dialogo_producto(parent, producto=None):
    dialogo = ProductDialog(parent, producto)
    if hasattr(dialogo, 'nombre'):
        return dialogo.nombre, dialogo.precio, dialogo.stock
    return None, None, None

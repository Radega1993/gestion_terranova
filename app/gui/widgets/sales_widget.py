# Widget de ventas

import tkinter as tk
from tkinter import ttk

class SalesWidget(tk.Frame):
    def __init__(self, parent, process_sale_callback):
        super().__init__(parent)
        self.process_sale_callback = process_sale_callback
        self.create_widgets()

    def create_widgets(self):
        self.product_id_label = tk.Label(self, text="ID del Producto:")
        self.product_id_label.grid(row=0, column=0)
        
        self.product_id_entry = tk.Entry(self)
        self.product_id_entry.grid(row=0, column=1)

        self.quantity_label = tk.Label(self, text="Cantidad:")
        self.quantity_label.grid(row=1, column=0)
        
        self.quantity_entry = tk.Entry(self)
        self.quantity_entry.grid(row=1, column=1)

        self.add_button = tk.Button(self, text="Añadir Producto", command=self.add_product)
        self.add_button.grid(row=2, column=0, columnspan=2)

    def add_product(self):
        # Aquí implementarías la lógica para añadir el producto a una lista de ventas
        product_id = self.product_id_entry.get()
        quantity = self.quantity_entry.get()
        self.process_sale_callback([{'producto_id': int(product_id), 'cantidad': int(quantity)}])

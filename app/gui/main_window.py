# Ventana principal de la aplicación

import tkinter as tk
from tkinter import messagebox

from app.database.connection import Session
from app.logic.sales import procesar_venta

class MainWindow(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Gestión Terranova")
        self.geometry("800x600")  # Configura el tamaño de la ventana aquí
        
        # Añade más widgets aquí
        self.create_widgets()

    def create_widgets(self):
        # Ejemplo de widget: Un simple botón para procesar venta
        self.sale_button = tk.Button(self, text="Procesar Venta", command=self.on_sale_button_clicked)
        self.sale_button.pack(pady=20)

    def on_sale_button_clicked(self):
        # Esta función se llamará cuando el botón sea presionado
        try:
            # Asumiremos que hay una función para obtener los detalles de la venta
            detalles_venta = self.get_sale_details_from_ui()
            # Asumiendo que detalles_venta es una lista de diccionarios con 'producto_id' y 'cantidad'
            with Session() as session:
                procesar_venta(session, detalles_venta)
            messagebox.showinfo("Éxito", "La venta ha sido procesada correctamente.")
        except Exception as e:
            messagebox.showerror("Error", str(e))
            
    def get_sale_details_from_ui(self):
        # Método dummy para el ejemplo. Deberías implementar la lógica para obtener los detalles de la UI
        return [{'producto_id': 1, 'cantidad': 2}]  # Ejemplo de estructura esperada

if __name__ == "__main__":
    app = MainWindow()
    app.mainloop()

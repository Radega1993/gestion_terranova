import tkinter as tk
from tkinter import ttk
from tkinter import messagebox

from app.gui.widgets.deber_dialog import DeudaDetalleDialog
from app.logic.deudas import obtener_deudas_agrupadas, procesar_pago

class DeudasWidget(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.configure(bg='#f0f0f0')  # Fondo claro para el frame

        style = ttk.Style()
        style.configure("Treeview", font=('Helvetica', 12), rowheight=25)
        style.configure("Treeview.Heading", font=('Helvetica', 13, 'bold'))
        style.map("TButton", foreground=[('pressed', 'white'), ('active', 'white')],
          background=[('pressed', '!disabled', '#4a69bd'), ('active', '#4a69bd')])

        self.create_widgets()

    def create_widgets(self):
        self.treeview = ttk.Treeview(self, columns=("socio_id", "nombre", "total_deuda"), show="headings")
        self.treeview.heading("socio_id", text="ID Socio")
        self.treeview.heading("nombre", text="Nombre Socio")
        self.treeview.heading("total_deuda", text="Total Deuda")
        self.treeview.pack(fill=tk.BOTH, expand=True)

        # Suponiendo que tienes una función que obtiene las deudas agrupadas
        deudas_agrupadas = obtener_deudas_agrupadas()
        for deuda in deudas_agrupadas:
            self.treeview.insert('', tk.END, values=(deuda['socio_id'], deuda['nombre'], f"{deuda['total_deuda']:.2f} €"))

        self.treeview.bind("<Double-1>", self.ver_detalle_deuda)

        # Añade el botón "Marcar como pagado"
        self.boton_pagar = tk.Button(self, text="Marcar como pagado", command=self.marcar_como_pagado, state=tk.DISABLED)
        self.boton_pagar.pack(pady=10)
        
        self.treeview.bind('<<TreeviewSelect>>', self.on_treeview_select)

    def actualizar_datos(self):
        """Recarga la lista de deudas desde la base de datos."""
        self.treeview.delete(*self.treeview.get_children())  # Limpia la lista actual
        deudas_agrupadas = obtener_deudas_agrupadas()  # Suponiendo que esta función ya filtra deudas no pagadas.
        for deuda in deudas_agrupadas:
            self.treeview.insert('', tk.END, values=(deuda['socio_id'], deuda['nombre'], f"{deuda['total_deuda']:.2f} €"))


    def ver_detalle_deuda(self, event):
        item_id = self.treeview.selection()[0]
        socio_id = self.treeview.item(item_id, 'values')[0]
        DeudaDetalleDialog(self, socio_id)

    def on_treeview_select(self, event):
        """Habilita el botón de pagar cuando hay una selección."""
        self.boton_pagar['state'] = tk.NORMAL if self.treeview.selection() else tk.DISABLED

    def marcar_como_pagado(self):
        """Lógica para marcar la deuda seleccionada como pagada."""
        item_id = self.treeview.selection()[0]
        socio_id = self.treeview.item(item_id, 'values')[0]
        respuesta = messagebox.askyesno("Confirmar pago", "¿Estás seguro de que deseas marcar la deuda como pagada?")
        if respuesta:
            procesar_pago(socio_id)
            self.actualizar_datos()


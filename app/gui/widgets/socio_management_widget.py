import tkinter as tk
from tkinter import ttk, messagebox
from app.gui.widgets.socio_dialog import abrir_dialogo_socio
from app.logic.socios import actualizar_socio, crear_socio, desactivar_socio, activar_socio, obtener_socio_por_id, obtener_socios

class SocioManagementWidget(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg="#f0f0f0")  # Fondo claro para la modernidad
        self.create_widgets()
        self.listar_socios()

    def create_widgets(self):
        style = ttk.Style()
        style.configure("Treeview", font=('Helvetica', 12), rowheight=25)
        style.configure("Treeview.Heading", font=('Helvetica', 13, 'bold'))
        style.map("TButton", foreground=[('pressed', 'white'), ('active', 'white')],
          background=[('pressed', '!disabled', '#4a69bd'), ('active', '#4a69bd')])

        self.frame_botones = tk.Frame(self, bg='#f0f0f0')
        self.frame_botones.pack(fill=tk.X, padx=10, pady=5)

        self.btn_recargar = ttk.Button(self.frame_botones, text="Recargar Lista", command=self.listar_socios)
        self.btn_recargar.pack(side=tk.LEFT, padx=5)

        self.btn_añadir_socio = ttk.Button(self.frame_botones, text="Añadir Socio", command=self.añadir_socio)        
        self.btn_añadir_socio.pack(side=tk.LEFT, padx=5)

        self.btn_desactivar_socio = ttk.Button(self.frame_botones, text="Desactivar Socio", command=self.desactivar_socio_seleccionado)
        self.btn_desactivar_socio.pack(side=tk.LEFT, padx=5)

        self.btn_activar_socio = ttk.Button(self.frame_botones, text="Activar Socio", command=self.activar_socio_seleccionado)
        self.btn_activar_socio.pack(side=tk.LEFT, padx=5)

        self.lista_socios = ttk.Treeview(self, columns=("ID", "Nombre", "Correo electrónico", "Activo"), show="headings", selectmode="browse")
        for col in self.lista_socios['columns']:
            self.lista_socios.heading(col, text=col)
            self.lista_socios.column(col, anchor=tk.CENTER)
        self.lista_socios.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

    def listar_socios(self):
        for i in self.lista_socios.get_children():
            self.lista_socios.delete(i)
        socios = obtener_socios()
        for socio in socios:
            self.lista_socios.insert("", tk.END, values=(socio.id, socio.nombre, socio.correo_electronico, "Sí" if socio.activo else "No"))

    def añadir_socio(self):
        nombre, correo = abrir_dialogo_socio(self)  # Implementa esta función para abrir un diálogo y obtener los datos
        if nombre and correo:
            crear_socio(nombre, correo)
            self.listar_socios()

    def modificar_socio_seleccionado(self):
        seleccion = self.lista_socios.selection()
        if seleccion:
            item = self.lista_socios.item(seleccion)
            socio_id = item['values'][0]
            socio = obtener_socio_por_id(socio_id)  # Implementa esta función para obtener un socio por su ID
            nombre, correo = abrir_dialogo_socio(self, socio)
            if nombre and correo:
                actualizar_socio(socio_id, nombre, correo)
                self.listar_socios()

    def desactivar_socio_seleccionado(self):
        seleccion = self.lista_socios.selection()
        if seleccion:
            item = self.lista_socios.item(seleccion)
            socio_id = item['values'][0]
            confirmacion = messagebox.askyesno("Desactivar Socio", "¿Estás seguro de que quieres desactivar este socio?")
            if confirmacion:
                desactivar_socio(socio_id)
                self.listar_socios()
    
    def activar_socio_seleccionado(self):
        seleccion = self.lista_socios.selection()
        if seleccion:
            item = self.lista_socios.item(seleccion)
            socio_id = item['values'][0]
            confirmacion = messagebox.askyesno("Activar Socio", "¿Estás seguro de que quieres activar a este socio?")
            if confirmacion:
                activar_socio(socio_id)
                self.listar_socios()

    def actualizar_datos(self):
            """Actualiza la lista de productos mostrada al usuario."""
            self.listar_socios()
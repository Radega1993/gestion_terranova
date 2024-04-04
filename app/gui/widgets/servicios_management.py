import tkinter as tk
from tkinter import messagebox, ttk
from app.database.connection import Session
from app.database.models import Servicio
from app.gui.widgets.servicio_dialog import abrir_dialogo_servicio 

class ServicioManagementWidget(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.configure(bg='#f0f0f0')

        style = ttk.Style()
        style.configure("Treeview", font=('Helvetica', 12), rowheight=25)
        style.configure("Treeview.Heading", font=('Helvetica', 13, 'bold'))

        self.create_widgets()
        self.listar_servicios()

    def create_widgets(self):
        self.frame_botones = tk.Frame(self, bg='#f0f0f0')
        self.frame_botones.pack(fill=tk.X, padx=10, pady=5)

        self.btn_recargar = ttk.Button(self.frame_botones, text="Recargar Lista", command=self.listar_servicios)
        self.btn_recargar.pack(side=tk.LEFT, padx=5)

        self.btn_añadir_servicio = ttk.Button(self.frame_botones, text="Añadir Servicio", command=self.añadir_servicio)
        self.btn_añadir_servicio.pack(side=tk.LEFT, padx=5)

        self.btn_actualizar_servicio = ttk.Button(self.frame_botones, text="Actualizar Servicio", command=self.actualizar_servicio)
        self.btn_actualizar_servicio.pack(side=tk.LEFT, padx=5)

        self.btn_eliminar_servicio = ttk.Button(self.frame_botones, text="Eliminar Servicio", command=self.eliminar_servicio)
        self.btn_eliminar_servicio.pack(side=tk.LEFT, padx=5)

        self.frame_lista = tk.Frame(self)
        self.frame_lista.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        self.scrollbar = ttk.Scrollbar(self.frame_lista)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.lista_servicios = ttk.Treeview(self.frame_lista, columns=("ID", "Nombre", "Precio", "Tipo"), show="headings", yscrollcommand=self.scrollbar.set)
        self.lista_servicios.pack(fill=tk.BOTH, expand=True)

        self.scrollbar.config(command=self.lista_servicios.yview)

        for col in self.lista_servicios['columns']:
            self.lista_servicios.heading(col, text=col)
            self.lista_servicios.column(col, width=120, anchor=tk.CENTER)

    def listar_servicios(self):
        for i in self.lista_servicios.get_children():
            self.lista_servicios.delete(i)
        with Session() as session:
            servicios = session.query(Servicio).filter_by(activo=True).all()
            for servicio in servicios:
                self.lista_servicios.insert('', 'end', values=(servicio.id, servicio.nombre, servicio.precio, servicio.tipo))

    def añadir_servicio(self):
        resultado = abrir_dialogo_servicio(self)  # Ahora retorna nombre, precio y tipo
        if resultado:
            nombre, precio, tipo = resultado
            with Session() as session:
                nuevo_servicio = Servicio(nombre=nombre, precio=precio, tipo=tipo, activo=True)
                session.add(nuevo_servicio)
                session.commit()
            self.listar_servicios()

    def actualizar_servicio(self):
        seleccion = self.lista_servicios.selection()
        if seleccion:
            item = self.lista_servicios.item(seleccion)
            servicio_id = item['values'][0]
            with Session() as session:
                servicio = session.query(Servicio).filter_by(id=servicio_id).first()
                resultado = abrir_dialogo_servicio(self, servicio)  # Pasa el servicio existente
                if resultado:
                    nombre, precio, tipo = resultado
                    servicio.nombre = nombre
                    servicio.precio = precio
                    servicio.tipo = tipo  # Actualiza el tipo
                    session.commit()
            self.listar_servicios()


    def eliminar_servicio(self):
        seleccion = self.lista_servicios.selection()
        if seleccion:
            item = self.lista_servicios.item(seleccion)
            servicio_id = item['values'][0]
            confirmacion = messagebox.askyesno("Eliminar Servicio", "¿Estás seguro de que quieres eliminar este servicio?")
            if confirmacion:
                with Session() as session:
                    servicio = session.query(Servicio).filter_by(id=servicio_id).one()
                    servicio.activo = False
                    session.commit()
                self.listar_servicios()
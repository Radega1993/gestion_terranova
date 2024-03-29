import tkinter as tk
from tkinter import messagebox, ttk, simpledialog
from app.database.connection import Session
from app.gui.widgets.product_dialog import abrir_dialogo_producto
from app.logic.stock import actualizar_stock, obtener_stock_actual  # Asegúrate de que el import es correcto
from app.database.models import Producto

class ProductManagementWidget(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.configure(bg='#f0f0f0')  # Fondo claro para el frame

        style = ttk.Style()
        style.configure("Treeview", font=('Helvetica', 12), rowheight=25)
        style.configure("Treeview.Heading", font=('Helvetica', 13, 'bold'))
        style.map("TButton", foreground=[('pressed', 'white'), ('active', 'white')],
          background=[('pressed', '!disabled', '#4a69bd'), ('active', '#4a69bd')])

        self.create_widgets()
        self.listar_productos()

    def create_widgets(self):
        self.frame_botones = tk.Frame(self, bg='#f0f0f0')
        self.frame_botones.pack(fill=tk.X, padx=10, pady=5)

        self.btn_recargar = ttk.Button(self.frame_botones, text="Recargar Lista", command=self.listar_productos)
        self.btn_recargar.pack(side=tk.LEFT, padx=5)

        self.btn_añadir_producto = ttk.Button(self.frame_botones, text="Añadir Producto", command=self.añadir_producto)
        self.btn_añadir_producto.pack(side=tk.LEFT, padx=5)

        self.btn_actualizar_stock = ttk.Button(self.frame_botones, text="Actualizar Producto", command=self.actualizar_producto)
        self.btn_actualizar_stock.pack(side=tk.LEFT, padx=5)

        self.btn_eliminar_producto = ttk.Button(self.frame_botones, text="Eliminar Producto", command=self.eliminar_producto)
        self.btn_eliminar_producto.pack(side=tk.LEFT, padx=5)

        # Lista de productos con scrollbar
        self.frame_lista = tk.Frame(self)
        self.frame_lista.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        self.scrollbar = ttk.Scrollbar(self.frame_lista)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.lista_productos = ttk.Treeview(self.frame_lista, columns=("ID", "Nombre", "Precio", "Stock"), show="headings", yscrollcommand=self.scrollbar.set)
        self.lista_productos.pack(fill=tk.BOTH, expand=True)

        self.scrollbar.config(command=self.lista_productos.yview)

        # Configuración de las columnas
        for col in self.lista_productos['columns']:
            self.lista_productos.heading(col, text=col)
            self.lista_productos.column(col, width=120, anchor=tk.CENTER)

    def listar_productos(self):
        self.lista_productos.delete(*self.lista_productos.get_children())
        with Session() as session:
            productos = session.query(Producto).filter_by(activo=True).all()
            for producto in productos:
                self.lista_productos.insert('', 'end', values=(producto.id, producto.nombre, producto.precio, producto.stock_actual))


    def añadir_producto(self):
        nombre, precio, stock = abrir_dialogo_producto(self)
        if nombre:
            with Session() as session:
                nuevo_producto = Producto(nombre=nombre, precio=precio, stock_actual=stock, activo=True)
                session.add(nuevo_producto)
                session.commit()
            self.listar_productos()


    def actualizar_producto(self):
        seleccion = self.lista_productos.selection()
        if seleccion:
            item = self.lista_productos.item(seleccion)
            producto_id = item['values'][0]
            with Session() as session:
                producto = session.query(Producto).filter_by(id=producto_id).first()
                nombre, precio, stock = abrir_dialogo_producto(self, producto)
                if nombre:
                    producto.nombre = nombre
                    producto.precio = precio
                    producto.stock_actual = stock
                    session.commit()
            self.listar_productos()

    def actualizar_stock_producto(self):
        seleccion = self.lista_productos.selection()
        if seleccion:
            item = self.lista_productos.item(seleccion)
            producto_id = item['values'][0]
            with Session() as session:
                producto = session.query(Producto).filter_by(id=producto_id).one()
                nombre, precio, stock = abrir_dialogo_producto(self, producto)
                if nombre and precio and stock is not None:
                    producto.nombre = nombre
                    producto.precio = precio
                    producto.stock_actual = stock
                    session.commit()
                    messagebox.showinfo("Producto Actualizado", f"Producto '{nombre}' actualizado con éxito.")
                    self.listar_productos()
        else:
            messagebox.showerror("Error", "Por favor, selecciona un producto de la lista.")

    def eliminar_producto(self):
        seleccion = self.lista_productos.selection()
        if seleccion:
            item = self.lista_productos.item(seleccion)
            producto_id = item['values'][0]
            confirmacion = messagebox.askyesno("Eliminar Producto", "¿Estás seguro de que quieres eliminar este producto?")
            if confirmacion:
                with Session() as session:
                    producto = session.query(Producto).filter_by(id=producto_id).one()
                    producto.activo = False  # Asumiendo que tienes una columna 'activo' en tu modelo
                    session.commit()
                    messagebox.showinfo("Producto Eliminado", f"El producto '{producto.nombre}' ha sido eliminado con éxito.")
                    self.listar_productos()
        else:
            messagebox.showerror("Error", "Por favor, selecciona un producto de la lista.")

    def actualizar_datos(self):
        """Actualiza la lista de productos mostrada al usuario."""
        self.listar_productos()

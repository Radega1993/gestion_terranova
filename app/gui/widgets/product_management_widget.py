import tkinter as tk
from tkinter import messagebox, ttk, simpledialog
from app.database.connection import Session
from app.logic.stock import actualizar_stock, obtener_stock_actual  # Asegúrate de que el import es correcto
from app.database.models import Producto

class ProductManagementWidget(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.create_widgets()
        self.listar_productos()

    def create_widgets(self):
        # Lista de productos
        self.lista_productos = ttk.Treeview(self, columns=("ID", "Nombre", "Precio", "Stock"), show="headings")
        for col in self.lista_productos['columns']:
            self.lista_productos.heading(col, text=col)
        self.lista_productos.pack(fill=tk.BOTH, expand=True)

        # Botón para recargar la lista de productos
        self.btn_recargar = tk.Button(self, text="Recargar Lista", command=self.listar_productos)
        self.btn_recargar.pack(side=tk.TOP, fill=tk.X)

        # Botón para añadir producto
        self.btn_añadir_producto = tk.Button(self, text="Añadir Producto", command=self.añadir_producto)
        self.btn_añadir_producto.pack(side=tk.TOP, fill=tk.X)

        # Botón para actualizar stock
        self.btn_actualizar_stock = tk.Button(self, text="Actualizar Stock", command=self.actualizar_stock_producto)
        self.btn_actualizar_stock.pack(side=tk.TOP, fill=tk.X)

    def listar_productos(self):
        for i in self.lista_productos.get_children():
            self.lista_productos.delete(i)
        with Session() as session:
            productos = session.query(Producto).all()
            for producto in productos:
                self.lista_productos.insert("", tk.END, values=(producto.id, producto.nombre, producto.precio, producto.stock_actual))

    def añadir_producto(self):
        # Crear una ventana simple para añadir un nuevo producto
        nombre = simpledialog.askstring("Nombre del Producto", "Introduce el nombre del producto:")
        precio = simpledialog.askfloat("Precio del Producto", "Introduce el precio del producto:")
        stock = simpledialog.askinteger("Stock del Producto", "Introduce el stock inicial del producto:")
        if nombre and precio and stock is not None:
            with Session() as session:
                nuevo_producto = Producto(nombre=nombre, precio=precio, stock_actual=stock)
                session.add(nuevo_producto)
                session.commit()
                messagebox.showinfo("Producto Añadido", f"Producto '{nombre}' añadido con éxito.")
                self.listar_productos()

    def actualizar_stock_producto(self):
        # Selecciona un producto de la lista para actualizar su stock
        seleccion = self.lista_productos.selection()
        if seleccion:
            item = self.lista_productos.item(seleccion)
            producto_id = item['values'][0]
            nueva_cantidad = simpledialog.askinteger("Actualizar Stock", "Introduce la nueva cantidad de stock:", initialvalue=0)
            if nueva_cantidad is not None:
                actualizar_stock(producto_id, nueva_cantidad - obtener_stock_actual(producto_id))
                messagebox.showinfo("Stock Actualizado", "El stock ha sido actualizado con éxito.")
                self.listar_productos()
        else:
            messagebox.showerror("Error", "Por favor, selecciona un producto de la lista.")

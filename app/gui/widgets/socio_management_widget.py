import tkinter as tk
from tkinter import ttk, messagebox
from app.gui.widgets.socio_dialog import abrir_dialogo_socio
from app.gui.widgets.socio_tree import SocioTree
from app.logic.socios import (actualizar_socio, crear_socio, desactivar_socio, 
                            activar_socio, obtener_socio_por_id, obtener_socios,
                            obtener_socios_principales, obtener_miembros_familia)
from app.logic.photo_handler import get_photo_path
from PIL import Image, ImageTk
import os
from app.database.connection import Session
from app.database.models import Socio, Usuario
from app.logic.EstadoApp import EstadoApp

class SocioManagementWidget(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg="#f0f0f0")
        self.setup_ui()

    def setup_ui(self):
        # Crear el frame principal
        main_frame = ttk.Frame(self)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Crear el SocioTree
        with Session() as session:
            tipo_usuario = session.query(Usuario).get(EstadoApp.get_usuario_logueado_id()).tipo_usuario
            self.socio_tree = SocioTree(main_frame, session, tipo_usuario)
            self.socio_tree.pack(fill=tk.BOTH, expand=True)

        # Frame inferior para detalles
        self.details_frame = ttk.LabelFrame(main_frame, text="Detalles del Socio")
        self.details_frame.pack(fill=tk.X, pady=(10, 0))

        # Inicializar variables para detalles
        self.detalles_vars = {
            "codigo": tk.StringVar(),
            "nombre": tk.StringVar(),
            "apellidos": tk.StringVar(),
            "dni": tk.StringVar(),
            "telefono": tk.StringVar(),
            "email": tk.StringVar(),
            "direccion": tk.StringVar(),
            "poblacion": tk.StringVar(),
            "codigo_postal": tk.StringVar(),
            "provincia": tk.StringVar(),
            "estado": tk.StringVar()
        }

        # Crear grid de detalles
        row = 0
        col = 0
        for key, var in self.detalles_vars.items():
            ttk.Label(self.details_frame, text=key.title() + ":").grid(row=row, column=col*2, padx=5, pady=2, sticky=tk.E)
            ttk.Label(self.details_frame, textvariable=var).grid(row=row, column=col*2+1, padx=5, pady=2, sticky=tk.W)
            col += 1
            if col > 2:
                col = 0
                row += 1

        # Bind para selección en el nuevo árbol
        self.socio_tree.tree.bind("<<TreeviewSelect>>", self.on_select)

    def on_select(self, event):
        """Maneja la selección de un socio en el Treeview"""
        selection = self.socio_tree.tree.selection()
        if not selection:
            return
        
        # Obtener el ID del socio seleccionado
        socio_id = int(self.socio_tree.tree.item(selection[0], "tags")[0])

        # Cargar detalles del socio
        with Session() as session:
            socio = session.query(Socio).get(socio_id)
            if socio:
                # Actualizar variables de detalles
                self.detalles_vars["codigo"].set(socio.codigo_socio)
                self.detalles_vars["nombre"].set(socio.nombre)
                self.detalles_vars["apellidos"].set(
                    f"{socio.primer_apellido} {socio.segundo_apellido or ''}"
                )
                self.detalles_vars["dni"].set(socio.dni or "")
                self.detalles_vars["telefono"].set(socio.telefono or "")
                self.detalles_vars["email"].set(socio.email or "")
                self.detalles_vars["direccion"].set(socio.direccion or "")
                self.detalles_vars["poblacion"].set(socio.poblacion or "")
                self.detalles_vars["codigo_postal"].set(socio.codigo_postal or "")
                self.detalles_vars["provincia"].set(socio.provincia or "")
                self.detalles_vars["estado"].set(
                    "Activo" if socio.activo else "Inactivo"
                )

    def añadir_socio(self):
        socios_principales = obtener_socios_principales()
        datos = abrir_dialogo_socio(self, socios_principales=socios_principales)
        if datos:
            crear_socio(**datos)
            self.socio_tree.actualizar_arbol()

    def modificar_socio_seleccionado(self):
        selection = self.socio_tree.tree.selection()
        if not selection:
            messagebox.showwarning("Advertencia", "Por favor, seleccione un socio para modificar")
            return
            
        socio_id = int(self.socio_tree.tree.item(selection[0], "tags")[0])
        with Session() as session:
            socio = session.query(Socio).get(socio_id)
            if socio:
                socios_principales = obtener_socios_principales()
                socio_actualizado = abrir_dialogo_socio(self, socio, socios_principales)
                if socio_actualizado:
                    # Convertir el objeto Socio a un diccionario con sus atributos
                    datos_socio = {
                        'nombre': socio_actualizado.nombre,
                        'primer_apellido': socio_actualizado.primer_apellido,
                        'segundo_apellido': socio_actualizado.segundo_apellido,
                        'dni': socio_actualizado.dni,
                        'fecha_nacimiento': socio_actualizado.fecha_nacimiento,
                        'telefono': socio_actualizado.telefono,
                        'email': socio_actualizado.email,
                        'es_principal': socio_actualizado.es_principal,
                        'foto_path': socio_actualizado.foto_path,
                        'direccion': socio_actualizado.direccion,
                        'codigo_postal': socio_actualizado.codigo_postal,
                        'poblacion': socio_actualizado.poblacion,
                        'provincia': socio_actualizado.provincia,
                        'telefono2': socio_actualizado.telefono2,
                        'email2': socio_actualizado.email2,
                        'num_pers': socio_actualizado.num_pers,
                        'adherits': socio_actualizado.adherits,
                        'menor_3_anys': socio_actualizado.menor_3_anys,
                        'cuota': socio_actualizado.cuota,
                        'iban': socio_actualizado.iban,
                        'entidad': socio_actualizado.entidad,
                        'oficina': socio_actualizado.oficina,
                        'dc': socio_actualizado.dc,
                        'cuenta_corriente': socio_actualizado.cuenta_corriente,
                        'rgpd': socio_actualizado.rgpd,
                        'socio_principal_id': socio_actualizado.socio_principal_id,
                        'codigo_socio': socio_actualizado.codigo_socio
                    }
                    actualizar_socio(socio_id, **datos_socio)
                    self.socio_tree.actualizar_arbol()
                    messagebox.showinfo("Éxito", "Socio actualizado correctamente")

    def desactivar_socio_seleccionado(self):
        selection = self.socio_tree.tree.selection()
        if not selection:
            messagebox.showwarning("Advertencia", "Por favor, seleccione un socio para desactivar")
            return
            
        socio_id = int(self.socio_tree.tree.item(selection[0], "tags")[0])
        with Session() as session:
            socio = session.query(Socio).get(socio_id)
            if socio:
                confirmacion = messagebox.askyesno("Desactivar Socio", 
                    "¿Estás seguro de que quieres desactivar este socio?\n\n" +
                    "Si es un socio principal, también se desactivarán todos sus miembros de familia.")
            if confirmacion:
                    if desactivar_socio(socio_id):
                        messagebox.showinfo("Éxito", "Socio desactivado correctamente")
                        self.socio_tree.actualizar_arbol()
    
    def activar_socio_seleccionado(self):
        selection = self.socio_tree.tree.selection()
        if not selection:
            messagebox.showwarning("Advertencia", "Por favor, seleccione un socio para activar")
            return
            
        socio_id = int(self.socio_tree.tree.item(selection[0], "tags")[0])
        with Session() as session:
            socio = session.query(Socio).get(socio_id)
            if socio:
                confirmacion = messagebox.askyesno("Activar Socio", 
                    "¿Estás seguro de que quieres activar este socio?")
        if confirmacion:
                    if activar_socio(socio_id):
                        messagebox.showinfo("Éxito", "Socio activado correctamente")
                        self.socio_tree.actualizar_arbol()

    def mostrar_detalles_familia(self, event):
        """Muestra los detalles de la familia al hacer doble clic en un socio principal"""
        selection = self.socio_tree.tree.selection()
        if not selection:
            return

        # Obtener el ID del socio seleccionado
        socio_id = int(self.socio_tree.tree.item(selection[0], "tags")[0])

        # Verificar si es un socio principal
        with Session() as session:
            socio = session.query(Socio).get(socio_id)
            if not socio or not socio.es_principal:
                return

            # Crear ventana de detalles
            detalles_window = tk.Toplevel(self)
            detalles_window.title(f"Detalles de la Familia - {socio.nombre}")
            detalles_window.geometry("800x600")
            detalles_window.transient(self)

            # Frame principal con scrollbar
            scrollable_frame = ttk.Frame(detalles_window)
            scrollable_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

            # Frame para el socio principal
            principal_frame = ttk.LabelFrame(scrollable_frame, text="Socio Principal")
            principal_frame.pack(fill=tk.X, pady=5, padx=5)

            # Mostrar foto del socio principal si existe
        if socio.foto_path:
            try:
                    image = Image.open(socio.foto_path)
                    image = image.resize((150, 150), Image.Resampling.LANCZOS)
                    photo = ImageTk.PhotoImage(image)
                    label = ttk.Label(principal_frame, image=photo)
                    label.image = photo
                    label.pack(pady=5)
            except Exception as e:
                print(f"Error al cargar la imagen: {e}")

            # Mostrar información del socio principal
            info_text = f"""
            Nombre: {socio.nombre} {socio.primer_apellido} {socio.segundo_apellido or ''}
            DNI: {socio.dni or 'No especificado'}
            Teléfono: {socio.telefono or 'No especificado'}
            Email: {socio.email or 'No especificado'}
            Dirección: {socio.direccion or 'No especificada'}
            """
            ttk.Label(principal_frame, text=info_text, justify=tk.LEFT).pack(pady=5)

            # Frame para los miembros de la familia
            familia_frame = ttk.LabelFrame(scrollable_frame, text="Miembros de la Familia")
            familia_frame.pack(fill=tk.X, pady=5, padx=5)

            # Obtener miembros de la familia
            miembros = session.query(Socio).filter(
                Socio.socio_principal_id == socio.id
            ).all()

            if not miembros:
                ttk.Label(familia_frame, text="No hay miembros familiares registrados", padding=10).pack()
        else:
                for miembro in miembros:
                    miembro_frame = ttk.LabelFrame(familia_frame, text=f"Miembro: {miembro.codigo_socio}")
                    miembro_frame.pack(fill=tk.X, padx=5, pady=5)

                    # Frame para foto y datos del miembro
                    datos_miembro_frame = ttk.Frame(miembro_frame)
                    datos_miembro_frame.pack(fill=tk.X, padx=5, pady=5)

                    # Mostrar foto del miembro si existe
                    if miembro.foto_path:
                        try:
                            image = Image.open(miembro.foto_path)
                            image = image.resize((100, 100), Image.Resampling.LANCZOS)
                            photo = ImageTk.PhotoImage(image)
                            label = ttk.Label(datos_miembro_frame, image=photo)
                            label.image = photo
                            label.pack(side=tk.LEFT, padx=5)
                        except Exception as e:
                            print(f"Error al cargar la imagen: {e}")

                    # Mostrar información del miembro
                    miembro_info = f"""
                    Nombre: {miembro.nombre} {miembro.primer_apellido} {miembro.segundo_apellido or ''}
                    DNI: {miembro.dni or 'No especificado'}
                    Teléfono: {miembro.telefono or 'No especificado'}
                    Email: {miembro.email or 'No especificado'}
                    """
                    ttk.Label(datos_miembro_frame, text=miembro_info, justify=tk.LEFT).pack(side=tk.LEFT, padx=5)
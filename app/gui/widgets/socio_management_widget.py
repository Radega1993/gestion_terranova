import tkinter as tk
from tkinter import ttk, messagebox
from app.gui.widgets.socio_dialog import abrir_dialogo_socio
from app.logic.socios import (actualizar_socio, crear_socio, desactivar_socio, 
                            activar_socio, obtener_socio_por_id, obtener_socios,
                            obtener_socios_principales, obtener_miembros_familia)
from app.logic.photo_handler import get_photo_path
from PIL import Image, ImageTk
import os

class SocioManagementWidget(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg="#f0f0f0")
        self.create_widgets()
        self.listar_socios()
        self.selected_socio = None

    def create_widgets(self):
        # Frame principal con dos paneles
        self.paned_window = ttk.PanedWindow(self, orient=tk.HORIZONTAL)
        self.paned_window.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Panel izquierdo para la lista de socios
        left_frame = ttk.Frame(self.paned_window)
        self.paned_window.add(left_frame, weight=1)
        
        # Panel derecho para detalles
        right_frame = ttk.Frame(self.paned_window)
        self.paned_window.add(right_frame, weight=2)
        
        # Botones en el panel izquierdo
        self.frame_botones = ttk.Frame(left_frame)
        self.frame_botones.pack(fill=tk.X, padx=5, pady=5)

        self.btn_recargar = ttk.Button(self.frame_botones, text="Recargar", command=self.listar_socios)
        self.btn_recargar.pack(side=tk.LEFT, padx=2)

        self.btn_añadir_socio = ttk.Button(self.frame_botones, text="Añadir Socio", command=self.añadir_socio)        
        self.btn_añadir_socio.pack(side=tk.LEFT, padx=2)

        self.btn_modificar_socio = ttk.Button(self.frame_botones, text="Modificar", command=self.modificar_socio_seleccionado)
        self.btn_modificar_socio.pack(side=tk.LEFT, padx=2)

        self.btn_desactivar_socio = ttk.Button(self.frame_botones, text="Desactivar", command=self.desactivar_socio_seleccionado)
        self.btn_desactivar_socio.pack(side=tk.LEFT, padx=2)

        self.btn_activar_socio = ttk.Button(self.frame_botones, text="Activar", command=self.activar_socio_seleccionado)
        self.btn_activar_socio.pack(side=tk.LEFT, padx=2)

        # Treeview para socios principales
        self.lista_socios = ttk.Treeview(left_frame, columns=(
            "ID", "Código", "Nombre", "DNI", "Activo"
        ), show="tree headings", selectmode="browse")
        
        # Configurar las columnas
        self.lista_socios.heading("ID", text="ID")
        self.lista_socios.heading("Código", text="Código")
        self.lista_socios.heading("Nombre", text="Nombre")
        self.lista_socios.heading("DNI", text="DNI")
        self.lista_socios.heading("Activo", text="Activo")
        
        # Ajustar el ancho de las columnas
        self.lista_socios.column("ID", width=50)
        self.lista_socios.column("Código", width=80)
        self.lista_socios.column("Nombre", width=200)
        self.lista_socios.column("DNI", width=100)
        self.lista_socios.column("Activo", width=70)
        
        self.lista_socios.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Bind para selección
        self.lista_socios.bind('<<TreeviewSelect>>', self.on_socio_select)
        
        # Panel derecho para detalles
        self.detalles_frame = ttk.LabelFrame(right_frame, text="Detalles del Socio")
        self.detalles_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Frame para la foto
        self.foto_frame = ttk.Frame(self.detalles_frame)
        self.foto_frame.pack(fill=tk.X, padx=10, pady=10)
        
        self.foto_label = ttk.Label(self.foto_frame)
        self.foto_label.pack()
        
        # Frame para información
        self.info_frame = ttk.Frame(self.detalles_frame)
        self.info_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Labels para información básica
        self.rgpd_label = ttk.Label(self.info_frame, text="RGPD: ")
        self.rgpd_label.pack(anchor=tk.W)
        
        self.codigo_label = ttk.Label(self.info_frame, text="Código: ")
        self.codigo_label.pack(anchor=tk.W)
        
        self.dni_label = ttk.Label(self.info_frame, text="DNI: ")
        self.dni_label.pack(anchor=tk.W)
        
        self.nombre_completo_label = ttk.Label(self.info_frame, text="Nombre Completo: ")
        self.nombre_completo_label.pack(anchor=tk.W)
        
        self.fecha_nacimiento_label = ttk.Label(self.info_frame, text="Fecha Nacimiento: ")
        self.fecha_nacimiento_label.pack(anchor=tk.W)
        
        self.cuota_label = ttk.Label(self.info_frame, text="Cuota: ")
        self.cuota_label.pack(anchor=tk.W)
        
        # Labels para información de contacto
        self.direccion_label = ttk.Label(self.info_frame, text="Dirección: ")
        self.direccion_label.pack(anchor=tk.W)
        
        self.poblacion_label = ttk.Label(self.info_frame, text="Población: ")
        self.poblacion_label.pack(anchor=tk.W)
        
        self.telefonos_label = ttk.Label(self.info_frame, text="Teléfonos: ")
        self.telefonos_label.pack(anchor=tk.W)
        
        self.emails_label = ttk.Label(self.info_frame, text="Emails: ")
        self.emails_label.pack(anchor=tk.W)
        
        # Labels para información bancaria
        self.cuenta_label = ttk.Label(self.info_frame, text="Cuenta Bancaria: ")
        self.cuenta_label.pack(anchor=tk.W)
        
        # Labels para información familiar
        self.tipo_label = ttk.Label(self.info_frame, text="Tipo: ")
        self.tipo_label.pack(anchor=tk.W)
        
        self.num_pers_label = ttk.Label(self.info_frame, text="Número de Personas: ")
        self.num_pers_label.pack(anchor=tk.W)
        
        self.adheridos_label = ttk.Label(self.info_frame, text="Adheridos: ")
        self.adheridos_label.pack(anchor=tk.W)
        
        self.menores_label = ttk.Label(self.info_frame, text="Menores de 3 años: ")
        self.menores_label.pack(anchor=tk.W)
        
        self.estado_label = ttk.Label(self.info_frame, text="Estado: ")
        self.estado_label.pack(anchor=tk.W)
        
        # Frame para miembros de familia (si es socio principal)
        self.miembros_frame = ttk.LabelFrame(self.detalles_frame, text="Miembros de la Familia")
        self.miembros_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        self.miembros_tree = ttk.Treeview(self.miembros_frame, columns=(
            "ID", "Código", "Nombre", "DNI", "Activo"
        ), show="headings", selectmode="browse")
        
        self.miembros_tree.heading("ID", text="ID")
        self.miembros_tree.heading("Código", text="Código")
        self.miembros_tree.heading("Nombre", text="Nombre")
        self.miembros_tree.heading("DNI", text="DNI")
        self.miembros_tree.heading("Activo", text="Activo")
        
        self.miembros_tree.column("ID", width=50)
        self.miembros_tree.column("Código", width=80)
        self.miembros_tree.column("Nombre", width=200)
        self.miembros_tree.column("DNI", width=100)
        self.miembros_tree.column("Activo", width=70)
        
        self.miembros_tree.pack(fill=tk.BOTH, expand=True)

    def listar_socios(self):
        # Limpiar el árbol
        for item in self.lista_socios.get_children():
            self.lista_socios.delete(item)
            
        # Obtener socios principales
        socios_principales = obtener_socios_principales()
        
        
        # Insertar socios principales
        for socio in socios_principales:
            
            # Insertar socio principal
            principal_id = self.lista_socios.insert("", tk.END, values=(
                socio.id,
                socio.codigo_socio,
                f"{socio.nombre} {socio.primer_apellido} {socio.segundo_apellido}".strip(),
                socio.dni,
                "Sí" if socio.activo else "No"
            ), tags=('principal',))
            
            # Obtener y insertar miembros de la familia
            miembros = obtener_miembros_familia(socio.id)
            for miembro in miembros:
                self.lista_socios.insert(principal_id, tk.END, values=(
                    miembro.id,
                    miembro.codigo_socio,
                    f"{miembro.nombre} {miembro.primer_apellido} {miembro.segundo_apellido}".strip(),
                    miembro.dni,
                    "Sí" if miembro.activo else "No"
                ), tags=('miembro',))
        
        # Configurar estilos para diferenciar principales y miembros
        self.lista_socios.tag_configure('principal', font=('TkDefaultFont', 10, 'bold'))
        self.lista_socios.tag_configure('miembro', font=('TkDefaultFont', 9))
        
        # Expandir todos los elementos para mostrar la jerarquía completa
        for item in self.lista_socios.get_children():
            self.lista_socios.item(item, open=True)

    def on_socio_select(self, event):
        # Obtener el item seleccionado
        selected_items = self.lista_socios.selection()
        if not selected_items:
            return
        
        item_id = selected_items[0]
        socio_id = self.lista_socios.item(item_id)['values'][0]
        
        # Obtener el socio seleccionado
        self.selected_socio = obtener_socio_por_id(socio_id)
        if not self.selected_socio:
            return
        
        # Actualizar la foto
        self.actualizar_foto()
        
        # Actualizar información básica
        self.rgpd_label.config(text=f"RGPD: {'Sí' if self.selected_socio.rgpd else 'No'}")
        self.codigo_label.config(text=f"Código: {self.selected_socio.codigo_socio}")
        self.dni_label.config(text=f"DNI: {self.selected_socio.dni}")
        self.nombre_completo_label.config(text=f"Nombre Completo: {self.selected_socio.nombre} {self.selected_socio.primer_apellido} {self.selected_socio.segundo_apellido}")
        self.fecha_nacimiento_label.config(text=f"Fecha Nacimiento: {self.selected_socio.fecha_nacimiento}")
        self.cuota_label.config(text=f"Cuota: {self.selected_socio.cuota}€")
        
        # Actualizar información de contacto
        self.direccion_label.config(text=f"Dirección: {self.selected_socio.direccion}")
        self.poblacion_label.config(text=f"Población: {self.selected_socio.poblacion} ({self.selected_socio.codigo_postal})")
        self.telefonos_label.config(text=f"Teléfonos: {self.selected_socio.telefono} / {self.selected_socio.telefono2}")
        self.emails_label.config(text=f"Emails: {self.selected_socio.email} / {self.selected_socio.email2}")
        
        # Actualizar información bancaria
        cuenta = f"{self.selected_socio.iban}-{self.selected_socio.entidad}-{self.selected_socio.oficina}-{self.selected_socio.dc}-{self.selected_socio.cuenta_corriente}"
        self.cuenta_label.config(text=f"Cuenta Bancaria: {cuenta}")
        
        # Actualizar información familiar
        tipo = "Principal" if self.selected_socio.es_principal else "Miembro"
        self.tipo_label.config(text=f"Tipo: {tipo}")
        self.num_pers_label.config(text=f"Número de Personas: {self.selected_socio.num_pers}")
        self.adheridos_label.config(text=f"Adheridos: {self.selected_socio.adherits}")
        self.menores_label.config(text=f"Menores de 3 años: {self.selected_socio.menor_3_anys}")
        self.estado_label.config(text=f"Estado: {'Activo' if self.selected_socio.activo else 'Inactivo'}")
        
        # Actualizar lista de miembros si es socio principal
        self.actualizar_lista_miembros()

    def actualizar_foto(self):
        if not self.selected_socio:
            return
        
        # Limpiar foto actual
        self.foto_label.config(image='')
        
        # Si el socio tiene foto, mostrarla
        if self.selected_socio.foto_path:
            try:
                photo_path = get_photo_path(self.selected_socio.foto_path)
                if os.path.exists(photo_path):
                    # Cargar y redimensionar la imagen
                    image = Image.open(photo_path)
                    image.thumbnail((200, 200))  # Redimensionar manteniendo proporción
                    photo = ImageTk.PhotoImage(image)
                    
                    # Mostrar la imagen
                    self.foto_label.config(image=photo)
                    self.foto_label.image = photo  # Mantener referencia
            except Exception as e:
                print(f"Error al cargar la foto: {e}")

    def actualizar_lista_miembros(self):
        # Limpiar la lista de miembros
        for item in self.miembros_tree.get_children():
            self.miembros_tree.delete(item)
        
        if not self.selected_socio or not self.selected_socio.es_principal:
            self.miembros_frame.pack_forget()
            return
        
        # Mostrar el frame de miembros
        self.miembros_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Obtener y mostrar los miembros
        miembros = obtener_miembros_familia(self.selected_socio.id)
        for miembro in miembros:
            self.miembros_tree.insert("", tk.END, values=(
                miembro.id,
                miembro.codigo_socio,
                f"{miembro.nombre} {miembro.primer_apellido} {miembro.segundo_apellido}".strip(),
                miembro.dni,
                "Sí" if miembro.activo else "No"
            ))

    def añadir_socio(self):
        socios_principales = obtener_socios_principales()
        datos = abrir_dialogo_socio(self, socios_principales=socios_principales)
        if datos:
            crear_socio(**datos)
            self.listar_socios()

    def modificar_socio_seleccionado(self):
        if not self.selected_socio:
            messagebox.showwarning("Advertencia", "Por favor, seleccione un socio para modificar")
            return
            
        socios_principales = obtener_socios_principales()
        datos = abrir_dialogo_socio(self, self.selected_socio, socios_principales)
        if datos:
            actualizar_socio(self.selected_socio.id, **datos)
            self.listar_socios()
            self.mostrar_detalles_socio(obtener_socio_por_id(self.selected_socio.id))

    def desactivar_socio_seleccionado(self):
        if not self.selected_socio:
            messagebox.showwarning("Advertencia", "Por favor, seleccione un socio para desactivar")
            return
            
        confirmacion = messagebox.askyesno("Desactivar Socio", "¿Estás seguro de que quieres desactivar este socio?")
        if confirmacion:
            desactivar_socio(self.selected_socio.id)
            self.listar_socios()

    def activar_socio_seleccionado(self):
        if not self.selected_socio:
            messagebox.showwarning("Advertencia", "Por favor, seleccione un socio para activar")
            return
            
        confirmacion = messagebox.askyesno("Activar Socio", "¿Estás seguro de que quieres activar este socio?")
        if confirmacion:
            try:
                activar_socio(self.selected_socio.id)
                self.listar_socios()
            except ValueError as e:
                messagebox.showerror("Error", str(e))

    def mostrar_detalles_socio(self, socio):
        # Actualizar información básica
        self.rgpd_label.config(text=f"RGPD: {'Sí' if socio.rgpd else 'No'}")
        self.codigo_label.config(text=f"Código: {socio.codigo_socio or ''}")
        self.dni_label.config(text=f"DNI: {socio.dni or ''}")
        
        nombre_completo = f"{socio.nombre or ''} {socio.primer_apellido or ''} {socio.segundo_apellido or ''}".strip()
        self.nombre_completo_label.config(text=f"Nombre Completo: {nombre_completo}")
        
        fecha_nacimiento = socio.fecha_nacimiento.strftime("%d/%m/%Y") if socio.fecha_nacimiento else ''
        self.fecha_nacimiento_label.config(text=f"Fecha Nacimiento: {fecha_nacimiento}")
        
        self.cuota_label.config(text=f"Cuota: {socio.cuota or 0:.2f} €")
        
        # Actualizar información de contacto
        direccion = f"{socio.direccion or ''}, {socio.codigo_postal or ''} {socio.poblacion or ''} ({socio.provincia or ''})".strip()
        self.direccion_label.config(text=f"Dirección: {direccion}")
        
        telefonos = f"{socio.telefono or ''} / {socio.telefono2 or ''}".strip(" /")
        self.telefonos_label.config(text=f"Teléfonos: {telefonos}")
        
        emails = f"{socio.email or ''} / {socio.email2 or ''}".strip(" /")
        self.emails_label.config(text=f"Emails: {emails}")
        
        # Actualizar información bancaria
        cuenta = f"IBAN: {socio.iban or ''} {socio.entidad or ''} {socio.oficina or ''} {socio.dc or ''} {socio.cuenta_corriente or ''}".strip()
        self.cuenta_label.config(text=f"Cuenta Bancaria: {cuenta}")
        
        # Actualizar información familiar
        self.tipo_label.config(text=f"Tipo: {'Principal' if socio.es_principal else 'Miembro'}")
        self.num_pers_label.config(text=f"Número de Personas: {socio.num_pers or 0}")
        self.adheridos_label.config(text=f"Adheridos: {socio.adherits or 0}")
        self.menores_label.config(text=f"Menores de 3 años: {socio.menor_3_anys or 0}")
        self.estado_label.config(text=f"Estado: {'Activo' if socio.activo else 'Inactivo'}")
        
        # Mostrar foto si existe
        if socio.foto_path:
            try:
                photo_path = get_photo_path(socio.foto_path)
                if os.path.exists(photo_path):
                    image = Image.open(photo_path)
                    image.thumbnail((200, 200))
                    photo = ImageTk.PhotoImage(image)
                    self.foto_label.configure(image=photo)
                    self.foto_label.image = photo
                else:
                    self.foto_label.configure(image='')
            except Exception as e:
                print(f"Error al cargar la imagen: {e}")
                self.foto_label.configure(image='')
        else:
            self.foto_label.configure(image='')
        
        # Mostrar miembros de familia si es socio principal
        if socio.es_principal:
            self.miembros_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
            self.actualizar_lista_miembros()
        else:
            self.miembros_frame.pack_forget()

    def actualizar_datos(self):
        """Actualiza la lista de socios mostrada al usuario."""
        self.listar_socios()
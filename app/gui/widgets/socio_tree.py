import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from app.database.connection import Session
from app.database.models import Socio
from app.gui.widgets.socio_dialog import abrir_dialogo_socio
from app.logic.socios import (actualizar_socio, crear_socio, desactivar_socio, 
                            activar_socio, obtener_socio_por_id, obtener_socios,
                            obtener_socios_principales, obtener_miembros_familia)
import pandas as pd
from datetime import datetime

class SocioTree(ttk.Frame):
    def __init__(self, parent, session, tipo_usuario):
        super().__init__(parent)
        self.session = session
        self.tipo_usuario = tipo_usuario
        
        # Barra de herramientas
        toolbar = ttk.Frame(self)
        toolbar.pack(fill=tk.X, padx=5, pady=5)
        
        # Botones según tipo de usuario
        if tipo_usuario == 'Trabajador':
            ttk.Button(toolbar, text="Nuevo Socio", command=self.nuevo_socio).pack(side=tk.LEFT, padx=2)
        elif tipo_usuario == 'Junta':
            ttk.Button(toolbar, text="Nuevo Socio", command=self.nuevo_socio).pack(side=tk.LEFT, padx=2)
            ttk.Button(toolbar, text="Editar", command=self.editar_socio).pack(side=tk.LEFT, padx=2)
            ttk.Button(toolbar, text="Activar", command=self.activar_socio).pack(side=tk.LEFT, padx=2)
            ttk.Button(toolbar, text="Desactivar", command=self.desactivar_socio).pack(side=tk.LEFT, padx=2)
        elif tipo_usuario == 'Administrador':
            ttk.Button(toolbar, text="Nuevo Socio", command=self.nuevo_socio).pack(side=tk.LEFT, padx=2)
            ttk.Button(toolbar, text="Editar", command=self.editar_socio).pack(side=tk.LEFT, padx=2)
            ttk.Button(toolbar, text="Activar", command=self.activar_socio).pack(side=tk.LEFT, padx=2)
            ttk.Button(toolbar, text="Desactivar", command=self.desactivar_socio).pack(side=tk.LEFT, padx=2)
            ttk.Button(toolbar, text="Importar Excel", command=self.importar_excel).pack(side=tk.LEFT, padx=2)
            ttk.Button(toolbar, text="Exportar Excel", command=self.exportar_excel).pack(side=tk.LEFT, padx=2)
        
        # Árbol de socios
        self.tree = ttk.Treeview(self, columns=("codigo", "nombre", "dni", "telefono", "email"), show="tree headings")
        self.tree.heading("#0", text="Socios")
        self.tree.heading("codigo", text="Código")
        self.tree.heading("nombre", text="Nombre")
        self.tree.heading("dni", text="DNI")
        self.tree.heading("telefono", text="Teléfono")
        self.tree.heading("email", text="Email")
        
        # Configurar evento de doble clic
        self.tree.bind("<Double-1>", self.on_double_click)
        
        self.tree.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.actualizar_arbol()
        
    def on_double_click(self, event):
        """Maneja el evento de doble clic en un socio"""
        item = self.tree.selection()[0]
        socio_id = int(self.tree.item(item, "tags")[0])
        
        # Obtener el socio
        socio = self.session.query(Socio).get(socio_id)
        if socio:
            # Si es un miembro de familia, obtener el socio principal
            if socio.socio_principal_id:
                socio_principal = self.session.query(Socio).get(socio.socio_principal_id)
                if socio_principal:
                    # Mostrar información del socio principal y sus miembros
                    self.mostrar_informacion_socio(socio_principal)
            else:
                # Mostrar información del socio principal y sus miembros
                self.mostrar_informacion_socio(socio)
                
    def mostrar_informacion_socio(self, socio_principal):
        """Muestra la información detallada del socio principal y sus miembros"""
        # Crear ventana de información
        info_window = tk.Toplevel(self)
        info_window.title(f"Información de {socio_principal.nombre}")
        info_window.geometry("800x600")
        
        # Frame principal
        main_frame = ttk.Frame(info_window)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Frame para el socio principal
        principal_frame = ttk.LabelFrame(main_frame, text="Socio Principal")
        principal_frame.pack(fill=tk.X, pady=5)
        
        # Mostrar foto del socio principal si existe
        if socio_principal.foto_path:
            try:
                from PIL import Image, ImageTk
                image = Image.open(socio_principal.foto_path)
                image = image.resize((150, 150), Image.Resampling.LANCZOS)
                photo = ImageTk.PhotoImage(image)
                label = ttk.Label(principal_frame, image=photo)
                label.image = photo
                label.pack(pady=5)
            except Exception as e:
                print(f"Error al cargar la imagen: {e}")
        
        # Mostrar información del socio principal según tipo de usuario
        if self.tipo_usuario == 'Trabajador':
            info_text = f"""
            Código Socio: {socio_principal.codigo_socio}
            Nombre: {socio_principal.nombre} {socio_principal.primer_apellido} {socio_principal.segundo_apellido or ''}
            Fecha Nacimiento: {socio_principal.fecha_nacimiento.strftime("%d/%m/%Y") if socio_principal.fecha_nacimiento else "No especificada"}
            Teléfono: {socio_principal.telefono or 'No especificado'}
            """
        else:  # Junta o Administrador
            info_text = f"""
            Código Socio: {socio_principal.codigo_socio}
            Nombre: {socio_principal.nombre} {socio_principal.primer_apellido} {socio_principal.segundo_apellido or ''}
            DNI: {socio_principal.dni or 'No especificado'}
            Fecha Nacimiento: {socio_principal.fecha_nacimiento.strftime("%d/%m/%Y") if socio_principal.fecha_nacimiento else "No especificada"}
            Teléfono: {socio_principal.telefono or 'No especificado'}
            Email: {socio_principal.email or 'No especificado'}
            Dirección: {socio_principal.direccion or 'No especificada'}
            Población: {socio_principal.poblacion or 'No especificada'}
            Código Postal: {socio_principal.codigo_postal or 'No especificado'}
            Provincia: {socio_principal.provincia or 'No especificada'}
            IBAN: {socio_principal.iban or 'No especificado'}
            """
        ttk.Label(principal_frame, text=info_text, justify=tk.LEFT).pack(pady=5)
        
        # Frame para los miembros de la familia
        family_frame = ttk.LabelFrame(main_frame, text="Miembros de la Familia")
        family_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # Obtener miembros de la familia
        miembros = self.session.query(Socio).filter(
            Socio.socio_principal_id == socio_principal.id
        ).all()
        
        # Mostrar información de cada miembro
        for miembro in miembros:
            member_frame = ttk.Frame(family_frame)
            member_frame.pack(fill=tk.X, pady=2)
            
            # Mostrar foto del miembro si existe
            if miembro.foto_path:
                try:
                    from PIL import Image, ImageTk
                    image = Image.open(miembro.foto_path)
                    image = image.resize((100, 100), Image.Resampling.LANCZOS)
                    photo = ImageTk.PhotoImage(image)
                    label = ttk.Label(member_frame, image=photo)
                    label.image = photo
                    label.pack(side=tk.LEFT, padx=5)
                except Exception as e:
                    print(f"Error al cargar la imagen: {e}")
            
            # Mostrar información del miembro según tipo de usuario
            if self.tipo_usuario == 'Trabajador':
                member_info = f"""
                Código Socio: {miembro.codigo_socio}
                Nombre: {miembro.nombre} {miembro.primer_apellido} {miembro.segundo_apellido or ''}
                Fecha Nacimiento: {miembro.fecha_nacimiento.strftime("%d/%m/%Y") if miembro.fecha_nacimiento else "No especificada"}
                Teléfono: {miembro.telefono or 'No especificado'}
                """
            else:  # Junta o Administrador
                member_info = f"""
                Código Socio: {miembro.codigo_socio}
                Nombre: {miembro.nombre} {miembro.primer_apellido} {miembro.segundo_apellido or ''}
                DNI: {miembro.dni or 'No especificado'}
                Fecha Nacimiento: {miembro.fecha_nacimiento.strftime("%d/%m/%Y") if miembro.fecha_nacimiento else "No especificada"}
                Teléfono: {miembro.telefono or 'No especificado'}
                Email: {miembro.email or 'No especificado'}
                Dirección: {miembro.direccion or 'No especificada'}
                """
            ttk.Label(member_frame, text=member_info, justify=tk.LEFT).pack(side=tk.LEFT, padx=5)

    def nuevo_socio(self):
        """Abre el diálogo para crear un nuevo socio"""
        socios_principales = obtener_socios_principales()
        datos = abrir_dialogo_socio(self, socios_principales=socios_principales)
        if datos:
            crear_socio(**datos)
            self.actualizar_arbol()

    def editar_socio(self):
        """Abre el diálogo para editar el socio seleccionado"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("Advertencia", "Por favor, seleccione un socio para editar")
            return
            
        socio_id = int(self.tree.item(selection[0], "tags")[0])
        with Session() as session:
            socio = session.query(Socio).get(socio_id)
            if socio:
                socios_principales = obtener_socios_principales()
                socio_actualizado = abrir_dialogo_socio(self, socio, socios_principales)
                if socio_actualizado:
                    actualizar_socio(socio_id, **socio_actualizado)
                    self.actualizar_arbol()
                    messagebox.showinfo("Éxito", "Socio actualizado correctamente")

    def desactivar_socio(self):
        """Desactiva el socio seleccionado"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("Advertencia", "Por favor, seleccione un socio para desactivar")
            return
            
        socio_id = int(self.tree.item(selection[0], "tags")[0])
        socio = self.session.query(Socio).get(socio_id)
        if socio:
            confirmacion = messagebox.askyesno("Desactivar Socio", 
                "¿Estás seguro de que quieres desactivar este socio?\n\n" +
                "Si es un socio principal, también se desactivarán todos sus miembros de familia.")
            if confirmacion:
                if desactivar_socio(socio_id):
                    self.session.commit()
                    messagebox.showinfo("Éxito", "Socio desactivado correctamente")
                    self.actualizar_arbol()
                else:
                    self.session.rollback()
                    messagebox.showerror("Error", "No se pudo desactivar el socio")

    def activar_socio(self):
        """Activa el socio seleccionado"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("Advertencia", "Por favor, seleccione un socio para activar")
            return
            
        socio_id = int(self.tree.item(selection[0], "tags")[0])
        socio = self.session.query(Socio).get(socio_id)
        if socio:
            if activar_socio(socio_id):
                self.session.commit()
                messagebox.showinfo("Éxito", "Socio activado correctamente")
                self.actualizar_arbol()
            else:
                self.session.rollback()
                messagebox.showerror("Error", "No se pudo activar el socio")

    def actualizar_arbol(self):
        """Actualiza el árbol de socios"""
        # Limpiar el árbol
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        # Configurar columnas según tipo de usuario
        if self.tipo_usuario == 'Trabajador':
            self.tree["columns"] = ("codigo", "nombre", "fecha_nacimiento", "telefono")
            self.tree.heading("#0", text="")
            self.tree.heading("codigo", text="Código Socio")
            self.tree.heading("nombre", text="Nombre Completo")
            self.tree.heading("fecha_nacimiento", text="Fecha de Nacimiento")
            self.tree.heading("telefono", text="Teléfono")
            
            # Configurar ancho de columnas
            self.tree.column("#0", width=20)
            self.tree.column("codigo", width=100)
            self.tree.column("nombre", width=250)
            self.tree.column("fecha_nacimiento", width=150)
            self.tree.column("telefono", width=120)
        else:  # Junta o Administrador
            self.tree["columns"] = ("codigo", "nombre", "dni", "telefono", "email", "direccion", "fecha_nacimiento")
            self.tree.heading("#0", text="")
            self.tree.heading("codigo", text="Código Socio")
            self.tree.heading("nombre", text="Nombre Completo")
            self.tree.heading("dni", text="DNI/NIE")
            self.tree.heading("telefono", text="Teléfono")
            self.tree.heading("email", text="Correo Electrónico")
            self.tree.heading("direccion", text="Dirección")
            self.tree.heading("fecha_nacimiento", text="Fecha de Nacimiento")
            
            # Configurar ancho de columnas
            self.tree.column("#0", width=20)
            self.tree.column("codigo", width=100)
            self.tree.column("nombre", width=250)
            self.tree.column("dni", width=100)
            self.tree.column("telefono", width=120)
            self.tree.column("email", width=200)
            self.tree.column("direccion", width=250)
            self.tree.column("fecha_nacimiento", width=150)
            
        # Obtener socios según tipo de usuario
        if self.tipo_usuario == 'Trabajador':
            socios = self.session.query(Socio).filter(
                Socio.es_principal == True,
                Socio.activo == True
            ).all()
        else:  # Junta o Administrador
            socios = self.session.query(Socio).filter(
                Socio.es_principal == True
            ).all()
            
        # Insertar socios en el árbol
        for socio in socios:
            if self.tipo_usuario == 'Trabajador':
                values = (
                    socio.codigo_socio,
                    f"{socio.nombre} {socio.primer_apellido} {socio.segundo_apellido or ''}",
                    socio.fecha_nacimiento.strftime("%d/%m/%Y") if socio.fecha_nacimiento else "",
                    socio.telefono or ""
                )
            else:
                values = (
                    socio.codigo_socio,
                    f"{socio.nombre} {socio.primer_apellido} {socio.segundo_apellido or ''}",
                    socio.dni or "",
                    socio.telefono or "",
                    socio.email or "",
                    socio.direccion or "",
                    socio.fecha_nacimiento.strftime("%d/%m/%Y") if socio.fecha_nacimiento else ""
                )
                
            item = self.tree.insert("", "end", text="", values=values, tags=(str(socio.id),))
            
            # Insertar miembros de la familia
            miembros = self.session.query(Socio).filter(
                Socio.socio_principal_id == socio.id
            ).all()
            
            for miembro in miembros:
                if self.tipo_usuario == 'Trabajador':
                    member_values = (
                        miembro.codigo_socio,
                        f"{miembro.nombre} {miembro.primer_apellido} {miembro.segundo_apellido or ''}",
                        miembro.fecha_nacimiento.strftime("%d/%m/%Y") if miembro.fecha_nacimiento else "",
                        miembro.telefono or ""
                    )
                else:
                    member_values = (
                        miembro.codigo_socio,
                        f"{miembro.nombre} {miembro.primer_apellido} {miembro.segundo_apellido or ''}",
                        miembro.dni or "",
                        miembro.telefono or "",
                        miembro.email or "",
                        miembro.direccion or "",
                        miembro.fecha_nacimiento.strftime("%d/%m/%Y") if miembro.fecha_nacimiento else ""
                    )
                    
                self.tree.insert(item, "end", text="", values=member_values, tags=(str(miembro.id),))
                
            # Aplicar estilo para socios inactivos
            if not socio.activo:
                self.tree.item(item, tags=(str(socio.id), "inactivo"))
                for child in self.tree.get_children(item):
                    self.tree.item(child, tags=(self.tree.item(child, "tags")[0], "inactivo"))

    def importar_excel(self):
        """Importa socios desde un archivo Excel"""
        file_path = filedialog.askopenfilename(
            title="Seleccionar archivo Excel",
            filetypes=[("Excel files", "*.xlsx *.xls")]
        )
        
        if not file_path:
            return
            
        try:
            from app.logic.excel_importer import import_socios_from_excel
            socios_importados, errores = import_socios_from_excel(self.session, file_path)
            
            messagebox.showinfo(
                "Importación completada",
                f"Se importaron {socios_importados} socios correctamente.\n"
                f"Hubo {errores} errores durante la importación."
            )
            
            # Actualizar el árbol
            self.actualizar_arbol()
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al importar el archivo: {str(e)}")
            # Hacer rollback en caso de error
            self.session.rollback()

    def exportar_excel(self):
        """Exporta los socios a un archivo Excel"""
        try:
            # Obtener todos los socios usando la sesión proporcionada
            socios = self.session.query(Socio).all()
            
            # Crear un DataFrame con los datos
            data = []
            for socio in socios:
                # Obtener el código del socio principal si existe
                socio_principal_codigo = None
                if not socio.es_principal and socio.socio_principal:
                    socio_principal_codigo = socio.socio_principal.codigo_socio

                data.append({
                    'CODIGO_SOCIO': socio.codigo_socio,
                    'NOMBRE': socio.nombre,
                    'PRIMER_APELLIDO': socio.primer_apellido,
                    'SEGUNDO_APELLIDO': socio.segundo_apellido,
                    'DNI': socio.dni,
                    'TELEFONO': socio.telefono,
                    'EMAIL': socio.email,
                    'DIRECCION': socio.direccion,
                    'POBLACION': socio.poblacion,
                    'CODIGO_POSTAL': socio.codigo_postal,
                    'PROVINCIA': socio.provincia,
                    'FECHA_NACIMIENTO': socio.fecha_nacimiento,
                    'ES_PRINCIPAL': socio.es_principal,
                    'ACTIVO': socio.activo,
                    'RGPD': socio.rgpd,
                    'CASA': socio.casa,
                    'TOTAL_SOC': socio.total_soc,
                    'NUM_PERS': socio.num_pers,
                    'ADHERITS': socio.adherits,
                    'MENOR_3_ANYS': socio.menor_3_anys,
                    'CUOTA': socio.cuota,
                    'IBAN': socio.iban,
                    'ENTIDAD': socio.entidad,
                    'OFICINA': socio.oficina,
                    'DC': socio.dc,
                    'CUENTA_CORRIENTE': socio.cuenta_corriente,
                    'TELEFONO2': socio.telefono2,
                    'EMAIL2': socio.email2,
                    'OBSERVACIONES': socio.observaciones,
                    'FOTO_PATH': socio.foto_path,
                    'CANVI': socio.canvi,
                    'SOCIO_PRINCIPAL_CODIGO': socio_principal_codigo
                })
            
            df = pd.DataFrame(data)
            
            # Pedir al usuario dónde guardar el archivo
            file_path = filedialog.asksaveasfilename(
                defaultextension=".xlsx",
                filetypes=[("Excel files", "*.xlsx")],
                title="Guardar archivo Excel"
            )
            
            if file_path:
                # Guardar el DataFrame en Excel
                df.to_excel(file_path, index=False)
                messagebox.showinfo("Éxito", "Socios exportados correctamente")
                
        except Exception as e:
            messagebox.showerror("Error", f"Error al exportar los socios: {str(e)}")
            # Hacer rollback en caso de error
            self.session.rollback() 
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from PIL import Image, ImageTk
from tkcalendar import DateEntry
import os
import shutil
from app.logic.photo_handler import save_photo, get_photo_path
from app.logic.socio_handler import generar_codigo_socio
from sqlalchemy.orm import Session
from app.models.socio import Socio
from datetime import datetime

class SocioDialog(tk.Toplevel):
    def __init__(self, parent, socio=None, socios_principales=None):
        super().__init__(parent)
        self.transient(parent)
        self.socio = socio
        self.socios_principales = socios_principales or []
        self.title("Socio")
        self.geometry("800x800")
        self.resizable(False, False)
        
        # Variables
        self.es_principal = tk.BooleanVar(value=socio.es_principal if socio else True)
        self.socio_principal_id = tk.StringVar(value=str(socio.socio_principal_id) if socio and socio.socio_principal_id else "")
        self.rgpd = tk.BooleanVar(value=socio.rgpd if socio else False)
        self.codigo_var = tk.StringVar(value=socio.codigo_socio if socio else "")
        self.nombre_var = tk.StringVar(value=socio.nombre if socio else "")
        self.primer_apellido_var = tk.StringVar(value=socio.primer_apellido if socio else "")
        self.segundo_apellido_var = tk.StringVar(value=socio.segundo_apellido if socio else "")
        self.dni_var = tk.StringVar(value=socio.dni if socio else "")
        self.fecha_nacimiento_var = tk.StringVar(value=socio.fecha_nacimiento.strftime('%Y-%m-%d') if socio and socio.fecha_nacimiento else "")
        self.telefono_var = tk.StringVar(value=socio.telefono if socio else "")
        self.email_var = tk.StringVar(value=socio.email if socio else "")
        self.direccion_var = tk.StringVar(value=socio.direccion if socio else "")
        self.poblacion_var = tk.StringVar(value=socio.poblacion if socio else "")
        self.codigo_postal_var = tk.StringVar(value=socio.codigo_postal if socio else "")
        self.provincia_var = tk.StringVar(value=socio.provincia if socio else "")
        self.foto_path_var = tk.StringVar(value=socio.foto_path if socio else "")
        self.foto_path = None  # Variable para almacenar la ruta de la foto seleccionada
        
        self.create_widgets()
        
        if socio:
            self.load_socio_data()

        self.grab_set()
        self.wait_window(self)
    
    def create_widgets(self):
        # Frame principal con scrollbar
        container = ttk.Frame(self)
        container.pack(fill=tk.BOTH, expand=True)
        
        # Crear canvas y scrollbar
        canvas = tk.Canvas(container)
        scrollbar = ttk.Scrollbar(container, orient="vertical", command=canvas.yview)
        
        # Frame para el contenido
        self.main_frame = ttk.Frame(canvas)
        self.main_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=self.main_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Empaquetar widgets
        scrollbar.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)
        
        # Tipo de socio (marcado al principio)
        self.create_socio_type_section()
        
        # Datos básicos
        self.create_basic_info_section()
        self.create_contact_info_section()
        self.create_family_info_section()
        self.create_photo_section()
        self.create_buttons_section()
        
        # Actualizar visibilidad inicial
        self.toggle_principal()
    
    def create_socio_type_section(self):
        """Sección para seleccionar el tipo de socio"""
        frame = ttk.LabelFrame(self.main_frame, text="Tipo de Socio", padding="10")
        frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Es principal
        ttk.Checkbutton(frame, text="Es socio principal", variable=self.es_principal, 
                       command=self.toggle_principal).grid(row=0, column=0, sticky=tk.W)
        
        # Socio principal (solo visible si no es principal)
        self.socio_principal_frame = ttk.Frame(frame)
        self.socio_principal_frame.grid(row=1, column=0, columnspan=6, sticky=tk.EW)
        ttk.Label(self.socio_principal_frame, text="Buscar Socio Principal:").grid(row=0, column=0, sticky=tk.W)
        self.busqueda_principal = ttk.Entry(self.socio_principal_frame)
        self.busqueda_principal.grid(row=0, column=1, sticky=tk.EW, padx=5)
        self.busqueda_principal.bind('<KeyRelease>', self.filtrar_socios_principales)
        
        # Lista de socios principales
        self.lista_socios = tk.Listbox(self.socio_principal_frame, height=5)
        self.lista_socios.grid(row=1, column=0, columnspan=2, sticky=tk.EW, pady=5)
        self.lista_socios.bind('<<ListboxSelect>>', self.seleccionar_socio_principal)
        
        # Configurar el grid
        self.socio_principal_frame.grid_columnconfigure(1, weight=1)
        
        # Diccionario para mantener la relación entre índices y IDs
        self.socio_indices = {}
        
        # Actualizar lista inicial
        self.actualizar_lista_socios()
    
    def create_basic_info_section(self):
        """Crea la sección de información básica"""
        basic_frame = ttk.LabelFrame(self.main_frame, text="Información Básica")
        basic_frame.pack(fill=tk.X, padx=10, pady=5)

        # Frame para código y tipo de socio
        self.codigo_frame = ttk.Frame(basic_frame)
        self.codigo_frame.pack(fill=tk.X, pady=5)

        ttk.Label(self.codigo_frame, text="Código Socio:").pack(side=tk.LEFT, padx=5)
        self.codigo_entry = ttk.Entry(self.codigo_frame, textvariable=self.codigo_var)
        self.codigo_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)

        # Frame para nombre y apellidos
        name_frame = ttk.Frame(basic_frame)
        name_frame.pack(fill=tk.X, pady=5)

        ttk.Label(name_frame, text="Nombre:").pack(side=tk.LEFT, padx=5)
        self.nombre_entry = ttk.Entry(name_frame, textvariable=self.nombre_var)
        self.nombre_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)

        # Frame para apellidos
        apellidos_frame = ttk.Frame(basic_frame)
        apellidos_frame.pack(fill=tk.X, pady=5)

        ttk.Label(apellidos_frame, text="Primer Apellido:").pack(side=tk.LEFT, padx=5)
        self.primer_apellido_entry = ttk.Entry(apellidos_frame, textvariable=self.primer_apellido_var)
        self.primer_apellido_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)

        ttk.Label(apellidos_frame, text="Segundo Apellido:").pack(side=tk.LEFT, padx=5)
        self.segundo_apellido_entry = ttk.Entry(apellidos_frame, textvariable=self.segundo_apellido_var)
        self.segundo_apellido_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)

        # Frame para DNI y fecha de nacimiento
        dni_frame = ttk.Frame(basic_frame)
        dni_frame.pack(fill=tk.X, pady=5)

        ttk.Label(dni_frame, text="DNI:").pack(side=tk.LEFT, padx=5)
        self.dni_entry = ttk.Entry(dni_frame, textvariable=self.dni_var)
        self.dni_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)

        ttk.Label(dni_frame, text="Fecha Nacimiento:").pack(side=tk.LEFT, padx=5)
        self.fecha_nacimiento_entry = DateEntry(dni_frame, width=12, background='darkblue',
                                              foreground='white', borderwidth=2, date_pattern='yyyy-mm-dd')
        self.fecha_nacimiento_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        if self.fecha_nacimiento_var.get():
            self.fecha_nacimiento_entry.set_date(self.fecha_nacimiento_var.get())
    
    def create_contact_info_section(self):
        frame = ttk.LabelFrame(self.main_frame, text="Información de Contacto", padding="10")
        frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Dirección (solo visible si es principal)
        self.direccion_frame = ttk.Frame(frame)
        self.direccion_frame.grid(row=0, column=0, columnspan=3, sticky=tk.W)
        ttk.Label(self.direccion_frame, text="Dirección:").grid(row=0, column=0, sticky=tk.W)
        self.direccion_entry = ttk.Entry(self.direccion_frame, width=40)
        self.direccion_entry.grid(row=0, column=1, padx=5, sticky=tk.EW)
        
        # Población (solo visible si es principal)
        self.poblacion_frame = ttk.Frame(frame)
        self.poblacion_frame.grid(row=1, column=0, columnspan=2, sticky=tk.W)
        ttk.Label(self.poblacion_frame, text="Población:").grid(row=0, column=0, sticky=tk.W)
        self.poblacion_entry = ttk.Entry(self.poblacion_frame)
        self.poblacion_entry.grid(row=0, column=1, padx=5, sticky=tk.EW)
        
        # Código Postal (solo visible si es principal)
        self.cp_frame = ttk.Frame(frame)
        self.cp_frame.grid(row=1, column=2, columnspan=2, sticky=tk.W)
        ttk.Label(self.cp_frame, text="CP:").grid(row=0, column=0, sticky=tk.W)
        self.cp_entry = ttk.Entry(self.cp_frame, width=7)
        self.cp_entry.grid(row=0, column=1, padx=5, sticky=tk.EW)
        
        # Provincia (solo visible si es principal)
        self.provincia_frame = ttk.Frame(frame)
        self.provincia_frame.grid(row=1, column=4, columnspan=2, sticky=tk.W)
        ttk.Label(self.provincia_frame, text="Provincia:").grid(row=0, column=0, sticky=tk.W)
        self.provincia_entry = ttk.Entry(self.provincia_frame)
        self.provincia_entry.grid(row=0, column=1, padx=5, sticky=tk.EW)
        
        # Teléfonos
        ttk.Label(frame, text="Teléfono:").grid(row=2, column=0, sticky=tk.W)
        self.telefono_entry = ttk.Entry(frame)
        self.telefono_entry.grid(row=2, column=1, padx=5, sticky=tk.EW)
        
        # Teléfono 2 (solo visible si es principal)
        self.telefono2_frame = ttk.Frame(frame)
        self.telefono2_frame.grid(row=2, column=2, columnspan=2, sticky=tk.W)
        ttk.Label(self.telefono2_frame, text="Teléfono 2:").grid(row=0, column=0, sticky=tk.W)
        self.telefono2_entry = ttk.Entry(self.telefono2_frame)
        self.telefono2_entry.grid(row=0, column=1, padx=5, sticky=tk.EW)
        
        # Emails
        ttk.Label(frame, text="Email:").grid(row=3, column=0, sticky=tk.W)
        self.email_entry = ttk.Entry(frame)
        self.email_entry.grid(row=3, column=1, padx=5, sticky=tk.EW)
        
        # Email 2 (solo visible si es principal)
        self.email2_frame = ttk.Frame(frame)
        self.email2_frame.grid(row=3, column=2, columnspan=2, sticky=tk.W)
        ttk.Label(self.email2_frame, text="Email 2:").grid(row=0, column=0, sticky=tk.W)
        self.email2_entry = ttk.Entry(self.email2_frame)
        self.email2_entry.grid(row=0, column=1, padx=5, sticky=tk.EW)
        
        # Configurar el grid para que los widgets se expandan correctamente
        frame.grid_columnconfigure(1, weight=1)
        for subframe in [self.direccion_frame, self.poblacion_frame, self.cp_frame, 
                        self.provincia_frame, self.telefono2_frame, self.email2_frame]:
            subframe.grid_columnconfigure(1, weight=1)
    
    def create_family_info_section(self):
        frame = ttk.LabelFrame(self.main_frame, text="Información Familiar", padding="10")
        frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Número de personas (solo visible si es principal)
        self.num_pers_frame = ttk.Frame(frame)
        self.num_pers_frame.grid(row=0, column=0, columnspan=2, sticky=tk.W)
        ttk.Label(self.num_pers_frame, text="Número de Personas:").pack(side=tk.LEFT)
        self.num_pers_entry = ttk.Entry(self.num_pers_frame, width=5)
        self.num_pers_entry.pack(side=tk.LEFT, padx=5)
        
        # Adheridos (solo visible si es principal)
        self.adheridos_frame = ttk.Frame(frame)
        self.adheridos_frame.grid(row=0, column=2, columnspan=2, sticky=tk.W)
        ttk.Label(self.adheridos_frame, text="Adheridos:").pack(side=tk.LEFT)
        self.adheridos_entry = ttk.Entry(self.adheridos_frame, width=5)
        self.adheridos_entry.pack(side=tk.LEFT, padx=5)
        
        # Menores de 3 años (solo visible si es principal)
        self.menores_frame = ttk.Frame(frame)
        self.menores_frame.grid(row=0, column=4, columnspan=2, sticky=tk.W)
        ttk.Label(self.menores_frame, text="Menores de 3 años:").pack(side=tk.LEFT)
        self.menores_entry = ttk.Entry(self.menores_frame, width=5)
        self.menores_entry.pack(side=tk.LEFT, padx=5)
    
    def create_photo_section(self):
        frame = ttk.LabelFrame(self.main_frame, text="Foto", padding="10")
        frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Frame para la foto
        self.foto_frame = ttk.Frame(frame, width=200, height=200)
        self.foto_frame.pack(pady=10)
        self.foto_frame.pack_propagate(False)
        
        # Label para mostrar la foto
        self.foto_label = ttk.Label(self.foto_frame)
        self.foto_label.pack(expand=True, fill=tk.BOTH)
        
        # Botón para seleccionar foto
        ttk.Button(frame, text="Seleccionar Foto", command=self.select_photo).pack(pady=5)
    
    def create_buttons_section(self):
        frame = ttk.Frame(self.main_frame)
        frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Button(frame, text="Guardar", command=self.guardar).pack(side=tk.LEFT, padx=5)
        ttk.Button(frame, text="Cancelar", command=self.destroy).pack(side=tk.LEFT)
    
    def toggle_principal(self):
        """Alterna la visibilidad de los campos según el tipo de socio"""
        if self.es_principal.get():
            # Mostrar todos los campos para socio principal
            self.codigo_frame.pack(fill=tk.X, pady=5)
            self.codigo_entry.config(state="normal")
            self.dni_entry.config(state="normal")
            self.direccion_frame.grid()
            self.poblacion_frame.grid()
            self.cp_frame.grid()
            self.provincia_frame.grid()
            self.telefono2_frame.grid()
            self.email2_frame.grid()
            self.num_pers_frame.grid()
            self.adheridos_frame.grid()
            self.menores_frame.grid()
            
            # Configurar campos como requeridos
            self.dni_entry.config(state="normal")
            self.direccion_entry.config(state="normal")
            self.poblacion_entry.config(state="normal")
            self.cp_entry.config(state="normal")
            self.provincia_entry.config(state="normal")
            self.telefono_entry.config(state="normal")
            self.email_entry.config(state="normal")
        else:
            # Ocultar campos no requeridos para socio familiar
            self.codigo_frame.pack_forget()
            self.codigo_entry.config(state="disabled")
            self.dni_entry.config(state="disabled")
            self.direccion_frame.grid_remove()
            self.poblacion_frame.grid_remove()
            self.cp_frame.grid_remove()
            self.provincia_frame.grid_remove()
            self.telefono2_frame.grid_remove()
            self.email2_frame.grid_remove()
            self.num_pers_frame.grid_remove()
            self.adheridos_frame.grid_remove()
            self.menores_frame.grid_remove()
            
            # Configurar campos opcionales
            self.dni_entry.config(state="disabled")
            self.direccion_entry.config(state="disabled")
            self.poblacion_entry.config(state="disabled")
            self.cp_entry.config(state="disabled")
            self.provincia_entry.config(state="disabled")
            self.telefono_entry.config(state="normal")
            self.email_entry.config(state="normal")

        # La fecha de nacimiento siempre debe estar habilitada
        self.fecha_nacimiento_entry.config(state="normal")
    
    def select_photo(self):
        """Permite al usuario seleccionar una foto"""
        file_path = filedialog.askopenfilename(
            title="Seleccionar Foto",
            filetypes=[("Imágenes", "*.png *.jpg *.jpeg *.gif *.bmp")]
        )
        if file_path:
            self.foto_path = file_path  # Guardar la ruta de la foto
            self.foto_path_var.set(file_path)  # Actualizar la variable de Tkinter
            self.show_photo_preview(file_path)
    
    def show_photo_preview(self, photo_path):
        """Muestra una vista previa de la foto seleccionada"""
        try:
            image = Image.open(photo_path)
            image.thumbnail((200, 200))
            photo = ImageTk.PhotoImage(image)
            self.foto_label.configure(image=photo)
            self.foto_label.image = photo
        except Exception as e:
            messagebox.showerror("Error", f"Error al cargar la imagen: {str(e)}")
    
    def load_socio_data(self):
        """Carga los datos del socio en el formulario"""
        if not self.socio:
            return
            
        # Datos básicos
        self.rgpd.set(self.socio.rgpd)
        self.codigo_entry.delete(0, tk.END)
        self.codigo_entry.insert(0, self.socio.codigo_socio or "")
        self.dni_entry.delete(0, tk.END)
        self.dni_entry.insert(0, self.socio.dni or "")
        self.nombre_entry.delete(0, tk.END)
        self.nombre_entry.insert(0, self.socio.nombre or "")
        self.primer_apellido_entry.delete(0, tk.END)
        self.primer_apellido_entry.insert(0, self.socio.primer_apellido or "")
        self.segundo_apellido_entry.delete(0, tk.END)
        self.segundo_apellido_entry.insert(0, self.socio.segundo_apellido or "")
        if self.socio.fecha_nacimiento:
            self.fecha_nacimiento_entry.set_date(self.socio.fecha_nacimiento)
        
        # Información de contacto
        self.direccion_entry.delete(0, tk.END)
        self.direccion_entry.insert(0, self.socio.direccion or "")
        self.poblacion_entry.delete(0, tk.END)
        self.poblacion_entry.insert(0, self.socio.poblacion or "")
        self.cp_entry.delete(0, tk.END)
        self.cp_entry.insert(0, self.socio.codigo_postal or "")
        self.provincia_entry.delete(0, tk.END)
        self.provincia_entry.insert(0, self.socio.provincia or "")
        self.telefono_entry.delete(0, tk.END)
        self.telefono_entry.insert(0, self.socio.telefono or "")
        self.telefono2_entry.delete(0, tk.END)
        self.telefono2_entry.insert(0, self.socio.telefono2 or "")
        self.email_entry.delete(0, tk.END)
        self.email_entry.insert(0, self.socio.email or "")
        self.email2_entry.delete(0, tk.END)
        self.email2_entry.insert(0, self.socio.email2 or "")
        
        # Información familiar
        self.es_principal.set(self.socio.es_principal)
        if self.socio.socio_principal_id:
            self.socio_principal_id.set(str(self.socio.socio_principal_id))
        self.num_pers_entry.delete(0, tk.END)
        self.num_pers_entry.insert(0, str(self.socio.num_pers or ""))
        self.adheridos_entry.delete(0, tk.END)
        self.adheridos_entry.insert(0, str(self.socio.adherits or ""))
        self.menores_entry.delete(0, tk.END)
        self.menores_entry.insert(0, str(self.socio.menor_3_anys or ""))
        
        # Foto
        if self.socio.foto_path:
            self.foto_path = self.socio.foto_path
            self.foto_path_var.set(self.socio.foto_path)
            self.show_photo_preview(self.socio.foto_path)
        
        # Actualizar visibilidad de campos
        self.toggle_principal()
    
    def filtrar_socios_principales(self, event=None):
        """Filtra la lista de socios principales según el texto de búsqueda"""
        busqueda = self.busqueda_principal.get().lower()
        self.lista_socios.delete(0, tk.END)
        self.socio_indices.clear()
        
        for socio in self.socios_principales:
            texto_busqueda = f"{socio.codigo_socio} - {socio.nombre} {socio.primer_apellido}".lower()
            if busqueda in texto_busqueda:
                idx = self.lista_socios.size()
                self.lista_socios.insert(tk.END, f"{socio.codigo_socio} - {socio.nombre} {socio.primer_apellido}")
                self.socio_indices[idx] = socio.id
    
    def seleccionar_socio_principal(self, event=None):
        """Maneja la selección de un socio principal de la lista"""
        if not self.lista_socios.curselection():
            return
            
        idx = self.lista_socios.curselection()[0]
        if idx in self.socio_indices:
            self.socio_principal_id.set(str(self.socio_indices[idx]))
    
    def actualizar_lista_socios(self):
        """Actualiza la lista completa de socios principales"""
        self.lista_socios.delete(0, tk.END)
        self.socio_indices.clear()
        
        for socio in self.socios_principales:
            idx = self.lista_socios.size()
            self.lista_socios.insert(tk.END, f"{socio.codigo_socio} - {socio.nombre} {socio.primer_apellido}")
            self.socio_indices[idx] = socio.id
    
    def guardar(self):
        """Guarda los datos del socio"""
        try:
            # Validar campos requeridos para todos los socios
            if not self.nombre_entry.get().strip():
                messagebox.showerror("Error", "El nombre es obligatorio")
                return
            if not self.primer_apellido_entry.get().strip():
                messagebox.showerror("Error", "El primer apellido es obligatorio")
                return

            # Validaciones adicionales solo para socios principales
            if self.es_principal.get():
                if not self.dni_entry.get().strip():
                    messagebox.showerror("Error", "El DNI es obligatorio para socios principales")
                    return
                if not self.fecha_nacimiento_entry.get().strip():
                    messagebox.showerror("Error", "La fecha de nacimiento es obligatoria para socios principales")
                    return
                if not self.direccion_entry.get().strip():
                    messagebox.showerror("Error", "La dirección es obligatoria para socios principales")
                    return
                if not self.poblacion_entry.get().strip():
                    messagebox.showerror("Error", "La población es obligatoria para socios principales")
                    return
                if not self.cp_entry.get().strip():
                    messagebox.showerror("Error", "El código postal es obligatorio para socios principales")
                    return
                if not self.provincia_entry.get().strip():
                    messagebox.showerror("Error", "La provincia es obligatoria para socios principales")
                    return
                if not self.telefono_entry.get().strip():
                    messagebox.showerror("Error", "El teléfono es obligatorio para socios principales")
                    return
                if not self.email_entry.get().strip():
                    messagebox.showerror("Error", "El email es obligatorio para socios principales")
                    return

            # Crear o actualizar socio
            socio_data = {
                'nombre': self.nombre_entry.get().strip(),
                'primer_apellido': self.primer_apellido_entry.get().strip(),
                'segundo_apellido': self.segundo_apellido_entry.get().strip(),
                'es_principal': self.es_principal.get(),
                'telefono': self.telefono_entry.get().strip(),
                'email': self.email_entry.get().strip(),
                'foto_path': self.foto_path
            }

            if self.es_principal.get():
                socio_data.update({
                    'codigo_socio': self.codigo_entry.get().strip(),
                    'dni': self.dni_entry.get().strip(),
                    'fecha_nacimiento': self.fecha_nacimiento_entry.get_date(),
                    'direccion': self.direccion_entry.get().strip(),
                    'poblacion': self.poblacion_entry.get().strip(),
                    'codigo_postal': self.cp_entry.get().strip(),
                    'provincia': self.provincia_entry.get().strip(),
                    'telefono2': self.telefono2_entry.get().strip(),
                    'email2': self.email2_entry.get().strip(),
                    'num_pers': int(self.num_pers_entry.get() or 0),
                    'adherits': int(self.adheridos_entry.get() or 0),
                    'menor_3_anys': int(self.menores_entry.get() or 0)
                })
            else:
                # Para socios familiares, asegurarse de que tengan un socio principal asignado
                if not self.socio_principal_id.get():
                    messagebox.showerror("Error", "Debe seleccionar un socio principal")
                    return
                socio_data['socio_principal_id'] = int(self.socio_principal_id.get())

            if self.socio:
                # Actualizar socio existente
                self.socio.update(socio_data)
            else:
                # Crear nuevo socio
                from app.logic.socios import crear_socio
                self.socio = crear_socio(**socio_data)

            self.result = True
            self.destroy()
        except Exception as e:
            messagebox.showerror("Error", f"Error al guardar el socio: {str(e)}")

def abrir_dialogo_socio(parent, socio=None, socios_principales=None):
    """Abre el diálogo de socio y retorna los datos si se guardó"""
    dialog = SocioDialog(parent, socio, socios_principales)
    return getattr(dialog, 'socio', None)

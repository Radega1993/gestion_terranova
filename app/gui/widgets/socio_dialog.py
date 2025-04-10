import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from PIL import Image, ImageTk
from tkcalendar import DateEntry
import os
import shutil
from app.logic.photo_handler import save_photo, get_photo_path

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
        self.foto_path = tk.StringVar()
        self.es_principal = tk.BooleanVar(value=False)
        self.socio_principal_id = tk.StringVar()
        self.rgpd = tk.BooleanVar(value=False)
        
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
        
        # Datos básicos
        self.create_basic_info_section()
        self.create_contact_info_section()
        self.create_bank_info_section()
        self.create_family_info_section()
        self.create_photo_section()
        self.create_buttons_section()
    
    def create_basic_info_section(self):
        frame = ttk.LabelFrame(self.main_frame, text="Datos Básicos", padding="10")
        frame.pack(fill=tk.X, padx=10, pady=5)
        
        # RGPD
        ttk.Checkbutton(frame, text="RGPD", variable=self.rgpd).grid(row=0, column=0, sticky=tk.W)
        
        # Código socio
        ttk.Label(frame, text="Código Socio:").grid(row=1, column=0, sticky=tk.W)
        self.codigo_socio_entry = ttk.Entry(frame)
        self.codigo_socio_entry.grid(row=1, column=1, padx=5)
        
        # DNI
        ttk.Label(frame, text="DNI:").grid(row=1, column=2, sticky=tk.W)
        self.dni_entry = ttk.Entry(frame)
        self.dni_entry.grid(row=1, column=3, padx=5)
        
        # Nombre completo
        ttk.Label(frame, text="Nombre:").grid(row=2, column=0, sticky=tk.W)
        self.nombre_entry = ttk.Entry(frame)
        self.nombre_entry.grid(row=2, column=1, padx=5)
        
        ttk.Label(frame, text="Primer Apellido:").grid(row=2, column=2, sticky=tk.W)
        self.primer_apellido_entry = ttk.Entry(frame)
        self.primer_apellido_entry.grid(row=2, column=3, padx=5)
        
        ttk.Label(frame, text="Segundo Apellido:").grid(row=2, column=4, sticky=tk.W)
        self.segundo_apellido_entry = ttk.Entry(frame)
        self.segundo_apellido_entry.grid(row=2, column=5, padx=5)
        
        # Fecha de nacimiento
        ttk.Label(frame, text="Fecha Nacimiento:").grid(row=3, column=0, sticky=tk.W)
        self.fecha_nacimiento_entry = DateEntry(frame, width=12, background='darkblue',
                                              foreground='white', borderwidth=2)
        self.fecha_nacimiento_entry.grid(row=3, column=1, padx=5)
        
        # Cuota
        ttk.Label(frame, text="Cuota:").grid(row=3, column=2, sticky=tk.W)
        self.cuota_entry = ttk.Entry(frame)
        self.cuota_entry.grid(row=3, column=3, padx=5)
    
    def create_contact_info_section(self):
        frame = ttk.LabelFrame(self.main_frame, text="Información de Contacto", padding="10")
        frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Dirección
        ttk.Label(frame, text="Dirección:").grid(row=0, column=0, sticky=tk.W)
        self.direccion_entry = ttk.Entry(frame, width=40)
        self.direccion_entry.grid(row=0, column=1, columnspan=3, padx=5)
        
        # Población
        ttk.Label(frame, text="Población:").grid(row=1, column=0, sticky=tk.W)
        self.poblacion_entry = ttk.Entry(frame)
        self.poblacion_entry.grid(row=1, column=1, padx=5)
        
        # Código Postal
        ttk.Label(frame, text="CP:").grid(row=1, column=2, sticky=tk.W)
        self.cp_entry = ttk.Entry(frame, width=7)
        self.cp_entry.grid(row=1, column=3, padx=5)
        
        # Provincia
        ttk.Label(frame, text="Provincia:").grid(row=1, column=4, sticky=tk.W)
        self.provincia_entry = ttk.Entry(frame)
        self.provincia_entry.grid(row=1, column=5, padx=5)
        
        # Teléfonos
        ttk.Label(frame, text="Teléfono:").grid(row=2, column=0, sticky=tk.W)
        self.telefono_entry = ttk.Entry(frame)
        self.telefono_entry.grid(row=2, column=1, padx=5)
        
        ttk.Label(frame, text="Teléfono 2:").grid(row=2, column=2, sticky=tk.W)
        self.telefono2_entry = ttk.Entry(frame)
        self.telefono2_entry.grid(row=2, column=3, padx=5)
        
        # Emails
        ttk.Label(frame, text="Email:").grid(row=3, column=0, sticky=tk.W)
        self.email_entry = ttk.Entry(frame)
        self.email_entry.grid(row=3, column=1, padx=5)
        
        ttk.Label(frame, text="Email 2:").grid(row=3, column=2, sticky=tk.W)
        self.email2_entry = ttk.Entry(frame)
        self.email2_entry.grid(row=3, column=3, padx=5)
    
    def create_bank_info_section(self):
        frame = ttk.LabelFrame(self.main_frame, text="Información Bancaria", padding="10")
        frame.pack(fill=tk.X, padx=10, pady=5)
        
        # IBAN
        ttk.Label(frame, text="IBAN:").grid(row=0, column=0, sticky=tk.W)
        self.iban_entry = ttk.Entry(frame, width=6)
        self.iban_entry.grid(row=0, column=1, padx=5)
        
        # Entidad
        ttk.Label(frame, text="Entidad:").grid(row=0, column=2, sticky=tk.W)
        self.entidad_entry = ttk.Entry(frame, width=6)
        self.entidad_entry.grid(row=0, column=3, padx=5)
        
        # Oficina
        ttk.Label(frame, text="Oficina:").grid(row=0, column=4, sticky=tk.W)
        self.oficina_entry = ttk.Entry(frame, width=6)
        self.oficina_entry.grid(row=0, column=5, padx=5)
        
        # DC
        ttk.Label(frame, text="DC:").grid(row=0, column=6, sticky=tk.W)
        self.dc_entry = ttk.Entry(frame, width=4)
        self.dc_entry.grid(row=0, column=7, padx=5)
        
        # Cuenta
        ttk.Label(frame, text="Cuenta:").grid(row=0, column=8, sticky=tk.W)
        self.cuenta_entry = ttk.Entry(frame, width=12)
        self.cuenta_entry.grid(row=0, column=9, padx=5)
    
    def create_family_info_section(self):
        frame = ttk.LabelFrame(self.main_frame, text="Información Familiar", padding="10")
        frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Es principal
        ttk.Checkbutton(frame, text="Es socio principal", variable=self.es_principal, 
                       command=self.toggle_principal).grid(row=0, column=0, sticky=tk.W)
        
        # Socio principal (solo visible si no es principal)
        self.socio_principal_frame = ttk.Frame(frame)
        self.socio_principal_frame.grid(row=1, column=0, columnspan=2, sticky=tk.EW)
        ttk.Label(self.socio_principal_frame, text="Socio Principal:").pack(side=tk.LEFT)
        self.socio_principal_combo = ttk.Combobox(self.socio_principal_frame, 
                                                 textvariable=self.socio_principal_id)
        self.socio_principal_combo['values'] = [(s.id, s.nombre) for s in self.socios_principales]
        self.socio_principal_combo.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Número de personas
        ttk.Label(frame, text="Número de Personas:").grid(row=2, column=0, sticky=tk.W)
        self.num_pers_entry = ttk.Entry(frame, width=5)
        self.num_pers_entry.grid(row=2, column=1, padx=5)
        
        # Adheridos
        ttk.Label(frame, text="Adheridos:").grid(row=2, column=2, sticky=tk.W)
        self.adheridos_entry = ttk.Entry(frame, width=5)
        self.adheridos_entry.grid(row=2, column=3, padx=5)
        
        # Menores de 3 años
        ttk.Label(frame, text="Menores de 3 años:").grid(row=2, column=4, sticky=tk.W)
        self.menores_entry = ttk.Entry(frame, width=5)
        self.menores_entry.grid(row=2, column=5, padx=5)
    
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
        """Muestra u oculta el combo de socio principal según corresponda"""
        if self.es_principal.get():
            self.socio_principal_frame.grid_remove()
        else:
            self.socio_principal_frame.grid()
    
    def select_photo(self):
        """Permite al usuario seleccionar una foto"""
        file_path = filedialog.askopenfilename(
            title="Seleccionar Foto",
            filetypes=[("Imágenes", "*.png *.jpg *.jpeg *.gif *.bmp")]
        )
        if file_path:
            self.foto_path.set(file_path)
            self.show_photo_preview(file_path)
    
    def show_photo_preview(self, photo_path):
        """Muestra una vista previa de la foto seleccionada"""
        try:
            # Abrir y redimensionar la imagen
            image = Image.open(photo_path)
            image.thumbnail((200, 200))
            photo = ImageTk.PhotoImage(image)
            
            # Mostrar la imagen
            self.foto_label.configure(image=photo)
            self.foto_label.image = photo
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo cargar la imagen: {str(e)}")
    
    def load_socio_data(self):
        """Carga los datos del socio en el formulario"""
        if self.socio:
            # Datos básicos
            self.rgpd.set(self.socio.rgpd)
            self.codigo_socio_entry.insert(0, self.socio.codigo_socio or '')
            self.dni_entry.insert(0, self.socio.dni or '')
            self.nombre_entry.insert(0, self.socio.nombre or '')
            self.primer_apellido_entry.insert(0, self.socio.primer_apellido or '')
            self.segundo_apellido_entry.insert(0, self.socio.segundo_apellido or '')
            if self.socio.fecha_nacimiento:
                self.fecha_nacimiento_entry.set_date(self.socio.fecha_nacimiento)
            self.cuota_entry.insert(0, str(self.socio.cuota) if self.socio.cuota else '')
            
            # Información de contacto
            self.direccion_entry.insert(0, self.socio.direccion or '')
            self.poblacion_entry.insert(0, self.socio.poblacion or '')
            self.cp_entry.insert(0, self.socio.codigo_postal or '')
            self.provincia_entry.insert(0, self.socio.provincia or '')
            self.telefono_entry.insert(0, self.socio.telefono or '')
            self.telefono2_entry.insert(0, self.socio.telefono2 or '')
            self.email_entry.insert(0, self.socio.email or '')
            self.email2_entry.insert(0, self.socio.email2 or '')
            
            # Información bancaria
            self.iban_entry.insert(0, self.socio.iban or '')
            self.entidad_entry.insert(0, self.socio.entidad or '')
            self.oficina_entry.insert(0, self.socio.oficina or '')
            self.dc_entry.insert(0, self.socio.dc or '')
            self.cuenta_entry.insert(0, self.socio.cuenta_corriente or '')
            
            # Información familiar
            self.es_principal.set(self.socio.es_principal)
            if self.socio.socio_principal_id:
                self.socio_principal_id.set(self.socio.socio_principal_id)
            self.num_pers_entry.insert(0, str(self.socio.num_pers) if self.socio.num_pers else '')
            self.adheridos_entry.insert(0, str(self.socio.adherits) if self.socio.adherits else '')
            self.menores_entry.insert(0, str(self.socio.menor_3_anys) if self.socio.menor_3_anys else '')
            
            # Foto
            if self.socio.foto_path:
                self.foto_path.set(self.socio.foto_path)
                self.show_photo_preview(get_photo_path(self.socio.foto_path))
            
            self.toggle_principal()
    
    def guardar(self):
        """Guarda los datos del socio"""
        # Datos básicos
        self.rgpd_value = self.rgpd.get()
        self.codigo_socio_value = self.codigo_socio_entry.get()
        self.dni_value = self.dni_entry.get()
        self.nombre_value = self.nombre_entry.get()
        self.primer_apellido_value = self.primer_apellido_entry.get()
        self.segundo_apellido_value = self.segundo_apellido_entry.get()
        self.fecha_nacimiento_value = self.fecha_nacimiento_entry.get_date()
        self.cuota_value = float(self.cuota_entry.get()) if self.cuota_entry.get() else None
        
        # Información de contacto
        self.direccion_value = self.direccion_entry.get()
        self.poblacion_value = self.poblacion_entry.get()
        self.cp_value = self.cp_entry.get()
        self.provincia_value = self.provincia_entry.get()
        self.telefono_value = self.telefono_entry.get()
        self.telefono2_value = self.telefono2_entry.get()
        self.email_value = self.email_entry.get()
        self.email2_value = self.email2_entry.get()
        
        # Información bancaria
        self.iban_value = self.iban_entry.get()
        self.entidad_value = self.entidad_entry.get()
        self.oficina_value = self.oficina_entry.get()
        self.dc_value = self.dc_entry.get()
        self.cuenta_value = self.cuenta_entry.get()
        
        # Información familiar
        self.es_principal_value = self.es_principal.get()
        self.socio_principal_id_value = None if self.es_principal_value else self.socio_principal_id.get()
        self.num_pers_value = int(self.num_pers_entry.get()) if self.num_pers_entry.get() else None
        self.adheridos_value = int(self.adheridos_entry.get()) if self.adheridos_entry.get() else None
        self.menores_value = int(self.menores_entry.get()) if self.menores_entry.get() else None
        
        # Procesar la foto si se seleccionó una nueva
        self.foto_path_value = None
        if self.foto_path.get():
            try:
                self.foto_path_value = save_photo(self.foto_path.get())
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo guardar la foto: {str(e)}")
                return
        
        self.destroy()

def abrir_dialogo_socio(parent, socio=None, socios_principales=None):
    dialogo = SocioDialog(parent, socio, socios_principales)
    if hasattr(dialogo, 'nombre_value'):
        return {
            # Datos básicos
            'rgpd': dialogo.rgpd_value,
            'codigo_socio': dialogo.codigo_socio_value,
            'dni': dialogo.dni_value,
            'nombre': dialogo.nombre_value,
            'primer_apellido': dialogo.primer_apellido_value,
            'segundo_apellido': dialogo.segundo_apellido_value,
            'fecha_nacimiento': dialogo.fecha_nacimiento_value,
            'cuota': dialogo.cuota_value,
            
            # Información de contacto
            'direccion': dialogo.direccion_value,
            'poblacion': dialogo.poblacion_value,
            'codigo_postal': dialogo.cp_value,
            'provincia': dialogo.provincia_value,
            'telefono': dialogo.telefono_value,
            'telefono2': dialogo.telefono2_value,
            'email': dialogo.email_value,
            'email2': dialogo.email2_value,
            
            # Información bancaria
            'iban': dialogo.iban_value,
            'entidad': dialogo.entidad_value,
            'oficina': dialogo.oficina_value,
            'dc': dialogo.dc_value,
            'cuenta_corriente': dialogo.cuenta_value,
            
            # Información familiar
            'es_principal': dialogo.es_principal_value,
            'socio_principal_id': dialogo.socio_principal_id_value,
            'num_pers': dialogo.num_pers_value,
            'adherits': dialogo.adheridos_value,
            'menor_3_anys': dialogo.menores_value,
            
            # Foto
            'foto_path': dialogo.foto_path_value
        }
    return None

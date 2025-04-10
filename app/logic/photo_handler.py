import os
from PIL import Image
import shutil
import uuid

# Configuración
PHOTOS_DIR = "photos"
THUMBNAIL_SIZE = (200, 200)
ALLOWED_EXTENSIONS = {'.png', '.jpg', '.jpeg', '.gif', '.bmp'}

def ensure_photos_dir():
    """Asegura que el directorio de fotos existe"""
    if not os.path.exists(PHOTOS_DIR):
        os.makedirs(PHOTOS_DIR)

def get_file_extension(filename):
    """Obtiene la extensión de un archivo"""
    return os.path.splitext(filename)[1].lower()

def is_valid_image(file_path):
    """Verifica si el archivo es una imagen válida"""
    if not os.path.exists(file_path):
        return False
    
    extension = get_file_extension(file_path)
    if extension not in ALLOWED_EXTENSIONS:
        return False
    
    try:
        with Image.open(file_path) as img:
            img.verify()
        return True
    except:
        return False

def optimize_image(source_path, target_path):
    """Optimiza una imagen para su almacenamiento"""
    with Image.open(source_path) as img:
        # Convertir a RGB si es necesario
        if img.mode in ('RGBA', 'P'):
            img = img.convert('RGB')
        
        # Redimensionar si es muy grande
        if img.size[0] > 800 or img.size[1] > 800:
            img.thumbnail((800, 800))
        
        # Guardar con compresión
        img.save(target_path, 'JPEG', quality=85, optimize=True)

def save_photo(source_path):
    """
    Guarda una foto de socio en el sistema
    
    Args:
        source_path: Ruta de la imagen original
    
    Returns:
        str: Nombre del archivo guardado
    
    Raises:
        ValueError: Si la imagen no es válida
    """
    if not is_valid_image(source_path):
        raise ValueError("El archivo no es una imagen válida")
    
    ensure_photos_dir()
    
    # Generar nombre único para la foto
    filename = f"{uuid.uuid4()}.jpg"
    target_path = os.path.join(PHOTOS_DIR, filename)
    
    # Optimizar y guardar la imagen
    optimize_image(source_path, target_path)
    
    return filename

def get_photo_path(filename):
    """
    Obtiene la ruta completa de una foto
    
    Args:
        filename: Nombre del archivo de la foto
    
    Returns:
        str: Ruta completa del archivo
    """
    if not filename:
        return None
    
    return os.path.join(PHOTOS_DIR, filename)

def delete_photo(filename):
    """
    Elimina una foto del sistema
    
    Args:
        filename: Nombre del archivo a eliminar
    """
    if not filename:
        return
    
    photo_path = get_photo_path(filename)
    if os.path.exists(photo_path):
        os.remove(photo_path) 
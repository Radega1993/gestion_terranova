import os
import shutil
from datetime import datetime
from PIL import Image
import uuid

class PhotoHandler:
    def __init__(self, base_path="photos"):
        self.base_path = base_path
        if not os.path.exists(base_path):
            os.makedirs(base_path)

    def save_photo(self, photo_path, socio_id):
        """
        Guarda una foto para un socio, reemplazando la anterior si existe.
        
        Args:
            photo_path (str): Ruta temporal de la foto a guardar
            socio_id (int): ID del socio
            
        Returns:
            str: Ruta donde se guardó la foto
        """
        # Crear directorio para el socio si no existe
        socio_dir = os.path.join(self.base_path, str(socio_id))
        if not os.path.exists(socio_dir):
            os.makedirs(socio_dir)

        # Generar nombre único para la foto
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        unique_id = str(uuid.uuid4())[:8]
        new_filename = f"photo_{timestamp}_{unique_id}.jpg"
        new_path = os.path.join(socio_dir, new_filename)

        # Procesar y guardar la imagen
        with Image.open(photo_path) as img:
            # Redimensionar si es necesario (por ejemplo, máximo 800x800)
            img.thumbnail((800, 800))
            # Convertir a RGB si es necesario
            if img.mode != 'RGB':
                img = img.convert('RGB')
            # Guardar con compresión
            img.save(new_path, 'JPEG', quality=85)

        # Eliminar foto anterior si existe
        old_photos = [f for f in os.listdir(socio_dir) if f.startswith('photo_')]
        for old_photo in old_photos:
            if old_photo != new_filename:
                os.remove(os.path.join(socio_dir, old_photo))

        return new_path

    def get_photo_path(self, socio_id):
        """
        Obtiene la ruta de la foto actual de un socio.
        
        Args:
            socio_id (int): ID del socio
            
        Returns:
            str: Ruta de la foto o None si no existe
        """
        socio_dir = os.path.join(self.base_path, str(socio_id))
        if not os.path.exists(socio_dir):
            return None

        photos = [f for f in os.listdir(socio_dir) if f.startswith('photo_')]
        if not photos:
            return None

        # Devolver la foto más reciente
        latest_photo = max(photos, key=lambda x: os.path.getctime(os.path.join(socio_dir, x)))
        return os.path.join(socio_dir, latest_photo)

    def delete_photo(self, socio_id):
        """
        Elimina todas las fotos de un socio.
        
        Args:
            socio_id (int): ID del socio
        """
        socio_dir = os.path.join(self.base_path, str(socio_id))
        if os.path.exists(socio_dir):
            shutil.rmtree(socio_dir) 
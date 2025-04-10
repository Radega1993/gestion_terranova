import os
import shutil
import tempfile
from PIL import Image
import pytest
from app.utils.photo_handler import PhotoHandler

@pytest.fixture
def temp_dir():
    # Crear un directorio temporal para las pruebas
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    # Limpiar después de las pruebas
    shutil.rmtree(temp_dir)

@pytest.fixture
def photo_handler(temp_dir):
    return PhotoHandler(base_path=temp_dir)

@pytest.fixture
def sample_image():
    # Crear una imagen de prueba
    img = Image.new('RGB', (100, 100), color='red')
    temp_file = tempfile.NamedTemporaryFile(suffix='.jpg', delete=False)
    img.save(temp_file.name)
    yield temp_file.name
    os.unlink(temp_file.name)

def test_save_photo(photo_handler, sample_image):
    # Probar guardar una foto
    socio_id = 1
    saved_path = photo_handler.save_photo(sample_image, socio_id)
    
    assert os.path.exists(saved_path)
    assert os.path.dirname(saved_path) == os.path.join(photo_handler.base_path, str(socio_id))

def test_get_photo_path(photo_handler, sample_image):
    # Probar obtener la ruta de una foto
    socio_id = 1
    photo_handler.save_photo(sample_image, socio_id)
    
    photo_path = photo_handler.get_photo_path(socio_id)
    assert photo_path is not None
    assert os.path.exists(photo_path)

def test_delete_photo(photo_handler, sample_image):
    # Probar eliminar una foto
    socio_id = 1
    photo_handler.save_photo(sample_image, socio_id)
    
    photo_handler.delete_photo(socio_id)
    assert not os.path.exists(os.path.join(photo_handler.base_path, str(socio_id)))

def test_photo_replacement(photo_handler, sample_image):
    # Probar que se reemplaza la foto anterior
    socio_id = 1
    
    # Guardar primera foto
    first_path = photo_handler.save_photo(sample_image, socio_id)
    
    # Crear y guardar segunda foto
    img = Image.new('RGB', (100, 100), color='blue')
    temp_file = tempfile.NamedTemporaryFile(suffix='.jpg', delete=False)
    img.save(temp_file.name)
    
    second_path = photo_handler.save_photo(temp_file.name, socio_id)
    os.unlink(temp_file.name)
    
    # Verificar que la primera foto fue eliminada
    assert not os.path.exists(first_path)
    assert os.path.exists(second_path)
    
    # Verificar que solo existe una foto
    photos = [f for f in os.listdir(os.path.join(photo_handler.base_path, str(socio_id))) 
             if f.startswith('photo_')]
    assert len(photos) == 1 
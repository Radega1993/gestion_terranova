import os

# Obtener la ruta absoluta del directorio del proyecto
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Ruta de la base de datos
DATABASE_PATH = os.path.join(BASE_DIR, 'geston_terranova.db')

# URL de la base de datos
DATABASE_URL = f'sqlite:///{DATABASE_PATH}' 
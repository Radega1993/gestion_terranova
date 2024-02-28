# Configuración de la conexión a la base de datos
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database.models import Base

# Conexión a SQLite
engine = create_engine('sqlite:///geston_terranova.db', echo=True)

# Crear todas las tablas definidas en Base
Base.metadata.create_all(engine)

# Crear una fábrica de sesiones vinculada al motor
Session = sessionmaker(bind=engine)

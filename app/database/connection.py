# En connection.py
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import QueuePool
from .models import Base

# Configuración de la base de datos
DATABASE_URL = "sqlite:///gestion_terranova.db"

# Crear el motor con configuración optimizada
engine = create_engine(
    DATABASE_URL,
    poolclass=QueuePool,
    pool_size=10,
    max_overflow=20,
    pool_timeout=60,
    pool_recycle=1800,
    connect_args={
        "timeout": 60,
        "check_same_thread": False,
        "isolation_level": None  # Autocommit mode
    }
)

# Configurar SQLite para mejor concurrencia
@event.listens_for(engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA journal_mode=WAL")
    cursor.execute("PRAGMA busy_timeout=10000")  # 10 segundos
    cursor.execute("PRAGMA synchronous=NORMAL")
    cursor.execute("PRAGMA cache_size=-2000")  # 2MB de cache
    cursor.execute("PRAGMA temp_store=MEMORY")
    cursor.close()

# Crear la sesión con configuración específica
Session = sessionmaker(
    bind=engine,
    expire_on_commit=False,  # Evitar problemas con objetos expirados
    autoflush=True  # Autoflush para mantener la consistencia
)

# Asegurar que las tablas existan
Base.metadata.create_all(engine)

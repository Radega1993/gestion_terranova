# En connection.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from .models import Base  # Asegúrate de que el path sea correcto

DATABASE_URL = 'sqlite:///geston_terranova.db'
engine = create_engine(DATABASE_URL, echo=True)
Session = sessionmaker(bind=engine)

Base.metadata.create_all(engine)

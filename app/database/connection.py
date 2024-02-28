# En connection.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from .models import Base  # Asegúrate de que el path sea correcto

engine = create_engine('sqlite:///geston_terranova.db', echo=True)
Session = sessionmaker(bind=engine)

Base.metadata.create_all(engine)

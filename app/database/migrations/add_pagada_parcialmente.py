from sqlalchemy import create_engine, Column, Boolean, text
from app.database.database import DATABASE_URL

def migrate():
    engine = create_engine(DATABASE_URL)
    
    # Añadir la columna pagada_parcialmente si no existe
    with engine.connect() as conn:
        # Verificar si la columna existe usando PRAGMA para SQLite
        result = conn.execute(text("PRAGMA table_info(deudas)"))
        columns = result.fetchall()
        column_exists = any(col[1] == 'pagada_parcialmente' for col in columns)
        
        if not column_exists:
            conn.execute(text("ALTER TABLE deudas ADD COLUMN pagada_parcialmente BOOLEAN DEFAULT FALSE"))
            conn.commit()
            print("Columna pagada_parcialmente añadida correctamente")
        else:
            print("La columna pagada_parcialmente ya existe")

if __name__ == "__main__":
    migrate() 
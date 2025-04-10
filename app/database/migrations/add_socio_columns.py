from sqlalchemy import create_engine, text, inspect
from app.database.database import DATABASE_URL
from datetime import datetime

def column_exists(inspector, table_name, column_name):
    """Verifica si una columna existe en una tabla"""
    columns = [c['name'] for c in inspector.get_columns(table_name)]
    return column_name in columns

def migrate():
    """Añade las nuevas columnas a la tabla socios"""
    engine = create_engine(DATABASE_URL)
    inspector = inspect(engine)
    
    with engine.connect() as conn:
        # Añadir nuevas columnas si no existen
        if not column_exists(inspector, 'socios', 'fecha_registro'):
            conn.execute(text("ALTER TABLE socios ADD COLUMN fecha_registro DATETIME"))
            # Actualizar los registros existentes con la fecha actual
            current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            conn.execute(text(f"UPDATE socios SET fecha_registro = '{current_time}'"))
        
        if not column_exists(inspector, 'socios', 'activo'):
            conn.execute(text("ALTER TABLE socios ADD COLUMN activo BOOLEAN DEFAULT 1"))
        
        if not column_exists(inspector, 'socios', 'es_principal'):
            conn.execute(text("ALTER TABLE socios ADD COLUMN es_principal BOOLEAN DEFAULT 1"))
        
        if not column_exists(inspector, 'socios', 'socio_principal_id'):
            conn.execute(text("ALTER TABLE socios ADD COLUMN socio_principal_id INTEGER REFERENCES socios(id)"))
        
        if not column_exists(inspector, 'socios', 'foto_path'):
            conn.execute(text("ALTER TABLE socios ADD COLUMN foto_path VARCHAR(255)"))
        
        # Crear tabla miembros_familia si no existe
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS miembros_familia (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                socio_principal_id INTEGER NOT NULL REFERENCES socios(id),
                socio_miembro_id INTEGER NOT NULL REFERENCES socios(id),
                fecha_registro DATETIME,
                activo BOOLEAN DEFAULT 1,
                FOREIGN KEY (socio_principal_id) REFERENCES socios(id),
                FOREIGN KEY (socio_miembro_id) REFERENCES socios(id)
            );
        """))
        
        conn.commit()

if __name__ == "__main__":
    migrate() 
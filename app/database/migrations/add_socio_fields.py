from sqlalchemy import create_engine, text, inspect
from app.database.connection import DATABASE_URL

def column_exists(inspector, table_name, column_name):
    columns = [col['name'] for col in inspector.get_columns(table_name)]
    return column_name in columns

def migrate():
    engine = create_engine(DATABASE_URL)
    inspector = inspect(engine)
    
    with engine.connect() as conn:
        # Lista de columnas a añadir con sus tipos
        columns = [
            ('rgpd', 'BOOLEAN DEFAULT FALSE'),
            ('codigo_socio', 'VARCHAR(10) UNIQUE'),
            ('canvi', 'VARCHAR(50)'),
            ('casa', 'INTEGER'),
            ('total_soc', 'INTEGER'),
            ('num_pers', 'INTEGER'),
            ('adherits', 'INTEGER'),
            ('menor_3_anys', 'INTEGER'),
            ('cuota', 'FLOAT'),
            ('dni', 'VARCHAR(9)'),
            ('primer_apellido', 'VARCHAR(100)'),
            ('segundo_apellido', 'VARCHAR(100)'),
            ('direccion', 'VARCHAR(200)'),
            ('poblacion', 'VARCHAR(100)'),
            ('codigo_postal', 'VARCHAR(5)'),
            ('provincia', 'VARCHAR(100)'),
            ('iban', 'VARCHAR(4)'),
            ('entidad', 'VARCHAR(4)'),
            ('oficina', 'VARCHAR(4)'),
            ('dc', 'VARCHAR(2)'),
            ('cuenta_corriente', 'VARCHAR(10)'),
            ('telefono', 'VARCHAR(15)'),
            ('telefono2', 'VARCHAR(15)'),
            ('email2', 'VARCHAR(100)'),
            ('observaciones', 'TEXT'),
            ('fecha_nacimiento', 'DATE')
        ]
        
        # Añadir cada columna individualmente
        for column_name, column_type in columns:
            if not column_exists(inspector, 'socios', column_name):
                try:
                    conn.execute(text(f"ALTER TABLE socios ADD COLUMN {column_name} {column_type}"))
                    print(f"Columna {column_name} añadida correctamente")
                except Exception as e:
                    print(f"Error al añadir la columna {column_name}: {str(e)}")
        
        # Renombrar columna correo_electronico a email si existe
        if column_exists(inspector, 'socios', 'correo_electronico'):
            try:
                conn.execute(text("ALTER TABLE socios RENAME COLUMN correo_electronico TO email"))
                print("Columna correo_electronico renombrada a email correctamente")
            except Exception as e:
                print(f"Error al renombrar la columna correo_electronico: {str(e)}")
        
        conn.commit()
        print("Migración completada")

if __name__ == '__main__':
    migrate() 
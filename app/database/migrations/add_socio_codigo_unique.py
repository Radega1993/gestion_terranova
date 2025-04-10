from sqlalchemy import create_engine, text
from app.database.connection import DATABASE_URL

def migrate():
    engine = create_engine(DATABASE_URL)
    
    with engine.connect() as conn:
        try:
            # Añadir la columna codigo_socio si no existe
            conn.execute(text("ALTER TABLE socios ADD COLUMN codigo_socio VARCHAR(10)"))
            print("Columna codigo_socio añadida correctamente")
        except Exception as e:
            print(f"La columna codigo_socio ya existe o hubo un error: {str(e)}")
        
        try:
            # Crear un índice UNIQUE para la columna codigo_socio
            conn.execute(text("CREATE UNIQUE INDEX IF NOT EXISTS uq_socio_codigo ON socios(codigo_socio) WHERE codigo_socio IS NOT NULL"))
            print("Índice UNIQUE creado correctamente para codigo_socio")
        except Exception as e:
            print(f"Error al crear el índice UNIQUE: {str(e)}")
        
        conn.commit()
        print("Migración completada")

if __name__ == '__main__':
    migrate() 
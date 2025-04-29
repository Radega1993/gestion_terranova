from app.database.connection import Session
from app.database.models import Usuario
from sqlalchemy import text

def column_exists(session, table, column):
    """Verifica si una columna existe en una tabla"""
    result = session.execute(
        text(f"SELECT COUNT(*) FROM pragma_table_info('{table}') WHERE name='{column}'")
    ).scalar()
    return bool(result)

def migrate():
    """Añade el campo validado a la tabla de usuarios y establece los valores por defecto"""
    session = Session()
    try:
        # Verificar si la columna ya existe
        if not column_exists(session, 'usuarios', 'validado'):
            # Añadir el campo validado
            session.execute(text('ALTER TABLE usuarios ADD COLUMN validado BOOLEAN DEFAULT FALSE'))
            
            # Establecer validado=True para todos los usuarios existentes
            session.execute(text('UPDATE usuarios SET validado = TRUE'))
            
            session.commit()
            print("Migración completada: Campo 'validado' añadido a la tabla usuarios")
        else:
            print("El campo 'validado' ya existe en la tabla usuarios")
    except Exception as e:
        print(f"Error durante la migración: {e}")
        session.rollback()
    finally:
        session.close() 
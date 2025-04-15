from app.database.connection import Session
from app.database.models import Usuario

def init_db():
    """Inicializa la base de datos con un usuario administrador por defecto"""
    session = Session()
    try:
        # Verificar si ya existe un usuario administrador
        admin = session.query(Usuario).filter_by(user='admin').first()
        if not admin:
            # Crear usuario administrador
            admin = Usuario(
                nombre='Administrador',
                user='admin',
                tipo_usuario='administrador',
                activo=True
            )
            admin.set_password('admin')  # Contraseña por defecto
            session.add(admin)
            session.commit()
            print("Usuario administrador creado con éxito")
        else:
            print("El usuario administrador ya existe")
    except Exception as e:
        print(f"Error al crear el usuario administrador: {e}")
        session.rollback()
    finally:
        session.close()

if __name__ == '__main__':
    init_db() 
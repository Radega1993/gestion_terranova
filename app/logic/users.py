# Autenticación y gestión de usuarios

from app.database.connection import Session
from app.database.models import Usuario

def crear_usuario(nombre, user, tipo_usuario, contrasena, validado=False):
    with Session() as session:
        nuevo_usuario = Usuario(nombre=nombre, user=user, tipo_usuario=tipo_usuario)
        nuevo_usuario.set_password(contrasena, validado)
        session.add(nuevo_usuario)
        session.commit()
        return nuevo_usuario.id

def obtener_usuario_por_user(user):
    with Session() as session:
        usuario = session.query(Usuario).filter_by(user=user).one()
        return usuario

def obtener_usuarios():
    with Session() as session:
        return session.query(Usuario).filter(Usuario.activo == True).all()

def actualizar_usuario(id_usuario, nombre=None, user=None, tipo_usuario=None, password=None):
    with Session() as session:
        usuario = session.query(Usuario).filter_by(id=id_usuario).one()
        if nombre:
            usuario.nombre = nombre
        if user:
            usuario.user = user
        if tipo_usuario:
            usuario.tipo_usuario = tipo_usuario
        if password:
            usuario.set_password(password)
        session.commit()

def eliminar_usuario(id_usuario):
    with Session() as session:
        usuario = session.query(Usuario).filter_by(id=id_usuario).one()
        
        # Verificar si es el último administrador
        if usuario.tipo_usuario == 'Administrador':
            admin_count = session.query(Usuario).filter_by(
                tipo_usuario='Administrador',
                activo=True
            ).count()
            if admin_count <= 1:
                raise Exception("No se puede eliminar el último usuario administrador")
        
        usuario.activo = False
        session.commit()

def obtener_usuario_por_id(id_usuario):
    with Session() as session:
        return session.query(Usuario).filter_by(id=id_usuario).one()

def toggle_validacion_usuario(id_usuario):
    with Session() as session:
        usuario = session.query(Usuario).filter_by(id=id_usuario).one()
        
        # No permitir invalidar administradores
        if usuario.tipo_usuario == 'Administrador':
            raise Exception("No se puede invalidar a un administrador")
        
        # Si vamos a invalidar, verificar que quede al menos un administrador válido
        if usuario.validado:
            admin_count = session.query(Usuario).filter_by(
                tipo_usuario='Administrador',
                validado=True,
                activo=True
            ).count()
            if admin_count <= 1:
                raise Exception("No se puede invalidar este usuario. Debe haber al menos un administrador válido en el sistema.")
        
        usuario.validado = not usuario.validado
        session.commit()

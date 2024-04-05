# Autenticación y gestión de usuarios

from app.database.connection import Session
from app.database.models import Usuario

def crear_usuario(nombre, user, tipo_usuario, contrasena):
    with Session() as session:
        nuevo_usuario = Usuario(nombre=nombre, user=user, tipo_usuario=tipo_usuario)
        nuevo_usuario.set_password(contrasena)
        session.add(nuevo_usuario)
        session.commit()
        return nuevo_usuario.id

def obtener_usuario_por_user(user):
    with Session() as session:
        usuario = session.query(Usuario).filter_by(user=user).one()
        return usuario

def obtener_usuarios():
    with Session() as session:
        usuarios = session.query(Usuario).filter(Usuario.activo == True).all()
        return [
            {
                "id": usuario.id, 
                "nombre": usuario.nombre, 
                "user": usuario.user, 
                "tipo_usuario": usuario.tipo_usuario
            } 
            for usuario in usuarios
        ]

def actualizar_usuario(id_usuario, nombre=None, tipo_usuario=None):
    with Session() as session:
        usuario = session.query(Usuario).filter_by(id=id_usuario).one()
        if nombre:
            usuario.nombre = nombre
        if tipo_usuario:
            usuario.tipo_usuario = tipo_usuario
        session.commit()


def eliminar_usuario(id_usuario):
    with Session() as session:
        usuario = session.query(Usuario).filter_by(id=id_usuario).one()
        usuario.activo = False
        session.commit()

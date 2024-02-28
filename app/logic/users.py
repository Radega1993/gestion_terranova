# Autenticación y gestión de usuarios

from app.database.connection import Session
from app.database.models import Usuario

def crear_usuario(nombre, correo_electronico, tipo_usuario, contrasena):
    with Session() as session:
        nuevo_usuario = Usuario(nombre=nombre, correo_electronico=correo_electronico, tipo_usuario=tipo_usuario)
        nuevo_usuario.set_password(contrasena)
        session.add(nuevo_usuario)
        session.commit()
        return nuevo_usuario.id

def obtener_usuario_por_correo(correo_electronico):
    with Session() as session:
        usuario = session.query(Usuario).filter_by(correo_electronico=correo_electronico).one()
        return usuario

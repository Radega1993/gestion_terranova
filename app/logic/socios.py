# En logic/socios.py
from app.database.connection import Session
from app.database.models import Socio

def crear_socio(nombre, correo_electronico):
    with Session() as session:
        socio = Socio(nombre=nombre, correo_electronico=correo_electronico)
        session.add(socio)
        session.commit()
        return socio.id

def obtener_socios():
    with Session() as session:
        return session.query(Socio).all()

def obtener_socio_por_id(socio_id):
    with Session() as session:
        socio = session.query(Socio).filter_by(id=socio_id).one_or_none()
        return socio

def desactivar_socio(socio_id):
    with Session() as session:
        socio = session.query(Socio).filter_by(id=socio_id).one()
        socio.activo = False
        session.commit()

def activar_socio(socio_id):
    with Session() as session:
        socio = session.query(Socio).filter_by(id=socio_id).one()
        socio.activo = True
        session.commit()

def actualizar_socio(socio_id, nombre, correo_electronico):
    with Session() as session:
        socio = session.query(Socio).filter_by(id=socio_id).one()
        socio.nombre = nombre
        socio.correo_electronico = correo_electronico
        session.commit()
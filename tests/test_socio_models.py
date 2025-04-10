import pytest
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database.models import Base, Socio, MiembroFamilia

@pytest.fixture
def engine():
    return create_engine('sqlite:///:memory:')

@pytest.fixture
def session(engine):
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()
    Base.metadata.drop_all(engine)

def test_create_socio_principal(session):
    # Crear un socio principal
    socio = Socio(
        nombre="Juan Pérez",
        correo_electronico="juan@example.com",
        es_principal=True
    )
    session.add(socio)
    session.commit()
    
    assert socio.id is not None
    assert socio.es_principal is True
    assert socio.socio_principal_id is None

def test_create_socio_miembro(session):
    # Crear un socio principal
    principal = Socio(
        nombre="Juan Pérez",
        correo_electronico="juan@example.com",
        es_principal=True
    )
    session.add(principal)
    session.commit()
    
    # Crear un miembro de la familia
    miembro = Socio(
        nombre="María Pérez",
        correo_electronico="maria@example.com",
        es_principal=False,
        socio_principal_id=principal.id
    )
    session.add(miembro)
    session.commit()
    
    assert miembro.id is not None
    assert miembro.es_principal is False
    assert miembro.socio_principal_id == principal.id

def test_familia_relationship(session):
    # Crear un socio principal
    principal = Socio(
        nombre="Juan Pérez",
        correo_electronico="juan@example.com",
        es_principal=True
    )
    session.add(principal)
    session.commit()
    
    # Crear miembros de la familia
    miembros = [
        Socio(
            nombre=f"Miembro {i}",
            correo_electronico=f"miembro{i}@example.com",
            es_principal=False,
            socio_principal_id=principal.id
        )
        for i in range(3)
    ]
    session.add_all(miembros)
    session.commit()
    
    # Verificar la relación
    assert len(principal.miembros_familia) == 3
    for miembro in miembros:
        assert miembro in principal.miembros_familia

def test_miembro_familia_model(session):
    # Crear un socio principal
    principal = Socio(
        nombre="Juan Pérez",
        correo_electronico="juan@example.com",
        es_principal=True
    )
    session.add(principal)
    session.commit()
    
    # Crear un miembro
    miembro = Socio(
        nombre="María Pérez",
        correo_electronico="maria@example.com",
        es_principal=False
    )
    session.add(miembro)
    session.commit()
    
    # Crear la relación en la tabla miembros_familia
    relacion = MiembroFamilia(
        socio_principal_id=principal.id,
        socio_miembro_id=miembro.id
    )
    session.add(relacion)
    session.commit()
    
    assert relacion.id is not None
    assert relacion.socio_principal_id == principal.id
    assert relacion.socio_miembro_id == miembro.id
    assert relacion.activo is True
    assert isinstance(relacion.fecha_registro, datetime) 
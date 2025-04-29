import pytest
import random
import uuid
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database.models import Base, Usuario
from app.logic.users import crear_usuario, obtener_usuarios, eliminar_usuario
from app.database.connection import Session, engine

def test_create_multiple_users():
    """Test para crear múltiples usuarios y verificar que se crean correctamente"""
    # Usar la sesión de la base de datos real
    with Session() as session:
        # Crear 20 usuarios
        usuarios = []
        for i in range(20):
            tipo = Usuario.TIPOS_USUARIO[i % len(Usuario.TIPOS_USUARIO)]  # Distribuir tipos de manera cíclica
            usuario = Usuario(
                nombre=f"Usuario {i+1}",
                user=f"user{i+1}",  # Nombre de usuario simple
                tipo_usuario=tipo,
                contrasena_hash="hash123",
                activo=True,
                validado=True
            )
            session.add(usuario)
            usuarios.append(usuario)
        
        session.commit()
        
        # Verificar que se crearon correctamente
        for i, usuario in enumerate(usuarios):
            assert usuario.nombre == f"Usuario {i+1}"
            assert usuario.user == f"user{i+1}"
            assert usuario.tipo_usuario in Usuario.TIPOS_USUARIO
            assert usuario.activo is True
            assert usuario.validado is True
        
        # Verificar que están en la base de datos
        usuarios_db = session.query(Usuario).filter(Usuario.activo == True).all()
        assert len(usuarios_db) >= 20  # Debe haber al menos 20 usuarios activos
        
        # Verificar distribución de tipos
        tipos_count = {tipo: 0 for tipo in Usuario.TIPOS_USUARIO}
        for usuario in usuarios_db:
            tipos_count[usuario.tipo_usuario] += 1
        
        # Verificar que hay una distribución razonable de tipos
        for tipo, count in tipos_count.items():
            assert count >= 6  # Debe haber al menos 6 usuarios de cada tipo

def test_delete_multiple_users():
    """Test para eliminar múltiples usuarios y limpiar la base de datos."""
    # Usar la sesión de la base de datos real
    with Session() as session:
        # Tipos de usuario disponibles
        tipos_usuario = Usuario.TIPOS_USUARIO
        
        # Crear 20 usuarios con diferentes tipos
        usuarios_creados = []
        for i in range(20):
            # Seleccionar un tipo de usuario aleatorio
            tipo_usuario = random.choice(tipos_usuario)
            
            # Crear el usuario con un nombre de usuario único
            nombre = f"Usuario Test {i+1}"
            user = f"usuario{i+1}_{uuid.uuid4().hex[:8]}"  # Añadir un sufijo único
            password = f"password{i+1}"
            
            # Crear el usuario directamente en la sesión
            usuario = Usuario(
                nombre=nombre,
                user=user,
                tipo_usuario=tipo_usuario,
                validado=True,
                activo=True
            )
            usuario.set_password(password)
            session.add(usuario)
            session.commit()
            
            # Guardar el ID del usuario creado
            usuarios_creados.append(usuario.id)
        
        # Verificar que se crearon todos los usuarios
        assert len(usuarios_creados) == 20
        
        # Eliminar todos los usuarios creados
        for user_id in usuarios_creados:
            usuario = session.query(Usuario).filter_by(id=user_id).first()
            usuario.activo = False
            session.commit()
        
        # Verificar que los usuarios fueron eliminados (marcados como inactivos)
        for user_id in usuarios_creados:
            usuario = session.query(Usuario).filter_by(id=user_id).first()
            assert usuario is not None
            assert usuario.activo is False
        
        # Verificar que no hay usuarios activos de los que creamos
        usuarios_activos = session.query(Usuario).filter(Usuario.activo == True).all()
        usuarios_activos_ids = [usuario.id for usuario in usuarios_activos]
        for user_id in usuarios_creados:
            assert user_id not in usuarios_activos_ids

def test_create_and_delete_users_with_logic_functions():
    """Test para crear y eliminar múltiples usuarios utilizando las funciones de la lógica de negocio."""
    # Tipos de usuario disponibles
    tipos_usuario = Usuario.TIPOS_USUARIO
    
    # Crear 20 usuarios con diferentes tipos
    usuarios_creados = []
    for i in range(20):
        # Seleccionar un tipo de usuario aleatorio
        tipo_usuario = random.choice(tipos_usuario)
        
        # Crear el usuario con un nombre de usuario único
        nombre = f"Usuario Test Logic {i+1}"
        user = f"usuario_logic_{i+1}_{uuid.uuid4().hex[:8]}"  # Añadir un sufijo único
        password = f"password{i+1}"
        
        # Crear el usuario usando la función de la lógica
        user_id = crear_usuario(nombre, user, tipo_usuario, password, validado=True)
        usuarios_creados.append(user_id)
        
        # Verificar que el usuario se creó correctamente
        with Session() as session:
            usuario = session.query(Usuario).filter_by(id=user_id).first()
            assert usuario is not None
            assert usuario.nombre == nombre
            assert usuario.user == user
            assert usuario.tipo_usuario == tipo_usuario
            assert usuario.validado is True
            assert usuario.activo is True
    
    # Verificar que se crearon todos los usuarios
    assert len(usuarios_creados) == 20
    
    # Verificar que podemos obtener todos los usuarios
    usuarios = obtener_usuarios()
    assert len(usuarios) >= 20  # Debe haber al menos 20 usuarios activos
    
    # Eliminar todos los usuarios creados
    for user_id in usuarios_creados:
        eliminar_usuario(user_id)
    
    # Verificar que los usuarios fueron eliminados (marcados como inactivos)
    with Session() as session:
        for user_id in usuarios_creados:
            usuario = session.query(Usuario).filter_by(id=user_id).first()
            assert usuario is not None
            assert usuario.activo is False
        
        # Verificar que no hay usuarios activos de los que creamos
        usuarios_activos = session.query(Usuario).filter(Usuario.activo == True).all()
        usuarios_activos_ids = [usuario.id for usuario in usuarios_activos]
        for user_id in usuarios_creados:
            assert user_id not in usuarios_activos_ids 
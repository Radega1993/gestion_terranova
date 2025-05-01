import pytest
import random
from datetime import datetime, date
from sqlalchemy import create_engine, func
from sqlalchemy.orm import sessionmaker
from app.database.models import Base, Socio
from app.database.connection import Session, engine

def get_next_codigo_socio(session):
    """Obtiene el siguiente código de socio disponible."""
    # Buscar el último código que siga el patrón AETXXX
    ultimo_codigo = session.query(Socio.codigo_socio)\
        .filter(Socio.codigo_socio.like('AET%'))\
        .filter(Socio.es_principal == True)\
        .order_by(Socio.codigo_socio.desc())\
        .first()

    if ultimo_codigo and ultimo_codigo[0]:
        # Extraer el número y sumar 1
        try:
            # Asegurarse de que el código sigue el formato AETXXX
            if len(ultimo_codigo[0]) >= 6 and ultimo_codigo[0][:3] == 'AET':
                ultimo_num = int(ultimo_codigo[0][3:6])
                print(f"\nÚltimo código de socio encontrado: {ultimo_codigo[0]}")
                print(f"Empezando desde el código: AET{ultimo_num + 1:03d}")
                return ultimo_num + 1
        except ValueError:
            pass
    
    # Si no hay códigos válidos, empezar desde 1
    print("\nNo se encontraron códigos de socio válidos. Empezando desde AET001")
    return 1

def cleanup_test_data(session):
    """Limpia los datos de prueba de la base de datos."""
    try:
        # Eliminar socios de prueba (aquellos con email @example.com)
        session.query(Socio).filter(
            Socio.email.like('%@example.com')
        ).delete(synchronize_session=False)
        session.commit()
        print("Datos de prueba eliminados correctamente")
    except Exception as e:
        print(f"Error al limpiar datos de prueba: {e}")
        session.rollback()

def test_generate_socios_with_families(request):
    """Test para generar 20 socios principales con unidades familiares aleatorias."""
    session = Session()
    cleanup_requested = request.config.getoption("--cleanup", default=False)
    
    try:
        # Limpiar datos anteriores de prueba si se solicita
        if cleanup_requested:
            print("\nLimpiando datos de prueba anteriores...")
            cleanup_test_data(session)
        
        # Obtener el siguiente número de socio disponible
        siguiente_num = get_next_codigo_socio(session)
        print(f"\nComenzando desde el código de socio AET{siguiente_num:03d}")
        
        # Generar 20 socios principales
        for i in range(20):
            # Crear socio principal
            socio_principal = Socio(
                nombre=f"Principal {i+1}",
                primer_apellido="Apellido1",
                segundo_apellido="Apellido2",
                dni=f"{random.randint(10000000, 99999999)}{random.choice('ABCDEFGHIJKLMNOPQRSTUVWXYZ')}",
                email=f"principal{i+1}@example.com",
                direccion=f"Calle Principal {i+1}",
                poblacion="Ciudad",
                codigo_postal="12345",
                provincia="Provincia",
                telefono=f"6{random.randint(10000000, 99999999)}",
                fecha_nacimiento=date(1980, 1, 1),
                fecha_registro=datetime.now(),
                activo=True,
                es_principal=True,
                codigo_socio=f"AET{siguiente_num + i:03d}",  # Formato: AET001, AET002, etc.
                num_pers=1,  # Se actualizará después con el total de la familia
                total_soc=1  # Se actualizará después con el total de la familia
            )
            session.add(socio_principal)
            session.flush()  # Para obtener el ID del socio principal
            
            # Generar número aleatorio de miembros de familia (0-10)
            num_miembros = random.randint(0, 10)
            miembros_familia = []
            
            # Crear miembros de la familia
            for j in range(num_miembros):
                miembro = Socio(
                    nombre=f"Miembro {j+1} de Principal {i+1}",
                    primer_apellido="Apellido1",
                    segundo_apellido="Apellido2",
                    dni=f"{random.randint(10000000, 99999999)}{random.choice('ABCDEFGHIJKLMNOPQRSTUVWXYZ')}",
                    email=f"miembro{j+1}_principal{i+1}@example.com",
                    direccion=f"Calle Principal {i+1}",
                    poblacion="Ciudad",
                    codigo_postal="12345",
                    provincia="Provincia",
                    telefono=f"6{random.randint(10000000, 99999999)}",
                    fecha_nacimiento=date(1980, 1, 1),
                    fecha_registro=datetime.now(),
                    activo=True,
                    es_principal=False,
                    socio_principal_id=socio_principal.id,
                    codigo_socio=f"{socio_principal.codigo_socio}_{j+1:02d}",  # Formato: AET001_01, AET001_02, etc.
                    num_pers=1,
                    total_soc=1
                )
                miembros_familia.append(miembro)
            
            # Actualizar el número total de personas y socios en el socio principal
            socio_principal.num_pers = 1 + len(miembros_familia)  # El principal + los miembros
            socio_principal.total_soc = socio_principal.num_pers  # En este caso es lo mismo
            
            # Añadir todos los miembros de la familia
            session.add_all(miembros_familia)
            
            print(f"Creado socio principal {socio_principal.codigo_socio} con {len(miembros_familia)} miembros")
        
        # Commit todos los cambios
        session.commit()
        
        # Verificar que se crearon los 20 socios principales
        socios_principales = session.query(Socio).filter(
            Socio.es_principal == True,
            Socio.email.like('%@example.com'),
            Socio.codigo_socio.like('AET%')
        ).all()
        
        print(f"\nSocios principales creados: {len(socios_principales)}")
        for socio in socios_principales:
            print(f"Código: {socio.codigo_socio}, Email: {socio.email}")
        
        assert len(socios_principales) == 20, f"Se esperaban 20 socios principales, pero se encontraron {len(socios_principales)}"
        
        print("\nResumen de socios creados:")
        for socio in socios_principales:
            miembros = session.query(Socio).filter_by(socio_principal_id=socio.id).all()
            print(f"Socio {socio.codigo_socio}: {socio.nombre} - {len(miembros)} miembros")
            assert socio.num_pers == 1 + len(miembros)
            assert socio.total_soc == socio.num_pers
        
        print("\nTest completado. Puedes verificar los datos en la aplicación.")
        print("Para limpiar los datos de prueba, ejecuta el test con --cleanup")
            
    except Exception as e:
        print(f"Error durante el test: {e}")
        session.rollback()
        raise
    finally:
        if cleanup_requested:
            print("\nLimpiando datos de prueba...")
            cleanup_test_data(session)
        session.close()

def pytest_addoption(parser):
    parser.addoption("--cleanup", action="store_true", default=False,
                    help="Limpiar datos de prueba antes de ejecutar los tests") 
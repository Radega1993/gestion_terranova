# En logic/socios.py
from app.database.connection import Session
from app.database.models import Socio, MiembroFamilia
from sqlalchemy import and_

def crear_socio(
    nombre, primer_apellido, segundo_apellido, dni=None, codigo_socio=None,
    email=None, email2=None, direccion=None, poblacion=None, codigo_postal=None,
    provincia=None, telefono=None, telefono2=None, fecha_nacimiento=None,
    iban=None, entidad=None, oficina=None, dc=None, cuenta_corriente=None,
    es_principal=False, socio_principal_id=None, num_pers=None, adherits=None,
    menor_3_anys=None, cuota=None, foto_path=None, rgpd=False
):
    with Session() as session:
        # Verificar que el socio principal existe si se proporciona
        if not es_principal and socio_principal_id:
            socio_principal = session.query(Socio).filter_by(
                id=socio_principal_id,
                activo=True,
                es_principal=True
            ).one_or_none()
            
            if not socio_principal:
                raise ValueError("El socio principal seleccionado no existe, no está activo o no es principal")

        # Crear el socio
        socio = Socio(
            # Datos básicos
            rgpd=rgpd,
            codigo_socio=codigo_socio,
            dni=dni,
            nombre=nombre,
            primer_apellido=primer_apellido,
            segundo_apellido=segundo_apellido,
            fecha_nacimiento=fecha_nacimiento,
            cuota=cuota,
            
            # Información de contacto
            direccion=direccion,
            poblacion=poblacion,
            codigo_postal=codigo_postal,
            provincia=provincia,
            telefono=telefono,
            telefono2=telefono2,
            email=email,
            email2=email2,
            
            # Información bancaria
            iban=iban,
            entidad=entidad,
            oficina=oficina,
            dc=dc,
            cuenta_corriente=cuenta_corriente,
            
            # Información familiar
            es_principal=es_principal,
            socio_principal_id=None if es_principal else socio_principal_id,
            num_pers=num_pers,
            adherits=adherits,
            menor_3_anys=menor_3_anys,
            
            # Foto
            foto_path=foto_path
        )
        session.add(socio)
        session.commit()
        return socio.id

def obtener_socios():
    with Session() as session:
        return session.query(Socio).all()

def obtener_socios_principales():
    with Session() as session:
        socios = session.query(Socio).filter(
            Socio.es_principal == True  # Eliminamos el filtro de activo
        ).all()
        
        # Imprimir para depuración
        print(f"SOCIOS PRINCIPALES ENCONTRADOS: {len(socios)}")
        for socio in socios:
            print(f"  - {socio.nombre} (ID: {socio.id}, es_principal: {socio.es_principal}, activo: {socio.activo})")
            
        return socios

def obtener_miembros_familia(socio_principal_id):
    with Session() as session:
        # Obtener los miembros directamente de la tabla Socio
        miembros = session.query(Socio).filter(
            and_(
                Socio.socio_principal_id == socio_principal_id,
                Socio.es_principal == False  # Eliminamos el filtro de activo
            )
        ).all()
        
        # Imprimir para depuración
        print(f"Miembros encontrados para socio principal {socio_principal_id}: {len(miembros)}")
        for miembro in miembros:
            print(f"  - {miembro.nombre} (ID: {miembro.id}, activo: {miembro.activo})")
            
        return miembros

def obtener_socio_por_id(socio_id):
    with Session() as session:
        socio = session.query(Socio).filter_by(id=socio_id).one_or_none()
        return socio

def desactivar_socio(socio_id):
    with Session() as session:
        socio = session.query(Socio).filter_by(id=socio_id).one()
        # Si es un socio principal, desactivar también a los miembros de su familia
        if socio.es_principal:
            miembros = session.query(Socio).filter_by(socio_principal_id=socio_id).all()
            for miembro in miembros:
                miembro.activo = False
        socio.activo = False
        session.commit()

def activar_socio(socio_id):
    with Session() as session:
        socio = session.query(Socio).filter_by(id=socio_id).one()
        # Si es un miembro de familia, verificar que su socio principal esté activo
        if not socio.es_principal and socio.socio_principal_id:
            socio_principal = session.query(Socio).filter_by(id=socio.socio_principal_id).one()
            if not socio_principal.activo:
                raise ValueError("No se puede activar un miembro de familia si su socio principal está inactivo")
        socio.activo = True
        session.commit()

def actualizar_socio(
    socio_id,
    nombre, primer_apellido, segundo_apellido, dni=None, codigo_socio=None,
    email=None, email2=None, direccion=None, poblacion=None, codigo_postal=None,
    provincia=None, telefono=None, telefono2=None, fecha_nacimiento=None,
    iban=None, entidad=None, oficina=None, dc=None, cuenta_corriente=None,
    es_principal=False, socio_principal_id=None, num_pers=None, adherits=None,
    menor_3_anys=None, cuota=None, foto_path=None, rgpd=False
):
    with Session() as session:
        socio = session.query(Socio).filter_by(id=socio_id).one()
        
        # Si cambia de tipo (principal a miembro o viceversa)
        if socio.es_principal != es_principal:
            if es_principal:
                # Si pasa a ser principal, eliminar su relación con el socio principal
                socio.socio_principal_id = None
            else:
                # Si pasa a ser miembro, verificar que no tenga miembros asociados
                miembros = session.query(Socio).filter_by(socio_principal_id=socio_id).all()
                if miembros:
                    raise ValueError("No se puede convertir en miembro un socio que tiene miembros asociados")
        
        # Verificar que el socio principal existe si se proporciona
        if not es_principal and socio_principal_id:
            socio_principal = session.query(Socio).filter_by(
                id=socio_principal_id,
                activo=True,
                es_principal=True
            ).one_or_none()
            
            if not socio_principal:
                raise ValueError("El socio principal seleccionado no existe, no está activo o no es principal")
        
        # Actualizar datos básicos
        socio.rgpd = rgpd
        socio.codigo_socio = codigo_socio
        socio.dni = dni
        socio.nombre = nombre
        socio.primer_apellido = primer_apellido
        socio.segundo_apellido = segundo_apellido
        socio.fecha_nacimiento = fecha_nacimiento
        socio.cuota = cuota
        
        # Actualizar información de contacto
        socio.direccion = direccion
        socio.poblacion = poblacion
        socio.codigo_postal = codigo_postal
        socio.provincia = provincia
        socio.telefono = telefono
        socio.telefono2 = telefono2
        socio.email = email
        socio.email2 = email2
        
        # Actualizar información bancaria
        socio.iban = iban
        socio.entidad = entidad
        socio.oficina = oficina
        socio.dc = dc
        socio.cuenta_corriente = cuenta_corriente
        
        # Actualizar información familiar
        socio.es_principal = es_principal
        socio.socio_principal_id = None if es_principal else socio_principal_id
        socio.num_pers = num_pers
        socio.adherits = adherits
        socio.menor_3_anys = menor_3_anys
        
        # Actualizar foto solo si se proporciona una nueva
        if foto_path:
            socio.foto_path = foto_path
            
        session.commit()
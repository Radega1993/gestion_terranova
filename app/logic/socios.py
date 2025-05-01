# En logic/socios.py
from app.database.connection import Session
from app.database.models import Socio, MiembroFamilia
from sqlalchemy import and_, or_

def generar_codigo_socio(session, es_principal=True, socio_principal_id=None):
    """
    Genera un código de socio único en el formato AET001 para socios principales
    o AET001_01 para miembros de familia.
    
    Args:
        session: Sesión de base de datos
        es_principal: Boolean indicando si es socio principal
        socio_principal_id: ID del socio principal si es miembro de familia
    
    Returns:
        String con el código de socio generado
    """
    if es_principal:
        # Obtener el último código de socio principal
        ultimo_socio = session.query(Socio).filter(
            Socio.es_principal == True,
            Socio.codigo_socio.like('AET%')
        ).order_by(Socio.codigo_socio.desc()).first()
        
        if not ultimo_socio or not ultimo_socio.codigo_socio:
            # Si no hay socios, empezar con AET001
            nuevo_numero = 1
        else:
            # Extraer el número del último código y sumar 1
            ultimo_numero = int(ultimo_socio.codigo_socio[3:])
            nuevo_numero = ultimo_numero + 1
        
        return f"AET{nuevo_numero:03d}"
    else:
        # Para miembros de familia, obtener el código del socio principal
        socio_principal = session.query(Socio).filter_by(id=socio_principal_id).first()
        if not socio_principal:
            raise ValueError("No se encontró el socio principal")
        
        # Obtener el último número de miembro para este socio principal
        ultimo_miembro = session.query(Socio).filter(
            Socio.socio_principal_id == socio_principal_id,
            Socio.codigo_socio.like(f"{socio_principal.codigo_socio}_%")
        ).order_by(Socio.codigo_socio.desc()).first()
        
        if not ultimo_miembro or not ultimo_miembro.codigo_socio:
            # Si no hay miembros, empezar con _01
            nuevo_numero = 1
        else:
            # Extraer el número del último código y sumar 1
            ultimo_numero = int(ultimo_miembro.codigo_socio.split('_')[1])
            nuevo_numero = ultimo_numero + 1
        
        return f"{socio_principal.codigo_socio}_{nuevo_numero:02d}"

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

        # Generar código de socio si no se proporciona
        if not codigo_socio:
            codigo_socio = generar_codigo_socio(session, es_principal, socio_principal_id)

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
        socio = session.query(Socio).filter_by(id=socio_id).one_or_none()
        if not socio:
            raise ValueError("El socio no existe")
            
        if not socio.activo:
            raise ValueError("El socio ya está desactivado")
            
        # Si es un socio principal, desactivar también a los miembros de su familia
        if socio.es_principal:
            miembros = session.query(Socio).filter_by(socio_principal_id=socio_id).all()
            for miembro in miembros:
                miembro.activo = False
                print(f"Desactivando miembro de familia: {miembro.nombre}")
        else:
            # Si es un miembro, verificar que no tenga deudas pendientes
            from app.logic.deudas import verificar_deudas_socio
            if verificar_deudas_socio(socio_id):
                raise ValueError("No se puede desactivar un socio con deudas pendientes")
                
        socio.activo = False
        session.commit()
        return True

def activar_socio(socio_id):
    with Session() as session:
        socio = session.query(Socio).filter_by(id=socio_id).one_or_none()
        if not socio:
            raise ValueError("El socio no existe")
            
        if socio.activo:
            raise ValueError("El socio ya está activo")
            
        # Si es un miembro de familia, verificar que su socio principal esté activo
        if not socio.es_principal and socio.socio_principal_id:
            socio_principal = session.query(Socio).filter_by(id=socio.socio_principal_id).one_or_none()
            if not socio_principal:
                raise ValueError("El socio principal no existe")
            if not socio_principal.activo:
                raise ValueError("No se puede activar un miembro de familia si su socio principal está inactivo")
                
        socio.activo = True
        session.commit()
        return True

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

def buscar_socios(session, termino):
    """
    Busca socios por nombre o email.
    
    Args:
        session: Sesión de SQLAlchemy
        termino: Término de búsqueda (nombre o email)
        
    Returns:
        Lista de socios que coinciden con el término de búsqueda
    """
    # Convertir el término a minúsculas para hacer la búsqueda insensible a mayúsculas/minúsculas
    termino = termino.lower()
    
    # Buscar socios que coincidan con el término en nombre o email
    socios = session.query(Socio).filter(
        and_(
            Socio.activo == True,
            or_(
                Socio.nombre.ilike(f"%{termino}%"),
                Socio.email.ilike(f"%{termino}%"),
                Socio.primer_apellido.ilike(f"%{termino}%"),
                Socio.segundo_apellido.ilike(f"%{termino}%")
            )
        )
    ).all()
    
    return socios
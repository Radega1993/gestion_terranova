import pandas as pd
from sqlalchemy.orm import Session
from app.database.models import Socio
from datetime import datetime
import re

def import_socios_from_excel(session: Session, file_path: str) -> tuple[int, int]:
    """
    Importa socios desde un archivo Excel.
    Retorna una tupla con (socios_importados, errores)
    """
    try:
        # Leer el archivo Excel
        df = pd.read_excel(file_path)
        
        # Validar que el archivo tenga las columnas mínimas requeridas
        required_columns = ['NOMBRE', 'PRIMER_APELLIDO', 'CODIGO_SOCIO']
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            raise ValueError(f"El archivo Excel no contiene las columnas requeridas: {', '.join(missing_columns)}")
            
        socios_importados = 0
        errores = 0
        socios_saltados = 0
        
        # Primero importar todos los socios principales
        socios_principales = {}
        for index, row in df.iterrows():
            try:
                if row.get('ES_PRINCIPAL', True):  # Por defecto es principal si no se especifica
                    # Validar datos requeridos para socios principales
                    if pd.isna(row['NOMBRE']) or pd.isna(row['PRIMER_APELLIDO']) or pd.isna(row['CODIGO_SOCIO']):
                        print(f"Error en fila {index + 2}: Faltan datos requeridos para socio principal")
                        errores += 1
                        continue
                        
                    # Crear un diccionario con los datos del socio
                    socio_data = {
                        'nombre': str(row['NOMBRE']).strip(),
                        'primer_apellido': str(row['PRIMER_APELLIDO']).strip(),
                        'segundo_apellido': str(row['SEGUNDO_APELLIDO']).strip() if 'SEGUNDO_APELLIDO' in row and pd.notna(row['SEGUNDO_APELLIDO']) else None,
                        'dni': str(row['DNI']).strip() if 'DNI' in row and pd.notna(row['DNI']) else None,
                        'telefono': str(row['TELEFONO']).strip() if 'TELEFONO' in row and pd.notna(row['TELEFONO']) else None,
                        'email': str(row['EMAIL']).strip() if 'EMAIL' in row and pd.notna(row['EMAIL']) else None,
                        'direccion': str(row['DIRECCION']).strip() if 'DIRECCION' in row and pd.notna(row['DIRECCION']) else None,
                        'poblacion': str(row['POBLACION']).strip() if 'POBLACION' in row and pd.notna(row['POBLACION']) else None,
                        'codigo_postal': str(row['CODIGO_POSTAL']).strip() if 'CODIGO_POSTAL' in row and pd.notna(row['CODIGO_POSTAL']) else None,
                        'provincia': str(row['PROVINCIA']).strip() if 'PROVINCIA' in row and pd.notna(row['PROVINCIA']) else None,
                        'fecha_nacimiento': row['FECHA_NACIMIENTO'] if 'FECHA_NACIMIENTO' in row and pd.notna(row['FECHA_NACIMIENTO']) else None,
                        'es_principal': True,
                        'activo': True if 'ACTIVO' not in row else bool(row['ACTIVO']),
                        'rgpd': False if 'RGPD' not in row else bool(row['RGPD']),
                        'codigo_socio': str(row['CODIGO_SOCIO']).strip(),
                        'casa': int(row['CASA']) if 'CASA' in row and pd.notna(row['CASA']) else None,
                        'total_soc': int(row['TOTAL_SOC']) if 'TOTAL_SOC' in row and pd.notna(row['TOTAL_SOC']) else None,
                        'num_pers': int(row['NUM_PERS']) if 'NUM_PERS' in row and pd.notna(row['NUM_PERS']) else None,
                        'adherits': int(row['ADHERITS']) if 'ADHERITS' in row and pd.notna(row['ADHERITS']) else None,
                        'menor_3_anys': int(row['MENOR_3_ANYS']) if 'MENOR_3_ANYS' in row and pd.notna(row['MENOR_3_ANYS']) else None,
                        'cuota': float(row['CUOTA']) if 'CUOTA' in row and pd.notna(row['CUOTA']) else None,
                        'iban': str(row['IBAN']).strip() if 'IBAN' in row and pd.notna(row['IBAN']) else None,
                        'entidad': str(row['ENTIDAD']).strip() if 'ENTIDAD' in row and pd.notna(row['ENTIDAD']) else None,
                        'oficina': str(row['OFICINA']).strip() if 'OFICINA' in row and pd.notna(row['OFICINA']) else None,
                        'dc': str(row['DC']).strip() if 'DC' in row and pd.notna(row['DC']) else None,
                        'cuenta_corriente': str(row['CUENTA_CORRIENTE']).strip() if 'CUENTA_CORRIENTE' in row and pd.notna(row['CUENTA_CORRIENTE']) else None,
                        'telefono2': str(row['TELEFONO2']).strip() if 'TELEFONO2' in row and pd.notna(row['TELEFONO2']) else None,
                        'email2': str(row['EMAIL2']).strip() if 'EMAIL2' in row and pd.notna(row['EMAIL2']) else None,
                        'observaciones': str(row['OBSERVACIONES']).strip() if 'OBSERVACIONES' in row and pd.notna(row['OBSERVACIONES']) else None,
                        'foto_path': str(row['FOTO_PATH']).strip() if 'FOTO_PATH' in row and pd.notna(row['FOTO_PATH']) else None,
                        'canvi': str(row['CANVI']).strip() if 'CANVI' in row and pd.notna(row['CANVI']) else None
                    }

                    # Eliminar los campos que son None
                    socio_data = {k: v for k, v in socio_data.items() if v is not None}

                    # Verificar si ya existe un socio con el mismo código
                    existing_socio = session.query(Socio).filter_by(codigo_socio=socio_data['codigo_socio']).first()
                    if existing_socio:
                        print(f"Info: Socio con código {socio_data['codigo_socio']} ya existe, se salta")
                        socios_saltados += 1
                        continue

                    # Crear el socio
                    socio = Socio(**socio_data)
                    session.add(socio)
                    socios_importados += 1
                    
            except Exception as e:
                print(f"Error procesando fila {index + 2}: {str(e)}")
                errores += 1
                continue
                
        # Guardar los cambios para obtener los IDs de los socios principales
        session.commit()
        
        # Obtener los socios principales recién creados
        for socio in session.query(Socio).filter_by(es_principal=True).all():
            socios_principales[socio.codigo_socio] = socio.id
            
        # Ahora importar los miembros de familia
        for index, row in df.iterrows():
            try:
                if not row.get('ES_PRINCIPAL', True):  # Si no es principal
                    # Validar datos requeridos para miembros de familia
                    if pd.isna(row['NOMBRE']) or pd.isna(row['PRIMER_APELLIDO']) or pd.isna(row['SOCIO_PRINCIPAL_CODIGO']):
                        print(f"Error en fila {index + 2}: Faltan datos requeridos para miembro de familia")
                        errores += 1
                        continue
                        
                    # Crear un diccionario con los datos del socio
                    socio_data = {
                        'nombre': str(row['NOMBRE']).strip(),
                        'primer_apellido': str(row['PRIMER_APELLIDO']).strip(),
                        'segundo_apellido': str(row['SEGUNDO_APELLIDO']).strip() if 'SEGUNDO_APELLIDO' in row and pd.notna(row['SEGUNDO_APELLIDO']) else None,
                        'dni': str(row['DNI']).strip() if 'DNI' in row and pd.notna(row['DNI']) else None,
                        'telefono': str(row['TELEFONO']).strip() if 'TELEFONO' in row and pd.notna(row['TELEFONO']) else None,
                        'email': str(row['EMAIL']).strip() if 'EMAIL' in row and pd.notna(row['EMAIL']) else None,
                        'direccion': str(row['DIRECCION']).strip() if 'DIRECCION' in row and pd.notna(row['DIRECCION']) else None,
                        'poblacion': str(row['POBLACION']).strip() if 'POBLACION' in row and pd.notna(row['POBLACION']) else None,
                        'codigo_postal': str(row['CODIGO_POSTAL']).strip() if 'CODIGO_POSTAL' in row and pd.notna(row['CODIGO_POSTAL']) else None,
                        'provincia': str(row['PROVINCIA']).strip() if 'PROVINCIA' in row and pd.notna(row['PROVINCIA']) else None,
                        'fecha_nacimiento': row['FECHA_NACIMIENTO'] if 'FECHA_NACIMIENTO' in row and pd.notna(row['FECHA_NACIMIENTO']) else None,
                        'es_principal': False,
                        'activo': True if 'ACTIVO' not in row else bool(row['ACTIVO']),
                        'rgpd': False if 'RGPD' not in row else bool(row['RGPD']),
                        'codigo_socio': str(row['CODIGO_SOCIO']).strip() if 'CODIGO_SOCIO' in row and pd.notna(row['CODIGO_SOCIO']) else None,
                        'casa': int(row['CASA']) if 'CASA' in row and pd.notna(row['CASA']) else None,
                        'total_soc': int(row['TOTAL_SOC']) if 'TOTAL_SOC' in row and pd.notna(row['TOTAL_SOC']) else None,
                        'num_pers': int(row['NUM_PERS']) if 'NUM_PERS' in row and pd.notna(row['NUM_PERS']) else None,
                        'adherits': int(row['ADHERITS']) if 'ADHERITS' in row and pd.notna(row['ADHERITS']) else None,
                        'menor_3_anys': int(row['MENOR_3_ANYS']) if 'MENOR_3_ANYS' in row and pd.notna(row['MENOR_3_ANYS']) else None,
                        'cuota': float(row['CUOTA']) if 'CUOTA' in row and pd.notna(row['CUOTA']) else None,
                        'iban': str(row['IBAN']).strip() if 'IBAN' in row and pd.notna(row['IBAN']) else None,
                        'entidad': str(row['ENTIDAD']).strip() if 'ENTIDAD' in row and pd.notna(row['ENTIDAD']) else None,
                        'oficina': str(row['OFICINA']).strip() if 'OFICINA' in row and pd.notna(row['OFICINA']) else None,
                        'dc': str(row['DC']).strip() if 'DC' in row and pd.notna(row['DC']) else None,
                        'cuenta_corriente': str(row['CUENTA_CORRIENTE']).strip() if 'CUENTA_CORRIENTE' in row and pd.notna(row['CUENTA_CORRIENTE']) else None,
                        'telefono2': str(row['TELEFONO2']).strip() if 'TELEFONO2' in row and pd.notna(row['TELEFONO2']) else None,
                        'email2': str(row['EMAIL2']).strip() if 'EMAIL2' in row and pd.notna(row['EMAIL2']) else None,
                        'observaciones': str(row['OBSERVACIONES']).strip() if 'OBSERVACIONES' in row and pd.notna(row['OBSERVACIONES']) else None,
                        'foto_path': str(row['FOTO_PATH']).strip() if 'FOTO_PATH' in row and pd.notna(row['FOTO_PATH']) else None,
                        'canvi': str(row['CANVI']).strip() if 'CANVI' in row and pd.notna(row['CANVI']) else None
                    }

                    # Eliminar los campos que son None
                    socio_data = {k: v for k, v in socio_data.items() if v is not None}

                    # Buscar el socio principal por código
                    codigo_principal = str(row['SOCIO_PRINCIPAL_CODIGO']).strip()
                    if codigo_principal in socios_principales:
                        socio_data['socio_principal_id'] = socios_principales[codigo_principal]
                    else:
                        print(f"Error en fila {index + 2}: No se encontró el socio principal con código {codigo_principal}")
                        errores += 1
                        continue

                    # Verificar si ya existe un socio con el mismo código
                    if 'codigo_socio' in socio_data:
                        existing_socio = session.query(Socio).filter_by(codigo_socio=socio_data['codigo_socio']).first()
                        if existing_socio:
                            print(f"Info: Socio con código {socio_data['codigo_socio']} ya existe, se salta")
                            socios_saltados += 1
                            continue

                    # Crear el socio
                    socio = Socio(**socio_data)
                    session.add(socio)
                    socios_importados += 1
                    
            except Exception as e:
                print(f"Error procesando fila {index + 2}: {str(e)}")
                errores += 1
                continue
                
        # Guardar los cambios
        session.commit()
        print(f"Importación completada: {socios_importados} socios importados, {socios_saltados} socios saltados, {errores} errores")
        return socios_importados, errores
        
    except Exception as e:
        session.rollback()
        raise Exception(f"Error al importar el archivo: {str(e)}") 
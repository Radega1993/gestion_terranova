from sqlalchemy.orm import Session
from app.models.socio import Socio

def generar_codigo_socio(session: Session, es_principal: bool, socio_principal_id: int = None) -> str:
    """
    Genera un código único para un socio.
    
    Args:
        session: Sesión de la base de datos
        es_principal: True si es socio principal, False si es familiar
        socio_principal_id: ID del socio principal (solo para socios familiares)
    
    Returns:
        str: Código generado en formato AET001 para principales o AET001_01 para familiares
    """
    if es_principal:
        # Buscar el último código de socio principal
        ultimo_socio = session.query(Socio).filter(
            Socio.es_principal == True,
            Socio.codigo_socio.like('AET%')
        ).order_by(Socio.codigo_socio.desc()).first()
        
        if ultimo_socio and ultimo_socio.codigo_socio:
            # Extraer el número y sumar 1
            numero = int(ultimo_socio.codigo_socio[3:]) + 1
        else:
            # Si no hay socios, empezar con 1
            numero = 1
            
        # Formatear el código con 3 dígitos
        return f"AET{numero:03d}"
    else:
        if not socio_principal_id:
            raise ValueError("Se requiere el ID del socio principal para generar código de familiar")
            
        # Obtener el código del socio principal
        socio_principal = session.query(Socio).get(socio_principal_id)
        if not socio_principal:
            raise ValueError("Socio principal no encontrado")
            
        # Buscar el último código de familiar para este socio principal
        ultimo_familiar = session.query(Socio).filter(
            Socio.socio_principal_id == socio_principal_id,
            Socio.codigo_socio.like(f'{socio_principal.codigo_socio}_%')
        ).order_by(Socio.codigo_socio.desc()).first()
        
        if ultimo_familiar and ultimo_familiar.codigo_socio:
            # Extraer el número y sumar 1
            numero = int(ultimo_familiar.codigo_socio.split('_')[1]) + 1
        else:
            # Si no hay familiares, empezar con 01
            numero = 1
            
        # Formatear el código con 2 dígitos
        return f"{socio_principal.codigo_socio}_{numero:02d}" 
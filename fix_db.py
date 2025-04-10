from app.database.connection import Session
from app.database.models import Socio
from sqlalchemy import and_

def main():
    with Session() as session:
        # Obtener todos los socios
        socios = session.query(Socio).all()
        print(f"Total de socios: {len(socios)}")
        
        # Corregir los socios_principal_id
        for socio in socios:
            if socio.socio_principal_id and isinstance(socio.socio_principal_id, str) and " " in socio.socio_principal_id:
                # Extraer solo el ID numérico
                socio_id = int(socio.socio_principal_id.split()[0])
                print(f"Corrigiendo socio {socio.nombre} (ID: {socio.id}): socio_principal_id de '{socio.socio_principal_id}' a {socio_id}")
                socio.socio_principal_id = socio_id
        
        session.commit()
        print("Corrección completada.")
        
        # Verificar los resultados
        socios = session.query(Socio).all()
        print("\nVerificación después de la corrección:")
        for socio in socios:
            print(f"Socio: {socio.nombre} (ID: {socio.id}, es_principal: {socio.es_principal}, activo: {socio.activo}, socio_principal_id: {socio.socio_principal_id})")
        
        # Obtener socios principales
        socios_principales = session.query(Socio).filter(
            and_(Socio.es_principal == True, Socio.activo == True)
        ).all()
        print(f"\nSocios principales: {len(socios_principales)}")
        for socio in socios_principales:
            print(f"  - {socio.nombre} (ID: {socio.id})")
            
            # Obtener miembros de familia
            miembros = session.query(Socio).filter(
                and_(
                    Socio.socio_principal_id == socio.id,
                    Socio.activo == True,
                    Socio.es_principal == False
                )
            ).all()
            print(f"    Miembros: {len(miembros)}")
            for miembro in miembros:
                print(f"      - {miembro.nombre} (ID: {miembro.id})")

if __name__ == "__main__":
    main() 
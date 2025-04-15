from sqlalchemy import create_engine, text

DATABASE_URL = 'sqlite:///geston_terranova.db'

def migrate():
    engine = create_engine(DATABASE_URL)
    
    with engine.connect() as conn:
        # Verificar si la columna ya existe
        result = conn.execute(text("PRAGMA table_info(ventas)"))
        columns = [row[1] for row in result.fetchall()]
        
        if 'metodo_pago' not in columns:
            # Añadir la columna metodo_pago
            conn.execute(text("ALTER TABLE ventas ADD COLUMN metodo_pago VARCHAR(20)"))
            conn.commit()
            print("Columna metodo_pago añadida a la tabla ventas")
        else:
            print("La columna metodo_pago ya existe en la tabla ventas") 
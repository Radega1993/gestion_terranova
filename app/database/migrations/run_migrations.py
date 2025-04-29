from app.database.migrations.add_validado_field import migrate as add_validado_field

def run_migrations():
    """Ejecuta todas las migraciones en orden"""
    print("Iniciando migraciones...")
    
    # Ejecutar migraciones en orden
    add_validado_field()
    
    print("Migraciones completadas")

if __name__ == "__main__":
    run_migrations() 
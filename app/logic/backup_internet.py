import requests
import sqlite3
import psycopg2

def hay_conexion_internet(url='http://www.google.com/', timeout=5):
    try:
        req = requests.get(url, timeout=timeout)
        req.raise_for_status()
        print("Conexión a Internet detectada.")
        return True
    except requests.RequestException as e:
        print("No se detectó conexión a Internet.")
        return False


def exportar_sqlite_a_csv(nombre_db_sqlite, archivo_salida):
    conn = sqlite3.connect(nombre_db_sqlite)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM tu_tabla;")
    rows = cursor.fetchall()

    with open(archivo_salida, 'w') as f:
        for row in rows:
            f.write(",".join([str(item) for item in row]) + "\n")

    conn.close()
    print(f"Datos exportados a {archivo_salida}.")


def importar_csv_a_postgres(nombre_archivo_csv, nombre_tabla_postgres):
    conn = psycopg2.connect("dbname=tu_db user=tu_usuario password=tu_contraseña")
    cursor = conn.cursor()

    with open(nombre_archivo_csv, 'r') as f:
        # Asumiendo que la primera línea del CSV son los nombres de las columnas
        next(f)
        cursor.copy_from(f, nombre_tabla_postgres, sep=',')
    
    conn.commit()
    cursor.close()
    conn.close()
    print(f"Datos importados a la tabla {nombre_tabla_postgres} de PostgreSQL.")

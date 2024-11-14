# db.py
import psycopg2
from config import DB_CONFIG

def get_db_connection():
    """
    Retorna una nueva conexión a la base de datos PostgreSQL.
    """
    return psycopg2.connect(
        host=DB_CONFIG['host'],
        port=DB_CONFIG['port'],
        user=DB_CONFIG['user'],
        password=DB_CONFIG['password'],
        database=DB_CONFIG['database']
    )

def ejecutar_consulta(query, params=()):
    """
    Ejecuta una consulta en la base de datos y retorna los resultados.
    """
    conexion = get_db_connection()
    cursor = conexion.cursor()
    cursor.execute(query, params)
    resultados = cursor.fetchall()
    cursor.close()
    conexion.close()
    return resultados

def insertar_datos(query, params):
    """
    Inserta datos en la base de datos y confirma la transacción.
    """
    conexion = get_db_connection()
    cursor = conexion.cursor()
    cursor.execute(query, params)
    conexion.commit()
    cursor.close()
    conexion.close()

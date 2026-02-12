import sqlite3
import os

# Ruta absoluta {.db}, sobreposición
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_NAME = os.path.join(BASE_DIR, 'DataBase.db')

def init_db():
    print(f"Creando base de datos en: {DB_NAME}")
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    # ============= TABLA DE USUARIOS ==============#
    cursor.execute('''CREATE TABLE IF NOT EXISTS AUTORES
                   (
                   ID INTEGER PRIMARY KEY AUTOINCREMENT,
                   Nombre TEXT,
                   Apellido TEXT,
                   Correo TEXT,
                   Celular TEXT
                   )''')

    # ============= TABLA DATOS SENSORES ============#
    cursor.execute('''CREATE TABLE IF NOT EXISTS SENSORES
                   (
                   ID INTEGER PRIMARY KEY AUTOINCREMENT,
                   Fecha TEXT,
                   Hora TEXT,
                   Humedad REAL,
                   Distancia TEXT
                   )''')
    
    conn.commit()
    conn.close()
    print("Base de datos [UpDate] correctamente.")

if __name__ == '__main__':
    init_db()
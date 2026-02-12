import os
import sqlite3
import json
import threading
import time
from datetime import datetime
from flask import Flask, render_template, jsonify, request
from flask_cors import CORS
import paho.mqtt.client as mqtt




# ==========================================
# 1. CONFIGURACIÓN DE RUTAS Y FLASK (CRÍTICO)

# Ubicación actual de Servidor.py
base_dir = os.path.dirname(os.path.abspath(__file__))

# Rutas hacia atrás para encontrar la carpeta Vista_Frontend
ruta_templates = os.path.join(base_dir, '../../Vista_Frontend/templates')
ruta_static = os.path.join(base_dir, '../../Vista_Frontend/static')
# Ruta para conectar con la Base de Datos (en la carpeta hermana 'BaseDeDatos')
ruta_db = os.path.join(base_dir, '../BaseDeDatos/DataBase.db')

app = Flask(__name__, template_folder=ruta_templates, static_folder=ruta_static)
CORS(app)
# ==========================================





# ==========================================
# 2. CONFIGURACIÓN MQTT Y VARIABLES GLOBALES

MQTT_BROKER = "broker.hivemq.com"
MQTT_PORT = 1883
TOPIC_BASE = "A9/Isaac/Sensores"

# Cache para mostrar datos rápidos en la web sin consultar la DB a cada segundo
estado_sistema = {
    "Humedad": 0,
    "Distancia": 0,
    "mqtt": "Desconectado",
    "ultimo_mensaje": "Esperando datos..."
}
# ==========================================





# ==========================================
# 3. FUNCIONES DE BASE DE DATOS

def guardar_dato_en_db(payload):
    """
    Recibe el JSON del sensor y lo guarda en la tabla SENSORES
    """
    try:
        # Obtenemos fecha y hora actuales
        now = datetime.now()
        fecha_actual = now.strftime("%Y-%m-%d")
        hora_actual = now.strftime("%H:%M:%S")

        humedad = payload.get("Humedad", 0)
        distancia = payload.get("Distancia", "0")

        # Conexión a la DB (se abre y cierra en cada escritura para evitar bloqueos)
        with sqlite3.connect(ruta_db) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO SENSORES (Fecha, Hora, Humedad, Distancia)
                VALUES (?, ?, ?, ?)
            ''', (fecha_actual, hora_actual, humedad, distancia))
            conn.commit()
            
        print(f"^^ Dato guardado: Humedad={humedad}, Distancia={distancia}")

    except Exception as e:
        print(f"❌ Error guardando en DB: {e}")
# ==========================================





# ==========================================
# 4. LÓGICA MQTT (CALLBACKS)

def on_connect(client, userdata, flags, rc):
    estado_conn = "Conectado" if rc == 0 else "Error"
    print(f"MQTT Status: {estado_conn} (Código: {rc})")
    estado_sistema["mqtt"] = estado_conn
    client.subscribe(TOPIC_BASE + "/#")

def on_message(client, userdata, msg):
    print(f"--> Recibido en {msg.topic}: {msg.payload.decode()}")
    try:
        payload = json.loads(msg.payload.decode())
        
        # 1. Actualizar memoria (para la web en tiempo real)
        estado_sistema["Humedad"] = payload.get("Humedad", 0)
        estado_sistema["Distancia"] = payload.get("Distancia", 0)
        estado_sistema["ultimo_mensaje"] = datetime.now().strftime("%H:%M:%S")

        # 2. Guardar en Base de Datos (Historial)
        guardar_dato_en_db(payload)

    except json.JSONDecodeError:
        print("[!] Error: El mensaje no es un JSON válido")

# Iniciar hilo MQTT en segundo plano
def iniciar_mqtt():
    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message
    try:
        client.connect(MQTT_BROKER, MQTT_PORT, 60)
        client.loop_forever()
    except Exception as e:
        print(f"Error conexión MQTT: {e}")

threading.Thread(target=iniciar_mqtt, daemon=True).start()
# ==========================================





# ==========================================
# 5. RUTAS WEB (FLASK)

@app.route('/')
def dashboard():
    return render_template('dashboard.html')

# API que consultará el JavaScript cada 2 segundos
@app.route('/api/tiempo_real')
def api_datos():
    return jsonify(estado_sistema)

# API opcional para sacar el historial de la DB
@app.route('/api/historial')
def api_historial():
    try:
        conn = sqlite3.connect(ruta_db)
        cursor = conn.cursor()
        # Traer los últimos 10 registros
        cursor.execute("SELECT * FROM SENSORES ORDER BY ID DESC LIMIT 10")
        filas = cursor.fetchall()
        conn.close()
        
        # Convertir a lista de diccionarios
        datos = []
        for fila in filas:
            datos.append({
                "id": fila[0],
                "fecha": fila[1],
                "hora": fila[2],
                "humedad": fila[3],
                "distancia": fila[4]
            })
        return jsonify(datos)
    except Exception as e:
        return jsonify({"error": str(e)})

if __name__ == '__main__':
    print("`~~~~~~~~~+ Servidor Web Iniciado +~~~~~~~~~~")
    print(f"? = ? Buscando templates en: {ruta_templates}")
    app.run(debug=True, port=5000)
# ==========================================

# CONEXIÓN AL SERVIDOR
import time
import json
import random
import paho.mqtt.client as mqtt

# ==========================================
# CONFIGURACIÓN (Conexión con Servidor.py)

MQTT_BROKER = "broker.hivemq.com"
MQTT_PORT = 1883
TOPIC = "A9/Isaac/Sensores"  # El mismo tema que en tu servidor

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("✅ SIMULADOR: Conectado al Broker MQTT")
    else:
        print(f"❌ Error de conexión, código: {rc}")
# ==========================================




# Inicializamos el cliente
client = mqtt.Client()
client.on_connect = on_connect

print("📡 Conectando al Broker...")
client.connect(MQTT_BROKER, MQTT_PORT, 60)





#==========================================
# Iniciamos el bucle de envío de datos
try:
    while True:
        # 1. SIMULAR DATOS (Como si el sensor leyera)
        # Humedad aleatoria entre 40% y 90%
        humedad_simulada = round(random.uniform(40.0, 90.0), 1) 
        # Distancia aleatoria entre 10cm y 300cm
        distancia_simulada = random.randint(10, 300)

        # 2. CREAR EL JSON (Payload)
        payload = {
            "Humedad": humedad_simulada,
            "Distancia": distancia_simulada
        }

        # Convertir diccionario a texto JSON
        mensaje_json = json.dumps(payload)

        # 3. PUBLICAR (ENVIAR) AL TEMA
        client.publish(TOPIC, mensaje_json)
        
        print(f"📤 Enviado a {TOPIC}: {mensaje_json}")

        # Esperar 3 segundos antes del siguiente envío
        time.sleep(3)

except KeyboardInterrupt:
    print("\n [!] Simulador detenido por el usuario.")
    client.disconnect()
# ==========================================



# ^^ Simulador de sensores para pruebas sin hardware real. Envia datos aleatorios cada 3 segundos al mismo tema MQTT que el servidor escucha. ^^
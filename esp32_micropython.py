import network
import time
import json
from machine import Pin
from umqtt.simple import MQTTClient

# --- 1. CONFIGURACIÓN DE TU RED WIFI ---
SSID = "TU_NOMBRE_DE_RED_WIFI"
PASSWORD = "TU_CONTRASEÑA_WIFI"

# --- 2. CONFIGURACIÓN DEL BROKER MQTT ---
MQTT_BROKER = "broker.hivemq.com"
MQTT_CLIENT_ID = "ESP32_Cliente_Mano" # Puede ser cualquier nombre
MQTT_TOPIC = b"esp32/control_mano" # En MicroPython el topic suele ir como bytes (con la 'b' inicial)

# Configurar el LED integrado (el pin 2 en la mayoría de ESP32)
led = Pin(2, Pin.OUT)
led.value(0) # Iniciar apagado

def conectar_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    if not wlan.isconnected():
        print("Conectando a la red WiFi", end="")
        wlan.connect(SSID, PASSWORD)
        while not wlan.isconnected():
            time.sleep(0.5)
            print(".", end="")
    print("\n¡WiFi Conectado!")
    print("Dirección IP:", wlan.ifconfig()[0])

# Función que se ejecuta automáticamente cuando llega un mensaje
def al_recibir_mensaje(topic, msg):
    print("\n-------------------------------------")
    print("Mensaje recibido del topic:", topic.decode())
    print("Contenido:", msg.decode())
    
    try:
        # Extraer y decodificar el mensaje JSON
        payload = msg.decode("utf-8")
        datos = json.loads(payload)
        
        # Buscar la llave "estado" dentro del JSON
        estado = datos.get("estado")
        
        if estado == "Mano ABIERTA":
            print(">>> ACCIÓN: MANO ABIERTA. Encendiendo LED.")
            led.value(1) # Prender LED
            
        elif estado == "Mano CERRADA":
            print(">>> ACCIÓN: MANO CERRADA. Apagando LED.")
            led.value(0) # Apagar LED
            
    except ValueError:
        print("Error: El mensaje recibido no es un JSON válido.")

def conectar_mqtt():
    # keepalive mantiene viva la conexión en la nube
    client = MQTTClient(MQTT_CLIENT_ID, MQTT_BROKER, keepalive=60)
    client.set_callback(al_recibir_mensaje)
    
    print("Conectando al broker MQTT HiveMQ...")
    client.connect()
    print("¡Conectado a MQTT exitosamente!")
    
    # Nos suscribimos al canal
    client.subscribe(MQTT_TOPIC)
    print(f"Suscrito a: {MQTT_TOPIC.decode()}")
    
    return client

def main():
    conectar_wifi()
    
    try:
        client = conectar_mqtt()
    except Exception as e:
        print("Fallo al conectar con MQTT. ¿Tienes instalada la librería umqtt.simple?")
        print("Error:", e)
        return
        
    print("\n=============================================")
    print("Sistema listo y esperando recibir señales...")
    print("=============================================")
    
    while True:
        try:
            # Revisar constantemente si hay nuevos mensajes
            client.check_msg()
            time.sleep(0.1) # Pausa pequeña para no saturar el procesador
        except OSError:
            print("Se perdió la conexión, reiniciando la ESP32 en 5 seg...")
            time.sleep(5)
            import machine
            machine.reset()

if __name__ == "__main__":
    main()

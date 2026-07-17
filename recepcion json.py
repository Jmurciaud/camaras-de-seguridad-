import network
import urequests
import ujson
import time

# ===========================
# CONFIGURACIÓN WIFI
# ===========================
SSID = "TU_WIFI"
PASSWORD = "TU_CONTRASEÑA"

# IP de la ESP32 receptora
URL = "http://192.168.1.100"

# ===========================
# CONECTAR WIFI
# ===========================
wifi = network.WLAN(network.STA_IF)
wifi.active(True)
wifi.connect(SSID, PASSWORD)

while not wifi.isconnected():
    pass

print("WiFi conectado")
print(wifi.ifconfig())

while True:

    # Cambia este valor por la condición de tu proyecto
    valor = 1      # o 0

    datos = {
        "alarma": valor
    }

    try:
        r = urequests.post(
            URL,
            data=ujson.dumps(datos),
            headers={"Content-Type": "application/json"}
        )

        print("JSON enviado:", datos)
        print("Respuesta:", r.text)
        r.close()

    except Exception as e:
        print("Error:", e)

    time.sleep(5)
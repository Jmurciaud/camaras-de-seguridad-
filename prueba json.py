import requests
import time

# Cambia esta IP por la de tu ESP32 receptora
URL = "http://10.176.216.170"

valor = 0

while True:
    datos = {
        "alarma": valor
    }

    try:
        respuesta = requests.post(
            URL,
            json=datos,
            timeout=5
        )

        print(f"Enviado: {datos} | Respuesta: {respuesta.text}")

    except Exception as e:
        print("Error:", e)

    # Alterna entre 0 y 1
    valor = 1 if valor == 0 else 0

    time.sleep(5)
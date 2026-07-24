import cv2
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
import os
import json
import paho.mqtt.client as mqtt
def main():
    print("Iniciando y cargando modelo de IA...")
    
    # Configurar MQTT para el ESP32
    print("Conectando al broker MQTT...")
    mqtt_client = mqtt.Client()
    try:
        # Usamos un broker público gratuito como hivemq
        mqtt_client.connect("broker.hivemq.com", 1883, 60)
        mqtt_client.loop_start()
        print("Conectado exitosamente a MQTT.")
    except Exception as e:
        print(f"Advertencia: No se pudo conectar a MQTT: {e}")
    # Configurar el detector usando la nueva API 'tasks' de MediaPipe
    # Esta API es compatible con las versiones más nuevas de Python (como 3.13)
    model_path = os.path.abspath('hand_landmarker.task')
    base_options = python.BaseOptions(model_asset_path=model_path)
    options = vision.HandLandmarkerOptions(
        base_options=base_options,
        num_hands=1,
        min_hand_detection_confidence=0.7,
        min_hand_presence_confidence=0.7,
        min_tracking_confidence=0.7
    )
    
    # Crear el detector
    detector = vision.HandLandmarker.create_from_options(options)

    # Iniciar cámara
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Error al abrir la cámara web.")
        return

    print("Cámara iniciada. Presiona 'q' sobre la ventana de video para salir.")
    estado_anterior = None

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        # Espejar
        frame = cv2.flip(frame, 1)
        h, w, _ = frame.shape
        
        # Convertir a formato propio de MediaPipe Image
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
        
        # Procesar con el modelo
        detection_result = detector.detect(mp_image)

        estado_actual = "No se detecta mano"

        if detection_result.hand_landmarks:
            for hand_landmarks in detection_result.hand_landmarks:
                
                # Dibujar los puntos manualmente (ya que mp.solutions falla en tu versión de Python)
                for lm in hand_landmarks:
                    cx, cy = int(lm.x * w), int(lm.y * h)
                    cv2.circle(frame, (cx, cy), 3, (0, 255, 0), -1)
                
                # Lógica de detección: Puntas vs bases
                tip_ids = [8, 12, 16, 20]
                mcp_ids = [5, 9, 13, 17]
                
                dedos_abiertos = 0
                for i in range(4):
                    # Comparamos si la punta está más alta (menor Y) que la articulación base
                    if hand_landmarks[tip_ids[i]].y < hand_landmarks[mcp_ids[i]].y:
                        dedos_abiertos += 1

                # Si al menos 3 de los 4 dedos principales están extendidos
                if dedos_abiertos >= 3:
                    estado_actual = "Mano ABIERTA"
                else:
                    estado_actual = "Mano CERRADA"

        if estado_actual != estado_anterior:
            print(f"> {estado_actual}")
            
            # Enviar por MQTT en formato JSON para la ESP32
            # Solo enviamos cuando detecta la mano en algún estado válido
            if estado_actual in ["Mano ABIERTA", "Mano CERRADA"]:
                payload = json.dumps({"estado": estado_actual})
                mqtt_client.publish("esp32/control_mano", payload)
                print(f"  [MQTT Enviado]: {payload}")

            estado_anterior = estado_actual
        cv2.imshow("Reconocimiento de Mano", frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()
    detector.close()
    
    # Cerrar conexión MQTT
    mqtt_client.loop_stop()
    mqtt_client.disconnect()

if __name__ == "__main__":
    main()

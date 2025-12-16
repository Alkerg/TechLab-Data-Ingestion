import json
import base64
import os
import paho.mqtt.client as mqtt
import requests
from utils import json_to_ngsi_entity
from dotenv import load_dotenv

load_dotenv()

ORION_URL = os.getenv("ORION_URL", "http://localhost:1026/v2/entities")
MQTT_BROKER_HOST = os.getenv("MQTT_BROKER_HOST", "localhost")
MQTT_TLS_BOOL = os.getenv("MQTT_TLS_BOOL", False)
MQTT_BROKER_PORT = int(os.getenv("MQTT_BROKER_PORT", "1883"))

with open("./schemas/models.json") as f:
    MODELS = json.load(f)

TOPIC_MODEL_MAP = {
    "smart_parking/data": "smart_parking",
    "cuenta_personas/data": "cuenta_personas",
    "lorawan/data": "lora_wan" # Por ahora solo este proyecto envia datos mediante MQTT
}

def on_message(client, userdata, msg):
    try:
        raw = json.loads(msg.payload.decode())
        topic = msg.topic

        print(f"Mensaje recibido en: {topic}")

        if topic not in TOPIC_MODEL_MAP:
            print("Modelo desconocido")
            return

        entity_type = TOPIC_MODEL_MAP[topic]
        id_field = MODELS[entity_type]["id_field"]

        raw_payload = base64.b64decode(raw["data"]).decode()

        try:
            payload = json.loads(raw_payload)
        except json.JSONDecodeError:
            payload = {"data": raw_payload}

        try:
            entity = json_to_ngsi_entity(payload, entity_type, id_field)
        except Exception as e:
            print("Error creando entidad NGSI:", e)
            return
        
        r = requests.post(ORION_URL, json=entity)

        if r.status_code == 201:
            print("Entidad creada:", entity["id"])
           

        elif r.status_code == 422:
            attributes = entity.copy()
            attributes.pop("id", None)
            attributes.pop("type", None)
            r2 = requests.patch(
                f"{ORION_URL}/{entity['id']}/attrs",
                json=attributes
            )
            print("Entidad actualizada:", entity["id"])

        else:
            print("Error Orion:", r.text)

    except Exception as e:
        print("Error procesando mensaje:", e)


if __name__ == "__main__":
    client = mqtt.Client()
    client.on_message = on_message

    client.tls_set()
    client.tls_insecure_set(True)        

    client.connect(MQTT_BROKER_HOST, MQTT_BROKER_PORT, 60)

    for topic in TOPIC_MODEL_MAP:
        client.subscribe(topic)

    print("Servidor MQTT escuchando...")
    client.loop_forever()

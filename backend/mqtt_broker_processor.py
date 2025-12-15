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
MQTT_BROKER_PORT = int(os.getenv("MQTT_BROKER_PORT", "1883"))

try:
    with open("./schemas/models.json") as f:
        MODELS = json.load(f)
except FileNotFoundError:
    print("Error: No se encontró backend/schemas/models.json")
    MODELS = {}

TOPIC_MODEL_MAP = {}
for model_name, config in MODELS.items():
    if "mqtt_topic" in config:
        TOPIC_MODEL_MAP[config["mqtt_topic"]] = model_name

print(f"Modelos cargados: {list(MODELS.keys())}")
print(f"Tópicos suscritos: {TOPIC_MODEL_MAP}")

def on_message(client, userdata, msg):
    try:
        raw = json.loads(msg.payload.decode())
        topic = msg.topic
        print(f"Mensaje recibido en: {topic}")

        if topic not in TOPIC_MODEL_MAP:
            print("Tópico no registrado en models.json")
            return

        entity_type = TOPIC_MODEL_MAP[topic]
        id_field = MODELS[entity_type]["id_field"]

        payload = raw.copy()

        if "data" in raw:
            is_base64 = raw.get("data_encode") == "base64" or entity_type == "lora_wan"
            
            if is_base64:
                try:
                    decoded_bytes = base64.b64decode(raw["data"])
                    decoded_str = decoded_bytes.decode('utf-8')
                    try:
                        decoded_json = json.loads(decoded_str)
                        if isinstance(decoded_json, dict):
                            payload.update(decoded_json)
                            payload["data"] = decoded_json
                        else:
                            payload["data"] = decoded_json
                    except json.JSONDecodeError:
                        payload["data"] = decoded_str
                except Exception:
                    pass 

        try:
            entity = json_to_ngsi_entity(payload, entity_type, id_field)
        except Exception as e:
            print(f"Error creando entidad ({entity_type}): {e}")
            return
        
        
        r = requests.post(ORION_URL, json=entity)
        if r.status_code == 201:
            print(f"Entidad creada: {entity['id']}")
        elif r.status_code == 422:
            attrs_only = entity.copy()
            attrs_only.pop("id", None)
            attrs_only.pop("type", None)
            requests.patch(f"{ORION_URL}/{entity['id']}/attrs", json=attrs_only)
            print(f"Entidad actualizada: {entity['id']}")
        else:
            print(f"Error Orion: {r.text}")

    except Exception as e:
        print(f"Error general: {e}")

if __name__ == "__main__":
    client = mqtt.Client()
    client.on_message = on_message
    client.connect(MQTT_BROKER_HOST, MQTT_BROKER_PORT, 60)

    for topic in TOPIC_MODEL_MAP:
        client.subscribe(topic)

    print("Servidor MQTT escuchando...")
    client.loop_forever()
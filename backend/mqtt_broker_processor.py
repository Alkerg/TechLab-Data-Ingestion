import json
import base64
import os
import paho.mqtt.client as mqtt
import requests
import re
from dotenv import load_dotenv

load_dotenv()

MQTT_BROKER_HOST = os.getenv("MQTT_BROKER_HOST", "localhost")
MQTT_TLS_BOOL = os.getenv("MQTT_TLS_BOOL", False)
MQTT_BROKER_PORT = int(os.getenv("MQTT_BROKER_PORT", "1883"))
DATA_BROKER_URL = os.getenv("DATA_BROKER_URL", "http://data-broker:8000")

MODELS_FILE = "./schemas/models.json"
try:
    with open(MODELS_FILE, 'r') as f:
        MODELS = json.load(f)
except Exception as e:
    print(f"Error cargando modelos: {e}")
    MODELS = {}

TOPIC_MODEL_MAP = {}
for model_name, config in MODELS.items():
    if "mqtt_topic" in config:
        TOPIC_MODEL_MAP[config["mqtt_topic"]] = model_name

def get_value_from_path(data, path):
    keys = re.split(r'\.|\[(\d+)\]', path)
    keys = [k for k in keys if k and k != '']
    current = data
    try:
        for key in keys:
            if isinstance(current, list):
                key = int(key)
                current = current[key]
            else:
                current = current[key]
        return current
    except Exception:
        return None

def apply_mappings(payload, mappings):
    for attr_name, path in mappings.items():
        val = get_value_from_path(payload, path)
        if val is not None:
            payload[attr_name] = val
    return payload

def on_message(client, userdata, msg):
    try:
        raw = json.loads(msg.payload.decode())
        topic = msg.topic
        print("[topic]:", topic)
        print("[raw]\n", raw, "\n")

        if topic not in TOPIC_MODEL_MAP:
            return

        entity_type = TOPIC_MODEL_MAP[topic]
        
        model_config = MODELS.get(entity_type, {})
        
        payload = raw.copy()

        if "data" in raw:
            is_base64 = raw.get("data_encode") == "base64" or entity_type == "lora_wan"
            if is_base64:
                try:
                    decoded_str = base64.b64decode(raw["data"]).decode('utf-8')
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

        if "mappings" in model_config:
            payload = apply_mappings(payload, model_config["mappings"])

        ingest_url = f"{DATA_BROKER_URL}/ingest/{entity_type}"
        
        try:
            r = requests.post(ingest_url, json=payload)
            if r.status_code in [200, 201]:
                print(f"[{entity_type}] Procesado exitosamente por Data Broker.")
            else:
                print(f"[{entity_type}] Error en Data Broker ({r.status_code}): {r.text}")
                
        except requests.exceptions.RequestException as e:
            print(f"Error conectando con Data Broker: {e}")

    except Exception as e:
        print(f"Error procesando mensaje MQTT: {e}")

if __name__ == "__main__":
    client = mqtt.Client()
    client.on_message = on_message

    # Configuración TLS para despliegue
    #client.tls_set()
    #client.tls_insecure_set(True)        

    client.connect(MQTT_BROKER_HOST, MQTT_BROKER_PORT, 60)

    for topic in TOPIC_MODEL_MAP:
        client.subscribe(topic)
        print(f"Suscrito a: {topic}")

    client.loop_forever()
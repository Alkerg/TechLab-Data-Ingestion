import json
import base64
import os
import ssl
import threading
import time
import paho.mqtt.client as mqtt
import requests
from utils import load_file
from dotenv import load_dotenv

load_dotenv()

MQTT_BROKER_HOST = os.getenv("MQTT_BROKER_HOST", "mqtt-broker")
MQTT_BROKER_PORT = int(os.getenv("MQTT_BROKER_PORT", "8883"))
DATA_BROKER_URL = os.getenv("DATA_BROKER_URL", "http://data-broker:8000")
USE_TLS = os.getenv("USE_TLS", "true").lower() == "true"
DEVICES_FILE = "./schemas/devices.json"
TYPES_FILE = "./schemas/types.json"
WATCH_INTERVAL = int(os.getenv("WATCH_INTERVAL", "3"))

TOPIC_MODEL_MAP = {}
TOPICS_LIST = []

def load_topics_and_types():
    global TOPIC_MODEL_MAP, TOPICS_LIST
    devices = load_file(DEVICES_FILE) or {}
    load_file(TYPES_FILE) or {}

    new_map = {}
    new_topics = []

    for device, config in devices.items():
        if "mqtt_topic" in config:
            new_map[config["mqtt_topic"]] = {"entity_type": config["entity_type"], "device": device}
            new_topics.append(config["mqtt_topic"])

    TOPIC_MODEL_MAP = new_map
    TOPICS_LIST = new_topics

def subscribe_to_topics(client):
    for topic in TOPICS_LIST:
        client.subscribe(topic)
        print(f"Suscrito a: {topic}")

def reload_and_subscribe(client):
    global TOPIC_MODEL_MAP, TOPICS_LIST

    devices = load_file(DEVICES_FILE) or {}
    load_file(TYPES_FILE) or {}

    new_map = {}
    new_topics = []

    for device, config in devices.items():
        if "mqtt_topic" in config:
            new_map[config["mqtt_topic"]] = {"entity_type": config["entity_type"], "device": device}
            new_topics.append(config["mqtt_topic"])

    added = set(new_topics) - set(TOPICS_LIST)
    removed = set(TOPICS_LIST) - set(new_topics)

    if not added and not removed:
        print("devices.json modificado pero sin cambios en topics MQTT.")
        return

    for topic in removed:
        client.unsubscribe(topic)
        print(f"Desuscrito de: {topic}")

    for topic in added:
        client.subscribe(topic)
        print(f"Suscrito a nuevo topic: {topic}")

    TOPIC_MODEL_MAP = new_map
    TOPICS_LIST = new_topics

    print(f"Topics actualizados. Total activos: {len(TOPICS_LIST)} | Añadidos: {len(added)} | Eliminados: {len(removed)}")

def watch_devices_file(client, interval=WATCH_INTERVAL):
    try:
        last_mtime = os.path.getmtime(DEVICES_FILE)
    except OSError:
        last_mtime = 0

    print(f"Monitor de archivo de dispositivos iniciado (intervalo: {interval}s)")

    while True:
        time.sleep(interval)
        try:
            current_mtime = os.path.getmtime(DEVICES_FILE)
            if current_mtime != last_mtime:
                print(f"Cambio detectado en {DEVICES_FILE}, recargando configuración...")
                last_mtime = current_mtime
                reload_and_subscribe(client)
        except OSError as e:
            print(f"Error accediendo a {DEVICES_FILE}: {e}")
        except Exception as e:
            print(f"Error en monitor de archivo de dispositivos: {e}")

def on_message(client, userdata, msg):
    try:
        raw = json.loads(msg.payload.decode())
        print(f"Mensaje recibido en {msg.topic}: {raw}")
        topic = msg.topic

        if topic not in TOPIC_MODEL_MAP:
            print(f"Advertencia: Topic '{topic}' no registrado. Registrados: {list(TOPIC_MODEL_MAP.keys())}")
            return

        entity_type = TOPIC_MODEL_MAP[topic]["entity_type"]
        entity_name = TOPIC_MODEL_MAP[topic]["device"]
                
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

        ingest_url = f"{DATA_BROKER_URL}/ingest/{entity_name}"
        
        try:
            r = requests.post(ingest_url, json=payload)
            if r.status_code in [200, 201]:
                print(f"[{entity_name}] Procesado exitosamente por Data Broker. \n")
            else:
                print(f"[{entity_name}] Error en Data Broker ({r.status_code}): {r.text} \n")

        except requests.exceptions.RequestException as e:
            print(f"Error conectando con Data Broker: {e}")

    except Exception as e:
        print(f"Error procesando mensaje MQTT: {e}")

if __name__ == "__main__":
    print("Iniciando MQTT Broker Processor...")
    load_topics_and_types()
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
    client.on_message = on_message

    if USE_TLS:
        client.username_pw_set("processor", "processor")
        client.tls_set(cert_reqs=ssl.CERT_NONE)
        client.tls_insecure_set(True)
              
    try:
        client.connect(MQTT_BROKER_HOST, MQTT_BROKER_PORT, 60)
        subscribe_to_topics(client)
    except Exception as e:
        print(f"Error conectando al broker MQTT: {e}")
        exit(1)

    watcher = threading.Thread(target=watch_devices_file, args=(client,), daemon=True)
    watcher.start()

    client.loop_forever()
# mqtt_broker.py
import os
import json
import time
import requests
import paho.mqtt.client as mqtt

MQTT_HOST = os.getenv("MQTT_HOST", "localhost")
MQTT_PORT = int(os.getenv("MQTT_PORT", 1883))
TOPIC = os.getenv("MQTT_TOPIC", "sensors/parking")
DATA_BROKER_URL = os.getenv("DATA_BROKER_URL", "http://localhost:5000/ingest")

def on_connect(client, userdata, flags, rc):
    print(f"Connected to MQTT broker {MQTT_HOST}:{MQTT_PORT}, rc={rc}")
    client.subscribe(TOPIC)

def on_message(client, userdata, msg):
    try:
        payload = json.loads(msg.payload.decode())
        parking_id = payload["parking_id"]
        timestamp = payload["timestamp"]
        parking_spots = payload.get("parking_spots", [])

        data = {
            "parking_id": parking_id,
            "timestamp": timestamp,
            "parking_spots": parking_spots
        }
        forward = {"type": "parking", "data": data}
        r = requests.post(DATA_BROKER_URL, json=forward)
        if r.status_code >= 400:
            print("Error forwarding to Data Broker:", r.text)
        else:
            print(f"Forwarded parking {parking_id} -> Orion via Data Broker")
    except Exception as e:
        print("Error processing MQTT message:", e)

def main():
    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect(MQTT_HOST, MQTT_PORT)
    client.loop_forever()

if __name__ == "__main__":
    main()

# send_mqtt_test.py
import time
import json
import random
import paho.mqtt.client as mqtt
from datetime import datetime, timezone

MQTT_HOST = "localhost"
MQTT_PORT = 1883
TOPIC = "sensors/parking"

def random_parking_payload(parking_id="PARK01", num_spots=6):
    spots = []
    for i in range(1, num_spots+1):
        spots.append({
            "spot_id": f"S{i}",
            "isOccuppied": random.choice([True, False])
        })
    payload = {
        "parking_id": parking_id,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "parking_spots": spots
    }
    return payload

if __name__ == "__main__":
    client = mqtt.Client()
    client.connect(MQTT_HOST, MQTT_PORT)
    client.loop_start()
    try:
        while True:
            p = random_parking_payload()
            client.publish(TOPIC, json.dumps(p))
            print("Published MQTT:", p)
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nNo more data sent")
        client.loop_stop()
        client.disconnect()

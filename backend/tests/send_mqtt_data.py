# send_mqtt_test.py
import time
import json
import random
import paho.mqtt.client as mqtt
import base64
from datetime import datetime, timezone

MQTT_HOST = "localhost"
MQTT_HOST = "oti-test.jorgeparishuana.dev"
MQTT_PORT = 1883
TOPIC = "cuenta_personas/data"

def encode_base64_payload(payload_dict):
    json_str = json.dumps(payload_dict)
    b64 = base64.b64encode(json_str.encode()).decode()
    return {"data": b64}

def random_smart_parking_mqtt_data():

    id_number = random.randint(1, 5)
    state = ""
    for i in range(6):
        state += random.choice(["0", "1"])

    parking_id = f"A{id_number}"

    payload = {
        "parking_id": parking_id,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "state": state
    }
    return payload

def random_cuenta_personas_mqtt_data():

    id_number = random.randint(1, 2)
    cam_code = f"CAM{id_number}"
    aforo = random.randint(0, 20)

    payload = {
        "camCode": cam_code,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "aforo": aforo
    }
    return payload

def random_lora_mqtt_data():
    return {
        "adr": True,
        "applicationID": str(random.randint(1, 2)),
        "applicationName": "mqtt", 
        "data": "SGVsbG8gUkFLV2lyZWxlc3M=", 
        "data_encode": "base64", 
        "devEUI": "ae10fccc25ae10fc", 
        "deviceName": "mqtt_test",
        "fCnt": 1, 
        "fPort": 1, 
        "rxInfo": [ 
            {
            "gatewayID": "ac1f09fffe0fd50c", 
            "loRaSNR": 9.2, 
            "location": { 
                "altitude": random.randint(0, 100),
                "latitude": random.uniform(-90, 90),
                "longitude": random.uniform(-180, 180)
            },
            "rssi": -36 
            }
        ],

        "timestamp": 1708395729, 
        
        "txInfo": {
            "dr": 0, 
            "frequency": random.randint(860000000, 1020000000) 
        }
    }

if __name__ == "__main__":
    client = mqtt.Client()
    client.tls_set()
    client.connect(MQTT_HOST, MQTT_PORT)
    client.loop_start()

    try:
        while True:
            smart_parking_data = random_smart_parking_mqtt_data()
            cuenta_personas_data = random_cuenta_personas_mqtt_data()
            lora_data = random_lora_mqtt_data()

            #client.publish(TOPIC, json.dumps(smart_parking_data))
            #print("Published to MQTT Broker:", smart_parking_data)

            wrapped = encode_base64_payload(cuenta_personas_data) 
            #Eclient.publish(TOPIC, json.dumps(wrapped))
            #print("Published to MQTT Broker:", cuenta_personas_data)

            client.publish(TOPIC, json.dumps(lora_data))
            print("Published to MQTT Broker:", lora_data)
            
            time.sleep(2)

    except KeyboardInterrupt:
        print("\nNo more data sent")
        client.loop_stop()
        client.disconnect()

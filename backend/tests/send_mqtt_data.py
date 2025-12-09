# send_mqtt_test.py
import time
import json
import random
import paho.mqtt.client as mqtt
from datetime import datetime, timezone

MQTT_HOST = "localhost"
MQTT_PORT = 1883
TOPIC = "lorawan/data"

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

    id_number = random.randint(1, 3)
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
        "applicationID": str(random.randint(1, 3)),
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
                "altitude": 0,
                "latitude": 0,
                "longitude": 0
            },
            "rssi": -36 
            }
        ],

        "timestamp": 1708395729, 
        
        "txInfo": {
            "dr": 0, 
            "frequency": 868100000 
        }
    }

if __name__ == "__main__":
    client = mqtt.Client()
    client.connect(MQTT_HOST, MQTT_PORT)
    client.loop_start()

    try:
        while True:
            smart_parking_data = random_smart_parking_mqtt_data()
            cuenta_personas_data = random_cuenta_personas_mqtt_data()
            lora_data = random_lora_mqtt_data()

            #client.publish(TOPIC, json.dumps(smart_parking_data))
            #print("Published to MQTT Broker:", smart_parking_data)

            client.publish(TOPIC, json.dumps(cuenta_personas_data))
            print("Published to MQTT Broker:", cuenta_personas_data)

            #client.publish(TOPIC, json.dumps(lora_data))
            #print("Published to MQTT Broker:", lora_data)
            
            time.sleep(2)

    except KeyboardInterrupt:
        print("\nNo more data sent")
        client.loop_stop()
        client.disconnect()

import time
import json
import random
import ssl
import paho.mqtt.client as mqtt
import base64
from datetime import datetime, timezone


""" MQTT_HOST = "oti-test.jorgeparishuana.dev"
MQTT_PORT = 8883
TOPIC = "lora_wan_1/data"
SENDING_RATE = 2 """


MQTT_HOST = "localhost"
MQTT_PORT = 8883
TOPIC = "lora_wan_4/data"
SENDING_RATE = 2

USE_TLS = True
VERIFY_CERTIFICATE = False

def encode_base64_payload(payload_dict):
    json_str = json.dumps(payload_dict)
    b64 = base64.b64encode(json_str.encode()).decode()
    return {"data": b64}

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

def random_lora_mqtt_data(application_id):
    return {
        "adr": True,
        "applicationID": str(application_id),
        "applicationName": "mqtt", 
        "data": str(base64.b64encode(b'{"temperature":' + str(random.randint(20, 30)).encode() + b',"humidity":60}'), 'utf-8'),
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
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)

    if USE_TLS:
        client.username_pw_set("lora_wan_4", "lora_wan_4")
        if VERIFY_CERTIFICATE:
            client.tls_set()
        else:
            client.tls_set(cert_reqs=ssl.CERT_NONE)
        client.tls_insecure_set(True) 

    client.connect(MQTT_HOST, MQTT_PORT)
    client.loop_start()

    try:
        while True:

            lora_data = random_lora_mqtt_data(4)

            # Envia datos del proyecto LoRaWAN
            client.publish(TOPIC, json.dumps(lora_data))
            print("Publicado a MQTT Broker:", lora_data)
            
            time.sleep(SENDING_RATE)
    except KeyboardInterrupt:
        print("\nFin de la prueba MQTT")
        client.loop_stop()
        client.disconnect()

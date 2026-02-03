# send_http_test.py
import time
import requests
import random
from datetime import datetime, timezone

HTTP_BROKER_URL_CUENTA_PERSONAS = "http://localhost:8000/ingest/cuenta_personas"
#HTTP_BROKER_URL_CUENTA_PERSONAS = "https://oti-test.jorgeparishuana.dev:4200/ingest/cuenta_personas"
HTTP_BROKER_URL_SMART_PARKING = "http://localhost:8000/ingest/smart_parking"
#HTTP_BROKER_URL_SMART_PARKING = "https://oti-test.jorgeparishuana.dev:4200/ingest/smart_parking"

def random_smart_parking_http_data():

    id_number = random.randint(1, 2)
    state = ""
    for i in range(6):
        state += random.choice(["0", "1"])

    parking_id = f"A{id_number}"

    """payload = {
        "parking_id": parking_id,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "state": state
    } """

    payload = {
        "parking_id": parking_id,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "parking_spots": [
            {
                "spot_id": f"{parking_id}_S1",
                "occupied": random.choice([True, False])
            },
            {
                "spot_id": f"{parking_id}_S2",
                "occupied": random.choice([True, False])
            },
            {
                "spot_id": f"{parking_id}_S3",
                "occupied": random.choice([True, False])
            },
            {
                "spot_id": f"{parking_id}_S4",
                "occupied": random.choice([True, False])
            }
        ]
    } 

    return payload

def random_cuenta_personas_http_data():

    id_number = random.randint(1, 2)
    cam_code = f"A{id_number}"
    aforo = random.randint(0, 20)

    payload = {
        "camCode": cam_code,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "aforo": aforo
    }
    return payload

if __name__ == "__main__":
    try:
        while True:
            smart_parking_data = random_smart_parking_http_data()
            #requests.post(HTTP_BROKER_URL_SMART_PARKING, json=smart_parking_data)
            print("\nSmart Parking data sent via HTTP:", smart_parking_data)
            time.sleep(1)
            cuenta_personas_data = random_cuenta_personas_http_data()
            requests.post(HTTP_BROKER_URL_CUENTA_PERSONAS, json=cuenta_personas_data)
            print("\nCuenta Personas data sent via HTTP:", cuenta_personas_data)

            time.sleep(2)
    except KeyboardInterrupt:
        print("\nEnd of HTTP testing")

import time
import requests
import random
from datetime import datetime, timezone

HTTP_BROKER_URL_SMART_PARKING = "http://localhost:8000/ingest/smart_parking_1"
#HTTP_BROKER_URL_SMART_PARKING = "https://oti-test.jorgeparishuana.dev:4200/ingest/smart_parking_1"

SENDING_RATE = 2

def random_smart_parking_http_data():

    id_number = 1
    parking_id = f"A{id_number}"

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

if __name__ == "__main__":
    try:
        while True:
            smart_parking_data = random_smart_parking_http_data()
            r = requests.post(HTTP_BROKER_URL_SMART_PARKING, json=smart_parking_data)
            print("\nEnviando datos de Smart Parking simulados:", smart_parking_data)
            print("Response:", r.text)

            time.sleep(SENDING_RATE)
    except KeyboardInterrupt:
        print("\nFin de la prueba HTTP")

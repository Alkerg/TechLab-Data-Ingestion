# send_http_test.py
import time
import requests
import random
from datetime import datetime, timezone

HTTP_BROKER_URL = "http://localhost:8000/camera"

def send(cam_id):
    payload = {
        "camCode": cam_id,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "aforo": random.randint(0, 50)
    }
    r = requests.post(HTTP_BROKER_URL, json=payload)
    print("Send HTTP:", payload, "->", r.status_code, r.text)

if __name__ == "__main__":
    cam_id = "CAM001"
    try:
        while True:
            send(cam_id)
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nNo more data sent")

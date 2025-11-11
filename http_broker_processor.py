# http_broker.py
import os
import requests
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uvicorn

DATA_BROKER_URL = os.getenv("DATA_BROKER_URL", "http://localhost:5000/ingest")

app = FastAPI(title="HTTP Broker")

class IncomingCamera(BaseModel):
    camCode: str
    timestamp: str
    aforo: int

@app.post("/camera")
async def camera_receive(cam: IncomingCamera):
    payload = {
        "type": "counting_camera",
        "data": cam.dict()
    }
    r = requests.post(DATA_BROKER_URL, json=payload)
    if r.status_code >= 400:
        raise HTTPException(status_code=500, detail=f"Failed to forward to Data Broker: {r.text}")
    return {"status": "forwarded", "data_broker_resp": r.json()}

if __name__ == "__main__":
    uvicorn.run("http_broker_processor:app", host="0.0.0.0", port=8000, reload=False)

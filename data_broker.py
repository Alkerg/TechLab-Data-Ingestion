# data_broker.py
import os
import requests
import uvicorn
from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel
from typing import List, Dict, Any
from datetime import datetime

ORION_URL = os.getenv("ORION_URL", "http://localhost:1026/v2/entities")
HEADERS = {
    "Content-Type": "application/json",
    "Fiware-Service": os.getenv("FIWARE_SERVICE", "techlab"),
    "Fiware-ServicePath": os.getenv("FIWARE_SERVICEPATH", "/")
}

app = FastAPI(title="Data Broker")

class CuentaPersonas(BaseModel):
    camCode: str
    timestamp: str
    aforo: int

class ParkingSpot(BaseModel):
    spot_id: str
    isOccuppied: bool

class ParkingPayload(BaseModel):
    parking_id: str
    timestamp: str
    parking_spots: List[ParkingSpot]

def normalize_timestamp(ts: str) -> str:
    """Convierte timestamp a formato NGSI-v2 (YYYY-MM-DDTHH:MM:SSZ)"""
    try:
        dt = datetime.fromisoformat(ts.replace("Z", "+00:00"))
        return dt.strftime("%Y-%m-%dT%H:%M:%SZ")
    except Exception:
        return ts 

@app.post("/ingest")
async def ingest(payload: Dict[str, Any]):
    """
    Recibe payloads normalizados desde brokers de protocolo.
    payload debe contener un campo 'type' con 'counting_camera' o 'parking',
    y el objeto 'data' con el modelo correspondiente.
    """
    try:
        ptype = payload.get("type")
        data = payload.get("data")
        if ptype == "counting_camera":
            return handle_counting_camera(data)
        elif ptype == "parking":
            return handle_parking(data)
        else:
            raise HTTPException(status_code=400, detail="type must be 'counting_camera' or 'parking'")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

def post_or_update_entity(entity: dict):
    """Intenta crear la entidad. Si ya existe actualiza los atributos."""
    eid = entity.get("id")
    url_entity = f"{ORION_URL}/{eid}"

    r = requests.post(ORION_URL, json=entity, headers=HEADERS)
    if r.status_code in (201, 204):
        return {"status": "created", "code": r.status_code}

    attrs = {}
    for k, v in entity.items():
        if k in ("id", "type"):
            continue
        attrs[k] = v
    patch_url = f"{ORION_URL}/{eid}/attrs"
    r2 = requests.patch(patch_url, json=attrs, headers=HEADERS)
    return {"status": "patched", "code": r2.status_code, "response": r2.text}

def handle_counting_camera(data: dict):
    cam = CuentaPersonas(**data)
    entity = {
        "id": f"Camera:{cam.camCode}",
        "type": "CameraCount",
        "peopleCount": {"value": cam.aforo, "type": "Integer"},
        "timestamp": {"value": normalize_timestamp(cam.timestamp), "type": "DateTime"}
    }
    res = post_or_update_entity(entity)
    return {"entity": entity, "orion_response": res}

def handle_parking(data: dict):
    parking = ParkingPayload(**data)
    spots_value = []
    for s in parking.parking_spots:
        spots_value.append({"spot_id": s.spot_id, "isOccuppied": s.isOccuppied})

    entity = {
        "id": f"Parking:{parking.parking_id}",
        "type": "ParkingSpotCollection",
        "parking_spots": {"value": spots_value, "type": "Structured"},
        "timestamp": {"value": normalize_timestamp(parking.timestamp), "type": "DateTime"}
    }
    res = post_or_update_entity(entity)
    print(res)
    return {"entity": entity, "orion_response": res}

if __name__ == "__main__":
    uvicorn.run("data_broker:app", host="0.0.0.0", port=5000, reload=False)

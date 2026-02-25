import json, requests, uvicorn, os
from fastapi import FastAPI, HTTPException
from utils import json_to_ngsi_entity, load_file
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="Data Broker v2")

ORION_URL = os.getenv("ORION_URL", "http://localhost:1026/v2/entities")
DEVICES_FILE = "./schemas/devices.json"
TYPES_FILE = "./schemas/types.json"

DEVICES = load_file(DEVICES_FILE)
TYPES = load_file(TYPES_FILE)

@app.post("/ingest/{entity_name}")
def ingest(entity_name: str, payload: dict):
    global DEVICES, TYPES

    if entity_name not in DEVICES:
        print(f"Entidad '{entity_name}' no encontrada en {DEVICES_FILE}.")
        DEVICES = load_file(DEVICES_FILE)
        
    if entity_name not in DEVICES:
        available_entities = list(DEVICES.keys())
        raise HTTPException(400, f"Entidad '{entity_name}' no registrada. Registradas: {available_entities}")
    
    entity_type = DEVICES[entity_name]["entity_type"]
    id_field = TYPES[entity_type]["id_field"]
    data_fields = TYPES[entity_type]["data_fields"] if "data_fields" in TYPES[entity_type] else []

    try:
        entity = json_to_ngsi_entity(payload, entity_type, id_field, data_fields)
    except ValueError as e:
        raise HTTPException(400, str(e))

    try:
        r = requests.post(
            ORION_URL,
            json=entity,
            headers={"Content-Type": "application/json"}
        )
    except requests.exceptions.RequestException as e:
        raise HTTPException(502, f"Error conectando con Orion: {e}")

    if r.status_code == 201:
        return {"status": "created", "entity_id": entity["id"]}

    elif r.status_code == 422:
        attrs_only = entity.copy()
        attrs_only.pop("id", None)
        attrs_only.pop("type", None)

        r_patch = requests.patch(
            f"{ORION_URL}/{entity['id']}/attrs",
            json=attrs_only,
            headers={"Content-Type": "application/json"}
        )

        
        if r_patch.status_code == 204:
             return {"status": "updated", "entity_id": entity["id"]}
        else:
             return {"status": "update_failed", "error": r_patch.text}

    else:
        return {"error": r.text, "status_code": r.status_code}

if __name__ == "__main__":
    uvicorn.run("data_broker:app", host="0.0.0.0", port=8000)
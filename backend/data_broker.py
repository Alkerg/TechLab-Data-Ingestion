import json, requests, uvicorn, os
from fastapi import FastAPI, HTTPException
# Eliminamos load_schemas de la importación
from utils import json_to_ngsi_entity
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="Data Broker v2")

ORION_URL = os.getenv("ORION_URL", "http://localhost:1026/v2/entities")
MODELS_FILE = "./schemas/models.json"

def load_models_config():
    try:
        with open(MODELS_FILE, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Error: No se encontró el archivo {MODELS_FILE}")
        return {}
    except json.JSONDecodeError:
        print(f"Error: {MODELS_FILE} no es un JSON válido")
        return {}

MODELS = load_models_config()

@app.post("/ingest/{entity_type}")
def ingest(entity_type: str, payload: dict):
    global MODELS

    if entity_type not in MODELS:
        print(f"Modelo '{entity_type}' no encontrado en memoria.")
        MODELS = load_models_config()
        
    if entity_type not in MODELS:
        available = list(MODELS.keys())
        raise HTTPException(400, f"Modelo '{entity_type}' no registrado. Disponibles: {available}")

    id_field = MODELS[entity_type]["id_field"]

    try:
        entity = json_to_ngsi_entity(payload, entity_type, id_field)
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
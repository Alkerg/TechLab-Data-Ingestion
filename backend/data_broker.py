import json, requests, uvicorn, os
from fastapi import FastAPI, HTTPException
from utils import json_to_ngsi_entity
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="Data Broker v2")

ORION_URL = os.getenv("ORION_URL", "http://localhost:1026/v2/entities")

# Cargar modelos dinámicamente
with open("./schemas/models.json") as f:
    MODELS = json.load(f)


@app.post("/ingest/{entity_type}")
def ingest(entity_type: str, payload: dict):

    if entity_type not in MODELS:
        raise HTTPException(400, "Modelo no registrado")

    id_field = MODELS[entity_type]["id_field"]

    entity = json_to_ngsi_entity(payload, entity_type, id_field)


    r = requests.post(
        ORION_URL,
        json=entity,
        headers={"Content-Type": "application/json"}
    )

    if r.status_code == 201:
        return {"status": "created", "entity_id": entity["id"]}

    elif r.status_code == 422:
        attrs_only = entity.copy()
        attrs_only.pop("id")
        attrs_only.pop("type")

        requests.patch(
            f"{ORION_URL}/{entity['id']}/attrs",
            json=attrs_only,
            headers={"Content-Type": "application/json"}
        )

        return {"status": "updated", "entity_id": entity["id"]}

    else:
        return {"error": r.text}

if __name__ == "__main__":
    uvicorn.run("data_broker:app", host="0.0.0.0", port=8000)

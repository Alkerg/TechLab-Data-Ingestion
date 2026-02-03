import os
import json

def json_to_ngsi_entity(payload: dict, entity_type: str, id_field: str, data_fields: list) -> dict:
    """Convierte un diccionario JSON en una entidad NGSI."""

    data_id = payload.get(id_field)
    
    if data_id is None:
        raise ValueError(f"El campo ID '{id_field}' no está presente en el payload")

    entity = {
        "id": f"{entity_type}:{data_id}",
        "type": entity_type
    }

    for key, value in payload.items():
        if key == id_field or key not in data_fields:
            continue

        if isinstance(value, bool):
            ngsi_type = "Boolean"
        elif isinstance(value, int) or isinstance(value, float):
            ngsi_type = "Number"
        elif isinstance(value, list) or isinstance(value, dict):
            ngsi_type = "StructuredValue"
        else:
            ngsi_type = "Text"

        entity[key] = {
            "type": ngsi_type,
            "value": value
        }

    return entity
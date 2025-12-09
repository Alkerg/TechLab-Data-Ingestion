def json_to_ngsi_entity(payload: dict, entity_type: str, id_field: str) -> dict:
    data_id = payload[id_field]

    entity = {
        "id": f"{entity_type}:{data_id}",
        "type": entity_type
    }

    for key, value in payload.items():
        if key == id_field:
            continue

        # Detectar tipo automáticamente
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

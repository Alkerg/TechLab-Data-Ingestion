import os
import json

def load_schemas(schema_dir: str = "./schemas") -> dict:
    """
    Carga dinámicamente todos los archivos .json en el directorio especificado.
    El nombre del archivo (sin extensión) se convierte en el 'entity_type'.
    """
    models = {}
    
    if not os.path.exists(schema_dir):
        print(f"Advertencia: El directorio {schema_dir} no existe.")
        return models

    for filename in os.listdir(schema_dir):
        if filename.endswith(".json") and filename != "models.json":
            entity_type = filename.replace(".json", "")
            filepath = os.path.join(schema_dir, filename)
            
            try:
                with open(filepath, 'r') as f:
                    config = json.load(f)
                    # Validamos que al menos tenga el campo id_field
                    if "id_field" in config:
                        models[entity_type] = config
                        print(f"Modelo cargado: {entity_type}")
            except Exception as e:
                print(f"Error cargando esquema {filename}: {e}")
                
    return models

def json_to_ngsi_entity(payload: dict, entity_type: str, id_field: str) -> dict:
    data_id = payload.get(id_field)
    
    if data_id is None:
        raise ValueError(f"El campo ID '{id_field}' no está presente en el payload")

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
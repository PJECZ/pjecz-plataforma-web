import json
import os
import requests

EXPEDIENTE_VIRTUAL_API_URL = os.environ.get("EXPEDIENTE_VIRTUAL_API_URL", "")
if EXPEDIENTE_VIRTUAL_API_URL == "":
    print("No se declaro la variable de entorno EXPEDIENTE_VIRTUAL_API_URL")
    exit(1)
EXPEDIENTE_VIRTUAL_API_KEY = os.environ.get("EXPEDIENTE_VIRTUAL_API_KEY", "")
if EXPEDIENTE_VIRTUAL_API_KEY == "":
    print("No se declaro la variable de entorno EXPEDIENTE_VIRTUAL_API_KEY")
    exit(1)

# Armado del cuerpo de petición para la API
request_body = {
    "idJuzgado": 76,
    "idOrigen": 0,
    "numeroExpediente": "1/2022",
}

try:
    respuesta = requests.post(
        EXPEDIENTE_VIRTUAL_API_URL,
        headers={'X-Api-Key': EXPEDIENTE_VIRTUAL_API_KEY},
        json=request_body,
        timeout=32,
    )
    respuesta.raise_for_status()

except requests.exceptions.ConnectionError as err:
    print(f"Error en conexión con el API. {err}")
    exit(1)
except requests.exceptions.Timeout as err:
    print(f"Error de tiempo. {err}")
    exit(1)
except requests.exceptions.HTTPError as err:
    print(f"Error HTTP. {err}")
    exit(1)
except requests.exceptions.RequestException as err:
    print(f"Error desconocido. {err}")
    exit(1)

respuesta_api = respuesta.json()
if "success" in respuesta_api:
    if respuesta_api["success"] is True:
        json_str = json.dumps(respuesta_api, indent=2)
        print(json_str)
        exit(0)
    else:
        print("Dato no encontrado, pero bien!")

print("Respuesta no esperada por parte del API")
exit(0)
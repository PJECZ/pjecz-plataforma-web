"""
Safe string
"""
import re
from datetime import date
from unidecode import unidecode

CONTRASENA_REGEXP = r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)[a-zA-Z\d]{8,48}$"
CURP_REGEXP = r"^[A-Z]{4}\d{6}[A-Z]{6}\d{2}$"
EMAIL_REGEXP = r"^[\w.-]+@[\w.-]+\.\w+$"
EXPEDIENTE_REGEXP = r"^\d+\/[12]\d\d\d(-[a-zA-Z0-9]+(-[a-zA-Z0-9]+)?)?$"
TOKEN_REGEXP = r"^[a-zA-Z0-9_.=+-]+$"
FOLIO_REGEXP = r"^\d+/[12]\d\d\d$"
NUMERO_PUBLICACION_REGEXP = r"^\d+/[12]\d\d\d$"
SENTENCIA_REGEXP = r"^\d+/[12]\d\d\d$"


def safe_string(input_str, max_len=250):
    """Safe string"""
    if not isinstance(input_str, str):
        return ""
    new_string = re.sub(r"[^a-zA-Z0-9]+", " ", unidecode(input_str))
    removed_multiple_spaces = re.sub(r"\s+", " ", new_string)
    final = removed_multiple_spaces.strip().upper()
    return (final[:max_len] + "...") if len(final) > max_len else final


def safe_message(input_str, max_len=250):
    """Safe message"""
    message = str(input_str)
    if message == "":
        message = "Sin descripción"
    return (message[:max_len] + "...") if len(message) > max_len else message


def safe_expediente(input_str):
    """Safe expediente"""
    if not isinstance(input_str, str) or input_str.strip() == "":
        return ""
    elementos = re.sub(r"[^a-zA-Z0-9]+", "|", unidecode(input_str)).split("|")
    try:
        numero = int(elementos[0])
        ano = int(elementos[1])
    except (IndexError, ValueError) as error:
        raise error
    if numero <= 0:
        raise ValueError
    if ano < 1950 or ano > date.today().year:
        raise ValueError
    extra_1 = ""
    if len(elementos) >= 3:
        extra_1 = "-" + elementos[2].upper()
    extra_2 = ""
    if len(elementos) >= 4:
        extra_2 = "-" + elementos[3].upper()
    limpio = f"{str(numero)}/{str(ano)}{extra_1}{extra_2}"
    if len(limpio) > 16:
        raise ValueError
    return limpio


def safe_sentencia(input_str):
    """Safe sentencia"""
    if not isinstance(input_str, str) or input_str.strip() == "":
        return ""
    elementos = re.sub(r"[^0-9A-Z]+", "|", unidecode(input_str)).split("|")
    try:
        numero = int(elementos[0])
        ano = int(elementos[1])
    except (IndexError, ValueError) as error:
        raise error
    if numero <= 0:
        raise ValueError
    if ano < 1950 or ano > date.today().year:
        raise ValueError
    limpio = f"{str(numero)}/{str(ano)}"
    if len(limpio) > 16:
        raise ValueError
    return limpio


def safe_numero_publicacion(input_str):
    """Safe número publicación"""
    return safe_sentencia(input_str)

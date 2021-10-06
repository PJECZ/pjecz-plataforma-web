"""
Safe string
"""
import re
from unidecode import unidecode

CONTRASENA_REGEXP = r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)[a-zA-Z\d]{8,48}$"
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

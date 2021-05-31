"""
Safe string
"""
import re
from datetime import date
from unidecode import unidecode


def safe_string(input_str):
    """Safe string"""
    if not isinstance(input_str, str):
        return ""
    new_string = re.sub(r"[^a-zA-Z0-9]+", " ", unidecode(input_str))
    removed_multiple_spaces = re.sub(r"\s+", " ", new_string)
    return removed_multiple_spaces.strip().upper()


def safe_expediente(input_str):
    """Safe expediente"""
    if not isinstance(input_str, str):
        return ""
    elementos = re.sub(r"[^0-9]+", "-", input_str).split("-")
    try:
        numero = int(elementos[0])
        ano = int(elementos[1])
    except (IndexError, ValueError):
        return ""
    if numero <= 0:
        return ""
    if ano < 1950 or ano > date.today().year:
        return ""
    return f"{str(numero)}/{str(ano)}"


def safe_numero_publicacion(input_str):
    """Safe número publicación"""
    return safe_expediente(input_str)

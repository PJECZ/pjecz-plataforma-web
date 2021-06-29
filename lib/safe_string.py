"""
Safe string
"""
import re
from datetime import date
from unidecode import unidecode


def safe_string(input_str, max_len=250):
    """Safe string"""
    if not isinstance(input_str, str):
        return ""
    new_string = re.sub(r"[^a-zA-Z0-9]+", " ", unidecode(input_str))
    removed_multiple_spaces = re.sub(r"\s+", " ", new_string)
    final = removed_multiple_spaces.strip().upper()
    return (final[:max_len] + '...') if len(final) > max_len else final


def safe_message(input_str, max_len=250):
    """Safe message"""
    message = str(input_str)
    if message == '':
        message = "Sin descripción"
    return (message[:max_len] + '...') if len(message) > max_len else message


def safe_expediente(input_str):
    """Safe expediente"""
    if not isinstance(input_str, str) or input_str.strip() == "":
        return ""
    elementos = re.sub(r"[^0-9]+", "-", input_str).split("-")
    try:
        numero = int(elementos[0])
        ano = int(elementos[1])
    except (IndexError, ValueError) as error:
        raise error
    if numero < 0:
        raise ValueError
    if ano < 1950 or ano > date.today().year:
        raise ValueError
    return f"{str(numero)}/{str(ano)}"


def safe_numero_publicacion(input_str):
    """Safe número publicación"""
    return safe_expediente(input_str)


def safe_sentencia(input_str):
    """Safe sentencia"""
    return safe_expediente(input_str)

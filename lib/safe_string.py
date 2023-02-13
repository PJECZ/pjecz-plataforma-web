"""
Safe string
"""
import re
from datetime import date
from unidecode import unidecode

CONTRASENA_REGEXP = r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)[a-zA-Z\d]{8,48}$"
CURP_REGEXP = r"^[A-Z]{4}\d{6}[A-Z]{6}[A-Z0-9]{2}$"
EMAIL_REGEXP = r"^[\w.-]+@[\w.-]+\.\w+$"
EXPEDIENTE_REGEXP = r"^\d+\/[12]\d\d\d(-[a-zA-Z0-9]+(-[a-zA-Z0-9]+)?)?$"
FOLIO_REGEXP = r"^\d+/[12]\d\d\d$"
MAC_ADDRESS_REGEXP = r"([0-9A-Fa-f]{2}[:-]?){5}([0-9A-Fa-f]{2})"
NUMERO_PUBLICACION_REGEXP = r"^\d+/[12]\d\d\d$"
SENTENCIA_REGEXP = r"^\d+/[12]\d\d\d$"
TOKEN_REGEXP = r"^[a-zA-Z0-9_.=+-]+$"
URL_REGEXP = r"^(https?:\/\/)[0-9a-z-_]*(\.[0-9a-z-_]+)*(\.[a-z]+)+(\/[0-9a-z%-_]*)*?\/?$"


def safe_clave(input_str, max_len=16):
    """Safe clave"""
    if not isinstance(input_str, str):
        return ""
    new_string = re.sub(r"[^a-zA-Z0-9()-]+", " ", unidecode(input_str))
    removed_multiple_spaces = re.sub(r"\s+", " ", new_string)
    spaces_to_dashes = re.sub(r"\s+", "-", removed_multiple_spaces)
    final = spaces_to_dashes.strip().upper()
    if len(final) > max_len:
        return final[:max_len]
    return final


def safe_email(input_str, search_fragment=False):
    """Safe string"""
    if not isinstance(input_str, str):
        return ""
    final = input_str.strip().lower()
    if search_fragment:
        if re.match(r"^[\w.-]*@*[\w.-]*\.*\w*$", final) is None:
            return ""
        return final
    if re.match(EMAIL_REGEXP, final) is None:
        return ""
    return final


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


def safe_string(input_str, max_len=250, do_unidecode=True, save_enie=False, to_uppercase=True):
    """Safe string"""
    if not isinstance(input_str, str):
        return ""
    if do_unidecode:
        new_string = re.sub(r"[^a-zA-Z0-9.()/-]+", " ", input_str)
        if save_enie:
            new_string = ""
            for char in input_str:
                if char == "ñ":
                    new_string += "ñ"
                elif char == "Ñ":
                    new_string += "Ñ"
                else:
                    new_string += unidecode(char)
        else:
            new_string = re.sub(r"[^a-zA-Z0-9.()/-]+", " ", unidecode(input_str))
    else:
        if save_enie is False:
            new_string = re.sub(r"[^a-záéíóúüA-ZÁÉÍÓÚÜ0-9.()/-]+", " ", input_str)
        else:
            new_string = re.sub(r"[^a-záéíóúüñA-ZÁÉÍÓÚÜÑ0-9.()/-]+", " ", input_str)
    removed_multiple_spaces = re.sub(r"\s+", " ", new_string)
    final = removed_multiple_spaces.strip()
    if to_uppercase:
        final = final.upper()
    if max_len == 0:
        return final
    return (final[:max_len] + "...") if len(final) > max_len else final


def safe_text(input_str, max_len=4096, to_uppercase=True):
    """Safe string"""
    if not isinstance(input_str, str):
        return ""
    new_string = re.sub(r"[^a-zA-Z0-9@\n()\?=\[\]:/_.-]+", " ", unidecode(input_str))
    final = new_string.strip()
    if to_uppercase:
        final = final.upper()
    if max_len == 0:
        return final
    return (final[:max_len] + "...") if len(final) > max_len else final


def safe_message(input_str, max_len=250, return_void=False):
    """Safe message"""
    message = str(input_str)
    if message == "":
        if return_void:
            return ""
        message = "Sin descripción"
    return (message[:max_len] + "...") if len(message) > max_len else message


def safe_numero_publicacion(input_str):
    """Safe número publicación"""
    return safe_sentencia(input_str)


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


def safe_url(input_str):
    """Safe URL"""
    if not isinstance(input_str, str) or input_str.strip() == "":
        return ""
    input_str = input_str.strip()
    if re.match(URL_REGEXP, input_str) is None:
        return ""
    return input_str


def safe_mac_address(input_str):
    """Safe MAC address"""
    if not isinstance(input_str, str) or input_str.strip() == "":
        return ""
    input_str = input_str.strip()
    if re.match(MAC_ADDRESS_REGEXP, input_str) is None:
        return ""
    en_mayusculas = input_str.upper()
    m = re.sub(r"[^0-9A-F]+", "", en_mayusculas)
    return f"{m[0:2]}:{m[2:4]}:{m[4:6]}:{m[6:8]}:{m[8:10]}:{m[10:12]}"

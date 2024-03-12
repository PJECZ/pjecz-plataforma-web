"""
Generador de contraseñas
"""
import os

import random
import string

from dotenv import load_dotenv
from hashids import Hashids

load_dotenv()  # Take environment variables from .env

SALT = os.environ.get("SALT", "Esta es una muy mala cadena aleatoria")


def generar_api_key(id: int, email: str, random_length: int = 24) -> str:
    """Generar API key a partir de un ID, un e-mail y una cadena aleatoria"""
    aleatorio = "".join(random.sample(string.ascii_letters + string.digits, k=random_length))
    hash_email = Hashids(salt=email, min_length=8).encode(1)
    hash_id = Hashids(salt=SALT, min_length=8).encode(id)
    return f"{hash_id}.{hash_email}.{aleatorio}"


def generar_contrasena(largo=16):
    """Generar contraseña con minúsculas, mayúculas, dígitos y signos"""
    minusculas = string.ascii_lowercase
    mayusculas = string.ascii_uppercase
    digitos = string.digits
    simbolos = string.punctuation
    todos = minusculas + mayusculas + digitos + simbolos
    temp = random.sample(todos, largo)
    return "".join(temp)


def generar_aleatorio(largo=16):
    """Generar cadena de texto aleatorio con minúsculas, mayúculas y dígitos"""
    minusculas = string.ascii_lowercase
    mayusculas = string.ascii_uppercase
    digitos = string.digits
    todos = minusculas + mayusculas + digitos
    temp = random.sample(todos, largo)
    return "".join(temp)

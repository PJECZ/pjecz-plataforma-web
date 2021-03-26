"""
Generador de contraseñas
"""
import random
import string


def generar_contrasena(largo=16):
    """ Generar contraseña """
    minusculas = string.ascii_lowercase
    mayusculas = string.ascii_uppercase
    digitos = string.digits
    simbolos = string.punctuation
    todos = minusculas + mayusculas + digitos + simbolos
    temp = random.sample(todos, largo)
    return "".join(temp)

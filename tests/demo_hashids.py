"""
Demo Hashids

Demostracion de las cadenas cifradas
"""
import re
from hashids import Hashids

hashid_regexp = re.compile("[0-9a-zA-Z]{8}")

instancia = Hashids(salt="Esta es mi semilla", min_length=8)
id = instancia.encode(1)
print(id)

muestra = "LISTA"
print(f"Muestra {muestra} tiene {len(muestra)} caracteres")

if re.match(hashid_regexp, muestra) is None:
    print("No pasa la expresión regular")

decifrado = instancia.decode(muestra)
try:
    numero = decifrado[0]
    print(numero)
except IndexError:
    print(f"No es correcto {muestra}")

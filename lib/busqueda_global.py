"""
Función para Búsqueda Global
"""
from flask import request


def post_buscar_to_filtros(campo_defecto="id"):
    """Procesa el post de búsqueda global y lo entrega como un dict de filtros"""
    campo = ""
    valor = ""
    filtros = {}

    if "texto_buscar" in request.form:
        texto_buscar = request.form["texto_buscar"]
        params = texto_buscar
        if " " in params:
            params = params.split(" ")
            if len(params) > 1:
                campo = params[1]
            if len(params) > 2:
                valor = " ".join(params[2:])

        if campo != "":
            # Si solo hay dos argumentos, dejamos el campo como el valor, y el campo como campo por defecto.
            if valor == "":
                if campo != "":
                    valor = campo
                    campo = campo_defecto

        filtros = {campo: valor}
    return filtros

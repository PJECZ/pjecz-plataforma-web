"""
Script de Migración de la BD de SIBED que está en MySQL a POSTGRESQL
Debe normalizar y filtrar los datos, dejando solo los registros considerados útiles.

    Fecha de Creación: 2023-03-10
    Autor: ricval
"""
import argparse
import logging
import os
import csv
from dotenv import load_dotenv
from sqlalchemy import text, create_engine
from lib.safe_string import safe_string, safe_message
from pathlib import Path

from plataforma_web.app import create_app
from plataforma_web.extensions import db

from SIBED_Documento_Model import SIBED_Documento

SIBED_JUZGADOS_CSV = "seed/SIBED_juzgados.csv"
SIBED_CONFIG_ENV = "seed/sibed.env"


def main():
    """Main function"""

    # Inicializar
    load_dotenv()  # Take environment variables from .env
    app = create_app()
    db.app = app

    # Manejo de un Log
    bitacora = logging.getLogger("migracion_sibed")
    bitacora.setLevel(logging.INFO)
    formato = logging.Formatter("%(asctime)s:%(levelname)s:%(message)s")
    empunadura = logging.FileHandler("migracion_sibed.log")
    empunadura.setFormatter(formato)
    bitacora.addHandler(empunadura)

    # -- Crear conexión a la BD SIBED que está en MySQL
    ruta = Path(SIBED_CONFIG_ENV)
    if not ruta.exists():
        print(f"AVISO: {ruta.name} no se encontró.")
        return
    if not ruta.is_file():
        print(f"AVISO: {ruta.name} no es un archivo.")
        return
    load_dotenv(ruta)  # Se necesita un archivo .env local para cargar la variable de conexión a la BD
    ENGINE_SIBED = os.getenv("ENGINE_SIBED", "")  # Ruta de conexión de la BD.
    engine = create_engine(ENGINE_SIBED)

    # Leer los juzgados de empate
    juzgados = {}
    ruta = Path(SIBED_JUZGADOS_CSV)
    if not ruta.exists():
        print(f"AVISO: {ruta.name} no se encontró.")
        return
    if not ruta.is_file():
        print(f"AVISO: {ruta.name} no es un archivo.")
        return
    with open(ruta, encoding="utf-8") as puntero:
        rows = csv.DictReader(puntero)
        for row in rows:
            juzgado_id_sibed = int(row["juzgado_id_sibed"])
            juzgado_id_plataforma_web = row["juzgado_id_plataforma_web"]
            if juzgado_id_plataforma_web.isnumeric() and int(juzgado_id_plataforma_web) > 0:
                if juzgado_id_sibed in juzgados:
                    print(f"ERROR: Juzgado con valor repetido en archivo {JUZGADOS_SIBED_CSV}")
                    exit
                juzgados[int(juzgado_id_sibed)] = int(juzgado_id_plataforma_web)
    bitacora.info(f"Juzgados cargados: {len(juzgados)}")

    # Simulación o Ejecución
    simulacion = True
    parser = argparse.ArgumentParser()
    parser.add_argument("-x", "--exec", help="Migrar tabla de la BD MySQL a PostgreSQL", action="store_true")
    args = parser.parse_args()
    if args.exec:
        simulacion = False

    # -- Migración de las Tablas --
    with engine.connect() as connection:
        num_registros_total = 0
        result = connection.execute(text("SELECT COUNT(*) AS total FROM expediente"))
        for row in result:
            num_registros_total = int(row["total"])
        # leer los registros de la BD v1 de usuarios
        result = connection.execute(
            text(
                "SELECT id, juzgadoId, numero_expediente, anno, upper(jucio) as juicio, \
                    upper(actor) as actor, upper(demandado) as demandado, observaciones, \
                    numero_fojas, type\
            FROM expediente \
            ORDER BY id"
            )
        )
        count_insert = 0
        # Posibles errores
        count_error = {
            "documento_repetido": 0,
            "juzgado_invalido": 0,
            "numero_expediente_invalido": 0,
            "juicio_nombre_invalido": 0,
            "actor_nombre_invalido": 0,
            "anio_invalido": 0,
        }

        # --- Comienzo de las validaciones ---
        for row in result:
            # Validar valor del juzgado
            if row["juzgadoId"] == "" or row["juzgadoId"] is None or row["juzgadoId"] not in juzgados:
                bitacora.info("Valor de JUZGADO inválido [ID:%d]", {row["id"]})
                count_error["juzgado_invalido"] += 1
                continue
            # Validar valor del número de expediente
            if row["numero_expediente"] <= 0:
                bitacora.info("NÚMERO DE EXPEDIENTE inválido [ID:%d]", {row["id"]})
                count_error["numero_expediente_invalido"] += 1
                continue
            # Validar nombre del juicio
            if safe_string(row["juicio"]) == "":
                bitacora.info("Nombre de JUICIO inválido [ID:%d]", {row["id"]})
                count_error["juicio_nombre_invalido"] += 1
                continue
            # Validar nombre del actor
            if safe_string(row["actor"]) == "":
                bitacora.info("Nombre del ACTOR inválido [ID:%d]", {row["id"]})
                count_error["actor_nombre_invalido"] += 1
                continue
            # Validar año
            if not row["anno"].isnumeric() or int(row["anno"]) <= 0 or int(row["anno"]) > 2023:
                bitacora.info("AÑO inválido [ID:%d]", {row["id"]})
                count_error["anio_invalido"] += 1
                continue
            # Correcciones en el año
            anio = int(row["anno"])
            if 23 > anio < 99:
                anio = 1900 + anio
            else:
                bitacora.info("AÑO inválido [ID:%d]", {row["id"]})
                count_error["anio_invalido"] += 1
                continue
            # --- Fin de las validaciones ---

            # Ajustar el número de fojas
            fojas = None
            if row["numero_fojas"].isnumeric() and int(row["numero_fojas"]) > 0:
                fojas = int(row["numero_fojas"])
            # Ajustar el tipo
            tipo = safe_string(row["type"])
            if tipo not in SIBED_Documento.TIPOS:
                tipo = SIBED_Documento.TIPOS["NO DEFINIDO"]

            # Insertar registro
            count_insert += 1
            if simulacion is False:
                SIBED_Documento(
                    expediente=f"{row['numero_expediente']}/{anio}",
                    anio=anio,
                    juzgado_id=juzgados[row["juzgadoId"]],
                    juicio=safe_string(row["juicio"]),
                    actor=safe_string(row["actor"]),
                    demandado=safe_string(row["demandado"]),
                    fojas=fojas,
                    tipo=tipo,
                    observaciones=safe_message(row["observaciones"], 255, None),
                ).save()

            # imprimir el progreso
            avance = num_registros_total - count_insert
            if avance % 500 == 0:
                print(f"Avance {count_insert} de {num_registros_total}")

        # Da el total de errores encontrados
        sum_errors = 0
        for _, value in count_error.items():
            sum_errors += value
        bitacora.info(f"Total de registros insertados {count_insert} de {num_registros_total}, omitidos {sum_errors}:{count_error}")
        if sum_errors == 0:
            bitacora.info("¡¡¡Sin Errores!!!")
        else:
            bitacora.info(f"Total de errores: {sum_errors}")


if __name__ == "__main__":
    main()

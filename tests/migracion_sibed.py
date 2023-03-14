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
    juzgados_id = {}
    juzgados_origen_id = {}
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
                if juzgado_id_sibed in juzgados_id:
                    print(f"ERROR: Juzgado con valor repetido en archivo {JUZGADOS_SIBED_CSV}")
                    exit
                juzgados_id[juzgado_id_sibed] = int(juzgado_id_plataforma_web)
                if row["juzgado_origen_id"] == 0:
                    juzgados_origen_id[juzgado_id_sibed] = None
                else:
                    juzgados_origen_id[juzgado_id_sibed] = int(row["juzgado_origen_id"])
    print(f"Juzgados cargados: {len(juzgados_id)}")
    bitacora.info(f"Juzgados cargados: {len(juzgados_id)}")

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
            "expediente_repetido": 0,
        }

        # --- Comienzo de las validaciones ---
        for row in result:
            # Validar valor del juzgado
            if row["juzgadoId"] == "" or row["juzgadoId"] is None or row["juzgadoId"] not in juzgados_id:
                bitacora.info("Valor de JUZGADO inválido [ID:%d]", row["id"])
                count_error["juzgado_invalido"] += 1
                continue
            # Validar valor del número de expediente
            if row["numero_expediente"] != "" and row["numero_expediente"] is not None:
                try:
                    num_expediente = int(row["numero_expediente"])
                    if num_expediente <= 0:
                        bitacora.info("NÚMERO DE EXPEDIENTE inválido [ID:%d]", row["id"])
                        count_error["numero_expediente_invalido"] += 1
                        continue
                except ValueError:
                    bitacora.info("NÚMERO DE EXPEDIENTE inválido [ID:%d]", row["id"])
                    count_error["numero_expediente_invalido"] += 1
                    continue
            else:
                bitacora.info(f"NÚMERO DE EXPEDIENTE vacío")
                count_error["numero_expediente_invalido"] += 1
                continue
            # Validar nombre del juicio
            if safe_string(row["juicio"]) == "":
                bitacora.info("Nombre de JUICIO inválido [ID:%d]", row["id"])
                count_error["juicio_nombre_invalido"] += 1
                continue
            # Validar nombre del actor
            if safe_string(row["actor"]) == "":
                bitacora.info("Nombre del ACTOR inválido [ID:%d]", row["id"])
                count_error["actor_nombre_invalido"] += 1
                continue
            # Validar año
            try:
                anio = int(row["anno"])
                if 0 <= anio > 2023:
                    bitacora.info("AÑO inválido [ID:%d] = %d", row["id"], anio)
                    count_error["anio_invalido"] += 1
                    continue
            except ValueError:
                bitacora.info("AÑO inválido [ID:%d]", row["id"])
                count_error["anio_invalido"] += 1
                continue
            # Correcciones en el año
            anio = int(row["anno"])
            if 23 > anio < 99:
                anio = 1900 + anio
            elif 99 > anio < 1900:
                bitacora.info("AÑO inválido [ID:%d] = %d", row["id"], anio)
                count_error["anio_invalido"] += 1
                continue
            # Correcciones de juzgado
            juzgado_id = juzgados_id[int(row["juzgadoId"])]
            if juzgado_id == 67 or juzgado_id == 68:
                if int(row["numero_expediente"]) % 2 == 0:
                    juzgado_id = 359
                else:
                    juzgado_id = 38
            # --- Fin de las validaciones ---

            # Ajustar el número de fojas
            fojas = None
            if row["numero_fojas"] != "" and row["numero_fojas"] is not None:
                try:
                    fojas = int(row["numero_fojas"])
                    if fojas <= 0:
                        fojas = None
                except ValueError:
                    fojas = None
            # Ajustar el tipo
            tipo = safe_string(row["type"])
            if tipo not in SIBED_Documento.TIPOS:
                tipo = "NO DEFINIDO"

            # Validar que no haya un expediente con el mismo juzgado ingresado
            num_expediente = f"{row['numero_expediente']}/{anio}"
            consulta = SIBED_Documento.query.filter_by(expediente=num_expediente).filter_by(juzgado_id=juzgado_id).first()
            if consulta:
                bitacora.info("Expediente ya cargado")
                count_error["expediente_repetido"] += 1
                continue

            # Insertar registro
            count_insert += 1
            if simulacion is False:
                SIBED_Documento(
                    expediente=num_expediente,
                    anio=anio,
                    juzgado_id=juzgado_id,
                    juzgado_origen_id=juzgados_origen_id[row["juzgadoId"]],
                    juicio=safe_string(row["juicio"]),
                    actor=safe_string(row["actor"]),
                    demandado=safe_string(row["demandado"]),
                    fojas=fojas,
                    tipo=tipo,
                    observaciones=safe_message(row["observaciones"], 255, None),
                ).save()

            # imprimir el progreso
            avance = num_registros_total - count_insert
            porcentaje = (count_insert * 100) / num_registros_total
            if avance % 1000 == 0:
                print(f"Avance {porcentaje:.2f}% : {count_insert} de {num_registros_total}")
                print(row)

        # Da el total de errores encontrados
        sum_errors = 0
        for _, value in count_error.items():
            sum_errors += value
        bitacora.info(f"Total de registros insertados {count_insert} de {num_registros_total}, omitidos {sum_errors}:{count_error}")
        print(f"Total de registros insertados {count_insert} de {num_registros_total}")
        if sum_errors == 0:
            bitacora.info("¡¡¡Sin Errores!!!")
            print("¡¡¡Sin Errores!!!")
        else:
            bitacora.info(f"Total de errores: {sum_errors}")
            print(f"Total de errores: {sum_errors}")


if __name__ == "__main__":
    main()

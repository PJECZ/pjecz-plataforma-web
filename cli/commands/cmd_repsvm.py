"""
REPSVM

- alimentar: Alimentar desde un archivo CSV
- respaldar: Respaldar los agresores a un archivo CSV
"""
import csv
from pathlib import Path

import click
from lib.safe_string import safe_clave, safe_expediente, safe_string, safe_text, safe_url

from plataforma_web.app import create_app
from plataforma_web.extensions import db

from plataforma_web.blueprints.distritos.models import Distrito
from plataforma_web.blueprints.repsvm_agresores.models import REPSVMAgresor

app = create_app()
db.app = app

TIPOS_JUZGADOS_CLAVES = {
    "ND": "NO DEFINIDO",
    "J-EVF": "JUZGADO ESPECIALIZADO EN VIOLENCIA FAMILIAR",
    "J-PEN": "JUZGADO DE PRIMERA INSTANCIA EN MATERIA PENAL",
}


@click.group()
def cli():
    """REPSVM"""


@click.command()
@click.argument("entrada_csv")
def alimentar(entrada_csv):
    """Alimentar desde un archivo CSV"""

    # Validar que el archivo CSV exista
    ruta = Path(entrada_csv)
    if not ruta.exists():
        click.echo(f"AVISO: {ruta.name} no se encontró.")
        return
    if not ruta.is_file():
        click.echo(f"AVISO: {ruta.name} no es un archivo.")
        return

    # Consultar el distrito NO DEFINIDO
    distrito_no_definido = Distrito.query.filter_by(nombre="NO DEFINIDO").first()
    if distrito_no_definido is None:
        click.echo("AVISO: No se encontró el distrito NO DEFINIDO.")
        return

    # Contar los agresores de cada distrito para iniciar el consecutivo de cada uno
    distritos_consecutivos = {}
    for distrito in Distrito.query.filter_by(estatus="A").all():
        distritos_consecutivos[distrito.id] = REPSVMAgresor.query.filter_by(distrito_id=distrito.id).count()

    # Bucle para leer el archivo CSV
    click.echo("Alimentando agresores...")
    contador = 0
    distrito = None
    with open(ruta, encoding="utf8") as puntero:
        rows = csv.DictReader(puntero)
        for row in rows:

            # Tomar el tipo de juzgado
            tipo_juzgado = "ND"
            if "tipo_juzgado_clave" in row:
                tipo_juzgado_clave = safe_clave(row["tipo_juzgado_clave"])
                if tipo_juzgado_clave not in TIPOS_JUZGADOS_CLAVES:
                    click.echo(f"AVISO: {tipo_juzgado_clave} no es un tipo de juzgado válido.")
                    continue
                tipo_juzgado = TIPOS_JUZGADOS_CLAVES[tipo_juzgado_clave]
            elif "tipo_juzgado" in row:
                tipo_juzgado = safe_string(row["tipo_juzgado"])
                if tipo_juzgado not in REPSVMAgresor.TIPOS_JUZGADOS:
                    click.echo(f"! SE OMITE porque no es valido el tipo de juzgado {tipo_juzgado}")
                    continue

            # Tomar el tipo de sentencia
            tipo_sentencia = "ND"
            if "tipo_sentencia" in row:
                tipo_sentencia = safe_string(row["tipo_sentencia"])
                if tipo_sentencia not in REPSVMAgresor.TIPOS_SENTENCIAS:
                    click.echo(f"! SE OMITE porque no es valido el tipo de sentencia {tipo_sentencia}")
                    continue

            # Consultar el distrito
            distrito = distrito_no_definido
            if "distrito_id" in row:
                distrito = Distrito.query.get(int(row["distrito_id"]))
                if distrito is None:
                    click.echo(f"AVISO: No se encontró el distrito {row['distrito_id']}.")
                    continue

            # Incrementar el consecutivo
            if distrito.id not in distritos_consecutivos:
                click.echo(f"! SE OMITE porque no existe el ID distrito {distrito.id}")
                continue
            distritos_consecutivos[distrito.id] += 1

            # Determinar si es publico o no
            es_publico = False
            if "es_publico" in row:
                es_publico = row["es_publico"].strip().lower() == "si"

            # Insertar agresor
            REPSVMAgresor(
                distrito=distrito,
                consecutivo=distritos_consecutivos[distrito.id],
                delito_generico=safe_string(row["delito_generico"], save_enie=True),
                delito_especifico=safe_string(row["delito_especifico"], save_enie=True),
                es_publico=es_publico,
                nombre=safe_string(row["nombre"], save_enie=True),
                numero_causa=safe_string(row["numero_causa"]),
                pena_impuesta=safe_string(row["pena_impuesta"], save_enie=True),
                observaciones=safe_text(row["observaciones"]),
                sentencia_url=safe_url(row["sentencia_url"]),
                tipo_juzgado=tipo_juzgado,
                tipo_sentencia=tipo_sentencia,
            ).save()

            # Incrementar contador
            contador += 1
            if contador % 100 == 0:
                click.echo(f"  Van {contador}...")

    click.echo(f"{contador} alimentados.")


@click.command()
@click.option("--distrito_id", default=None, type=int, help="ID del Distrito")
@click.option("--output", default="repsvm.csv", type=str, help="Archivo CSV a escribir")
def respaldar(distrito_id, output):
    """Respaldar los agresores a un archivo CSV"""
    ruta = Path(output)
    if ruta.exists():
        click.echo(f"AVISO: {ruta.name} existe, no voy a sobreescribirlo.")
        return
    contador = 0
    agresores = REPSVMAgresor.query.filter_by(estatus="A")
    if distrito_id is not None:
        agresores = agresores.filter(REPSVMAgresor.distrito_id == distrito_id)
        click.echo(f"Respaldando los agresores de REPSVM del distrito ID {distrito_id}...")
    else:
        click.echo("Respaldando TODOS los agresores de REPSVM...")
    agresores = agresores.order_by(REPSVMAgresor.distrito_id, REPSVMAgresor.consecutivo).all()
    with open(ruta, "w", encoding="utf8") as puntero:
        respaldo = csv.writer(puntero)
        encabezados = [
            "id",
            "distrito_id",
            "distrito_nombre_corto",
            "consecutivo",
            "materia_nombre",
            "tipo_juzgado_clave",
            "tipo_sentencia",
            "delito_generico",
            "delito_especifico",
            "nombre",
            "numero_causa",
            "pena_impuesta",
            "observaciones",
            "sentencia_url",
        ]
        respaldo.writerow(encabezados)
        for agresor in agresores:
            fila = [
                agresor.id,
                agresor.distrito_id,
                agresor.distrito.nombre_corto,
                agresor.consecutivo,
                agresor.materia_tipo_juzgado.materia.nombre,
                agresor.materia_tipo_juzgado.clave,
                agresor.repsvm_tipo_sentencia.nombre,
                agresor.repsvm_delito_especifico.repsvm_delito_generico.nombre,
                agresor.repsvm_delito_especifico.descripcion,
                agresor.nombre,
                agresor.numero_causa,
                agresor.pena_impuesta,
                agresor.observaciones,
                agresor.sentencia_url,
            ]
            respaldo.writerow(fila)
            contador += 1
            if contador % 100 == 0:
                click.echo(f"  Van {contador}...")
    click.echo(f"Respaldados {contador} agresores en {ruta.name}")


cli.add_command(alimentar)
cli.add_command(respaldar)

"""
REDAM (Registro Estatal de Deudores Alimentarios)

- alimentar: Alimentar desde un archivo CSV
- respaldar: Respaldar a un archivo CSV
- subir_descargable: Subir archivo CSV a Google Storage para descargar como datos abiertos
"""
import csv
from datetime import datetime
from pathlib import Path
import os

import click
from dotenv import load_dotenv
from google.cloud import storage

from lib.safe_string import safe_expediente, safe_string

from plataforma_web.app import create_app
from plataforma_web.extensions import db

from plataforma_web.blueprints.autoridades.models import Autoridad
from plataforma_web.blueprints.redams.models import Redam

app = create_app()
db.app = app

load_dotenv()  # Take environment variables from .env

SUBDIRECTORIO = "REDAM"


@click.group()
def cli():
    """REDAM"""


@click.command()
@click.argument("entrada_csv")
def alimentar(entrada_csv):
    """Alimentar a partir de un archivo CSV"""

    # Validar que el archivo CSV exista
    ruta = Path(entrada_csv)
    if not ruta.exists():
        click.echo(f"AVISO: {ruta.name} no se encontró.")
        return
    if not ruta.is_file():
        click.echo(f"AVISO: {ruta.name} no es un archivo.")
        return

    # Consultar la Autoridad "ND" (No definida)
    autoridad_no_definida = Autoridad.query.filter_by(clave="ND").first()
    if autoridad_no_definida is None:
        click.echo("AVISO: No hay autoridad con clave ND.")
        return

    # Bucle para leer el archivo CSV
    click.echo("Alimentando deudores alimentarios...")
    contador = 0
    with open(ruta, encoding="utf8") as puntero:
        rows = csv.DictReader(puntero)
        for row in rows:
            # Tomar la clave de autoridad
            if "autoridad_clave" in row:
                autoridad_clave = row["autoridad_clave"]
                autoridad = Autoridad.query.filter_by(clave=autoridad_clave).first()
                if autoridad is None:
                    autoridad = autoridad_no_definida
                    click.echo(f"No existe la clave de autoridad {autoridad_clave}")

            # Tomar el nombre
            nombre = safe_string(row["nombre"])
            if nombre == "":
                continue

            # Tomar el expediente
            try:
                expediente = safe_expediente(row["expediente"])
            except (IndexError, ValueError):
                click.echo(f"No es correcto el expediente {row['expediente']}")
                continue

            # Tomar la fecha
            try:
                fecha = datetime.strptime(row["fecha"], "%Y-%m-%d")
            except (ValueError, TypeError):
                click.echo(f"No es correcta la fecha {row['fecha']}")
                continue

            # Insertar el registro
            Redam(
                autoridad=autoridad,
                nombre=nombre,
                expediente=expediente,
                fecha=fecha,
                observaciones=safe_string(row["observaciones"], max_len=1024),
                estatus=row["estatus"],
            ).save()

            # Incrementar el contador
            contador += 1
            if contador % 100 == 0:
                click.echo(f"  Van {contador}...")

    click.echo(f"{contador} deudores alimentarios.")


@click.command()
@click.option("--output", default="redam.csv", type=str, help="Archivo CSV a escribir")
def respaldar(output):
    """Respaldar a un archivo CSV"""
    contador = 0

    # Verificar que el archivo no exista
    ruta = Path(output)
    if ruta.exists():
        click.echo(f"AVISO: {ruta.name} existe, no voy a sobreescribirlo.")
        return

    # Consultar y ordenar por ID
    deudores = Redam.query.order_by(Redam.id).all()

    # Escribir el archivo CSV
    with open(ruta, "w", encoding="utf8") as puntero:
        respaldo = csv.writer(puntero)
        encabezados = [
            "id",
            "autoridad_id",
            "autoridad_clave",
            "nombre",
            "expediente",
            "fecha",
            "observaciones",
            "estatus",
        ]
        respaldo.writerow(encabezados)
        for deudor in deudores:
            fila = [
                deudor.id,
                deudor.autoridad_id,
                deudor.autoridad.clave,
                deudor.nombre,
                deudor.expediente,
                deudor.fecha,
                deudor.observaciones,
                deudor.estatus,
            ]
            respaldo.writerow(fila)
            contador += 1
            if contador % 100 == 0:
                click.echo(f"  Van {contador}...")
    click.echo(f"Respaldados {contador} deudores en {ruta.name}")


@click.command()
@click.option("--output", default="redams.csv", type=str, help="Archivo CSV a escribir")
def subir_descargable(output):
    """Subir archivo CSV a Google Storage para descargar como datos abiertos"""
    contador = 0
    ruta = Path(output)

    # Si el archivo existe, lo borramos
    if ruta.exists():
        ruta.unlink()

    # Consultar los deudores con estatus "A"
    deudores = Redam.query.filter_by(estatus="A").order_by(Redam.id).all()

    # Escribir el archivo CSV
    with open(ruta, "w", encoding="utf8") as puntero:
        descargable = csv.writer(puntero)
        encabezados = [
            "numero",
            "distrito_nombre_corto",
            "autoridad_descripcion_corta",
            "nombre",
            "expediente",
            "fecha",
        ]
        descargable.writerow(encabezados)
        for deudor in deudores:
            contador += 1
            fila = [
                contador,
                deudor.autoridad.distrito.nombre_corto,
                deudor.autoridad.descripcion_corta,
                deudor.nombre,
                deudor.expediente,
                deudor.fecha,
            ]
            descargable.writerow(fila)
            if contador % 100 == 0:
                click.echo(f"  Van {contador}...")
    click.echo(f"Descargables {contador} deudores en {ruta.name}")

    # Subir el archivo a Google Storage
    cloud_storage_bucket = os.getenv("CLOUD_STORAGE_DEPOSITO", None)
    if cloud_storage_bucket is not None:
        storage_client = storage.Client()
        bucket = storage_client.bucket(cloud_storage_bucket)
        blob = bucket.blob(f"{SUBDIRECTORIO}/{ruta.name}")
        blob.upload_from_filename(ruta, content_type="text/csv")
        url = blob.public_url
        click.echo(f"Archivo subido a {url}")


cli.add_command(alimentar)
cli.add_command(respaldar)
cli.add_command(subir_descargable)

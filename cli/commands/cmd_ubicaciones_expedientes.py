"""
Ubicación Expedientes

- alimentar: Alimentar desde un archivo CSV con el nombre de la clave de la autoridad
- respaldar: Respaldar a un archivo CSV
"""
import re
from datetime import date
from pathlib import Path
import csv
import click

from plataforma_web.app import create_app
from plataforma_web.extensions import db

from plataforma_web.blueprints.autoridades.models import Autoridad
from plataforma_web.blueprints.ubicaciones_expedientes.models import UbicacionExpediente

app = create_app()
db.app = app


@click.group()
def cli():
    """Ubicación Expedientes"""


@click.command()
@click.argument("entrada_csv")
def alimentar(entrada_csv):
    """Alimentar desde un archivo CSV con el nombre de la clave de la autoridad"""
    ruta = Path(entrada_csv)
    if not ruta.exists():
        click.echo(f"AVISO: {ruta.name} no se encontró.")
        return
    if not ruta.is_file():
        click.echo(f"AVISO: {ruta.name} no es un archivo.")
        return
    clave = ruta.name[: -len(ruta.suffix)]
    autoridad = Autoridad.query.filter(Autoridad.clave == clave).first()
    if autoridad is None:
        click.echo(f"AVISO: Con el nombre del archivo {ruta.name} no hay clave en autoridades.")
        return
    click.echo("Alimentando ubicaciones de expedientes...")
    contador = 0
    with open(ruta, encoding="utf8") as puntero:
        rows = csv.DictReader(puntero)
        for row in rows:
            # Validar ubicación
            ubicacion = row["ubicacion"].strip()
            if not ubicacion in UbicacionExpediente.UBICACIONES.keys():
                click.echo("! Ubicación no válida")
                continue
            # Validar expediente
            try:
                if not row["expediente"] or row["expediente"].strip() == "":
                    click.echo("! Expediente vacio ")
                    continue
                elementos = re.sub(r"[^0-9]+", "-", row["expediente"]).split("-")
                complemento = (row["expediente"]).split(elementos[0] + "/" + elementos[1])
                try:
                    numero = int(elementos[0])
                    ano = int(elementos[1])
                    texto = str(complemento[1])
                except (IndexError, ValueError) as error:
                    click.echo(error)
                    raise error
                if numero < 0:
                    raise ValueError
                if ano < 1950 or ano > date.today().year:
                    raise ValueError
                expediente = f"{str(numero)}/{str(ano)}{str(texto)}"
            except (IndexError, ValueError):
                click.echo("! Expediente no válido " + row["expediente"].strip())
                continue
            # Insertar
            datos = {
                "autoridad": autoridad,
                "expediente": expediente,
                "ubicacion": ubicacion,
            }
            UbicacionExpediente(**datos).save()
            contador += 1
            if contador % 100 == 0:
                click.echo(f"  Van {contador}...")
    click.echo(f"{contador} ubicaciones de expedientes alimentadas.")


@click.command()
@click.option("--autoridad-id", default=None, type=int, help="ID de la autoridad")
@click.option("--autoridad-clave", default="", type=str, help="Clave de la autoridad")
@click.option("--output", default="ubicaciones_expedientes.csv", type=str, help="Archivo CSV a escribir")
def respaldar(autoridad_id, autoridad_clave, output):
    """Respaldar a un archivo CSV"""
    ruta = Path(output)
    if ruta.exists():
        click.echo(f"AVISO: {ruta.name} existe, no voy a sobreescribirlo.")
        return
    if autoridad_id:
        autoridad = Autoridad.query.get(autoridad_id)
    elif autoridad_clave:
        autoridad = Autoridad.query.filter_by(clave=autoridad_clave).first()
    else:
        autoridad = None
    if autoridad is not None and autoridad.es_jurisdiccional is False:
        click.echo("AVISO: La autoridad no es jurisdiccional")
        return
    click.echo("Respaldando ubicaciones de expedientes...")
    contador = 0
    ubicaciones_expedientes = UbicacionExpediente.query.filter_by(estatus="A")
    if autoridad is not None:
        ubicaciones_expedientes = ubicaciones_expedientes.filter(UbicacionExpediente.autoridad == autoridad)
    ubicaciones_expedientes = ubicaciones_expedientes.all()
    with open(ruta, "w", encoding="utf8") as puntero:
        respaldo = csv.writer(puntero)
        respaldo.writerow(["autoridad_clave", "expediente", "ubicacion"])
        for ubicacion_expediente in ubicaciones_expedientes:
            respaldo.writerow(
                [
                    ubicacion_expediente.autoridad.clave,
                    ubicacion_expediente.expediente,
                    ubicacion_expediente.ubicacion,
                ]
            )
            contador += 1
            if contador % 100 == 0:
                click.echo(f"  Van {contador}...")
    click.echo(f"Respaldados {contador} en {ruta.name}")


cli.add_command(alimentar)
cli.add_command(respaldar)

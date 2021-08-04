"""
Ubicación de Expedientes

- alimentar: Alimentar insertando registros desde un archivo CSV
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

from lib.safe_string import safe_expediente

app = create_app()
db.app = app


@click.group()
def cli():
    """Ubicación de Expedientes"""


@click.command()
@click.argument("entrada_csv")
def alimentar(entrada_csv):
    """Alimentar insertando registros desde un archivo CSV"""
    ruta = Path(entrada_csv)
    if not ruta.exists():
        click.echo(f"AVISO: {ruta.name} no se encontró.")
        return
    if not ruta.is_file():
        click.echo(f"AVISO: {ruta.name} no es un archivo.")
        return
    click.echo("Alimentando ubicaciones de expedientes...")
    contador = 0
    with open(ruta, encoding="utf8") as puntero:
        rows = csv.DictReader(puntero)
        for row in rows:

            # Validar autoridad
            autoridad_str = row["autoridad_id"].strip()
            if autoridad_str == "":
                click.echo("! Sin autoridad")
                continue
            try:
                autoridad_id = int(autoridad_str)
            except ValueError:
                click.echo("! El ID de la autoridad no es un entero")
                continue
            autoridad = Autoridad.query.get(autoridad_id)
            if autoridad is False:
                click.echo("! No existe la autoridad")
                continue
            if autoridad.es_jurisdiccional is False:
                click.echo("! La autoridad no es jurisdiccional")
                continue

            # Validar ubicación
            ubicacion = row["ubicacion"].strip()
            if not ubicacion in UbicacionExpediente.UBICACIONES.keys():
                click.echo("! Ubicación no válida")
                continue

            # Validar expediente
            try:
                if not row["expediente"] or row["expediente"].strip() == "":
                    return ""
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
                click.echo(f"  Van {contador} ubicaciones de expedientes...")

    click.echo(f"{contador} ubicaciones de expedientes alimentadas.")


@click.command()
@click.argument("salida_csv")
def respaldar(salida_csv):
    """Respaldar a un archivo CSV"""
    ruta = Path(salida_csv)
    if ruta.exists():
        click.echo(f"AVISO: {ruta.name} existe, no voy a sobreescribirlo.")
        return
    click.echo("Respaldando ubicaciones de expedientes...")
    contador = 0
    ubicaciones_expedientes = UbicacionExpediente.query.filter(UbicacionExpediente.estatus == "A").all()
    with open(ruta, "w") as puntero:
        escritor = csv.writer(puntero)
        escritor.writerow(["autoridad", "expediente", "ubicacion"])
        for ubicacion_expediente in ubicaciones_expedientes:
            escritor.writerow(
                [
                    ubicacion_expediente.autoridad_id,
                    ubicacion_expediente.expediente,
                    ubicacion_expediente.ubicacion,
                ]
            )
            contador += 1
            if contador % 100 == 0:
                click.echo(f"  Van {contador} registros...")
    click.echo(f"Respaldados {contador} registros.")


cli.add_command(alimentar)
cli.add_command(respaldar)

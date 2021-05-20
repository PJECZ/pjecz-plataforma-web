"""
Ubicación de Expedientes

- alimentar: Alimentar insertando registros desde un archivo CSV
- borrar: Borrar todos los registros
- respaldar: Respaldar a un archivo CSV
"""
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
            autoridad_str = row["autoridad"].strip()
            if autoridad_str == "":
                click.echo("  Sin autoridad")
                continue
            try:
                autoridad_id = int(autoridad_str)
            except ValueError:
                click.echo(f"  No es válida la autoridad {autoridad_str}")
                continue
            autoridad = Autoridad.query.get(autoridad_id)
            if autoridad is False:
                click.echo(f"  No es válida la autoridad {autoridad_str}")
                continue
            # Validar ubicación
            ubicacion = row["ubicacion"].strip()
            if not ubicacion in UbicacionExpediente.UBICACIONES.keys():
                click.echo(f"  No es válida la ubicación {ubicacion}")
                continue
            # Validar expediente
            expediente = row["expediente"].strip()
            if expediente == "":
                click.echo("  Sin expediente")
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


@click.command()
def borrar():
    """Borrar todos los registros"""
    click.echo("Borrando las ubicaciones de expedientes en la base de datos...")
    cantidad = db.session.query(UbicacionExpediente).delete()
    db.session.commit()
    click.echo(f"Han sido borrados {cantidad} registros.")


cli.add_command(alimentar)
cli.add_command(respaldar)
cli.add_command(borrar)

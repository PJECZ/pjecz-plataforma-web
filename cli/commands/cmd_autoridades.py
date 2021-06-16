"""
Autoridades

- actualizar_materias: Actualizar columnas materia y organo_jurisdiccional
- alimentar_notarias: Alimentar la tabla autoridades con Notarías

Al momento se requiere ejecutar

    UPDATE autoridades SET organo_jurisdiccional='NO DEFINIDO';

"""
from pathlib import Path
import csv
import click

from plataforma_web.app import create_app
from plataforma_web.extensions import db

from plataforma_web.blueprints.autoridades.models import Autoridad
from plataforma_web.blueprints.distritos.models import Distrito
from plataforma_web.blueprints.materias.models import Materia

app = create_app()
db.app = app


@click.group()
def cli():
    """Autoridades"""


@click.command()
@click.argument("entrada_csv")
def actualizar_materias(entrada_csv):
    """Actualizar columnas materia y organo_jurisdiccional"""
    ruta = Path(entrada_csv)
    if not ruta.exists():
        click.echo(f"AVISO: {ruta.name} no se encontró.")
        return
    if not ruta.is_file():
        click.echo(f"AVISO: {ruta.name} no es un archivo.")
        return
    contador = 0
    click.echo("Actualizando autoridades...")
    with open(ruta, encoding="utf8") as puntero:
        rows = csv.DictReader(puntero)
        for row in rows:
            autoridad = Autoridad.query.filter(Autoridad.clave == row["clave"].strip()).first()
            if autoridad is None:
                click.echo("! No existe la autoridad " + row["clave"])
                continue
            if autoridad.estatus != "A":
                continue
            materia = Materia.query.filter(Materia.nombre == row["materia"].strip()).first()
            if materia is None:
                click.echo("! No existe la materia " + row["materia"])
                continue
            organo_jurisdiccional = row["organo_jurisdiccional"].strip()
            if organo_jurisdiccional not in Autoridad.ORGANOS_JURISDICCIONALES:
                click.echo("! No existe el órgano jurisdiccional " + row["organo_jurisdiccional"])
                continue
            if autoridad.materia != materia or autoridad.organo_jurisdiccional != organo_jurisdiccional:
                autoridad.materia = materia
                autoridad.organo_jurisdiccional = organo_jurisdiccional
                autoridad.save()
                contador += 1
    click.echo(f"{contador} autoridades actualizadas.")


@click.command()
@click.argument("entrada_csv")
def alimentar_notarias(entrada_csv):
    """Alimentar la tabla autoridades con Notarías"""
    ruta = Path(entrada_csv)
    if not ruta.exists():
        click.echo(f"AVISO: {ruta.name} no se encontró.")
        return
    if not ruta.is_file():
        click.echo(f"AVISO: {ruta.name} no es un archivo.")
        return
    click.echo("Alimentando notarías...")
    contador = 0
    with open(ruta, encoding="utf8") as puntero:
        rows = csv.DictReader(puntero)
        for row in rows:
            distrito = Distrito.query.filter(Distrito.nombre == row["distrito"].strip()).first()
            if distrito is None:
                click.echo("  No existe el distrito " + row["distrito"])
                continue
            descripcion = row["autoridad"].strip()
            if descripcion == "":
                click.echo("  Falta una descripción")
                continue
            clave = row["clave"].strip()  # Única
            if Autoridad.query.filter(Autoridad.clave == clave).first() is not None:
                click.echo(f"  Se omite la clave {clave} porque ya está presente")
                continue
            directorio_edictos = row["directorio_edictos"].strip()
            datos = {
                "distrito": distrito,
                "descripcion": descripcion,
                "clave": clave,
                "es_jurisdiccional": True,
                "es_notaria": True,
                "directorio_edictos": directorio_edictos,
            }
            Autoridad(**datos).save()
            contador += 1
            if contador % 100 == 0:
                click.echo(f"  Van {contador} registros...")
    click.echo(f"{contador} notarías alimentadas.")


cli.add_command(actualizar_materias)
cli.add_command(alimentar_notarias)

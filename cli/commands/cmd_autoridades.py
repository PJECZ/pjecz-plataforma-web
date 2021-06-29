"""
Autoridades

- alimentar: Alimentar la tabla insertando registros desde un archivo CSV
- respaldar: Respaldar a un archivo CSV
"""
from pathlib import Path
import csv
import click

from plataforma_web.app import create_app
from plataforma_web.extensions import db

from plataforma_web.blueprints.autoridades.models import Autoridad

app = create_app()
db.app = app


@click.group()
def cli():
    """Autoridades"""


@click.command()
@click.argument("entrada_csv")
def alimentar(entrada_csv):
    """Alimentar la tabla insertando registros desde un archivo CSV"""
    ruta = Path(entrada_csv)
    if not ruta.exists():
        click.echo(f"AVISO: {ruta.name} no se encontró.")
        return
    if not ruta.is_file():
        click.echo(f"AVISO: {ruta.name} no es un archivo.")
        return
    click.echo("Alimentando autoridades...")
    contador = 0
    with open(ruta, encoding="utf8") as puntero:
        rows = csv.DictReader(puntero)
        for row in rows:
            Autoridad(
                distrito_id=int(row["distrito_id"]),
                materia_id=int(row["materia_id"]),
                descripcion=row["descripcion"],
                descripcion_corta=row["descripcion_corta"],
                clave=row["clave"],
                es_jurisdiccional=(row["es_jurisdiccional"] == "1"),
                es_notaria=(row["es_notaria"] == "1"),
                organo_jurisdiccional=row["organo_jurisdiccional"],
                directorio_edictos=row["directorio_edictos"],
                directorio_glosas=row["directorio_glosas"],
                directorio_listas_de_acuerdos=row["directorio_listas_de_acuerdos"],
                directorio_sentencias=row["directorio_sentencias"],
                audiencia_categoria=row["audiencia_categoria"],
            ).save()
            contador += 1
    click.echo(f"{contador} autoridades alimentadas.")


@click.command()
@click.argument("salida_csv")
def respaldar(salida_csv):
    """Respaldar a un archivo CSV"""
    ruta = Path(salida_csv)
    if ruta.exists():
        click.echo(f"AVISO: {ruta.name} existe, no voy a sobreescribirlo.")
        return
    click.echo("Respaldando autoridades...")
    contador = 0
    autoridades = Autoridad.query.order_by(Autoridad.id).all()
    with open(ruta, "w") as puntero:
        escritor = csv.writer(puntero)
        escritor.writerow(
            [
                "id",
                "distrito_id",
                "materia_id",
                "descripcion",
                "descripcion_corta",
                "clave",
                "es_jurisdiccional",
                "es_notaria",
                "organo_jurisdiccional",
                "directorio_edictos",
                "directorio_glosas",
                "directorio_listas_de_acuerdos",
                "directorio_sentencias",
                "audiencia_categoria",
            ]
        )
        for autoridad in autoridades:
            escritor.writerow(
                [
                    autoridad.id,
                    autoridad.distrito_id,
                    autoridad.materia_id,
                    autoridad.descripcion,
                    autoridad.descripcion_corta,
                    autoridad.clave,
                    int(autoridad.es_jurisdiccional),
                    int(autoridad.es_notaria),
                    autoridad.organo_jurisdiccional,
                    autoridad.directorio_edictos,
                    autoridad.directorio_glosas,
                    autoridad.directorio_listas_de_acuerdos,
                    autoridad.directorio_sentencias,
                    autoridad.audiencia_categoria,
                ]
            )
            contador += 1
    click.echo(f"Respaldadas {contador} autoridades.")


cli.add_command(alimentar)
cli.add_command(respaldar)

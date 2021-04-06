"""
Peritos

- alimentar: Alimentar insertando registros desde un archivo CSV
- respaldar: Respaldar a un archivo CSV
"""
from pathlib import Path
import csv
from unidecode import unidecode
import click

from plataforma_web.app import create_app
from plataforma_web.extensions import db

from plataforma_web.blueprints.distritos.models import Distrito
from plataforma_web.blueprints.peritos.models import Perito

app = create_app()
db.app = app


@click.group()
def cli():
    """ Peritos """


@click.command()
@click.argument("entrada_csv")
def alimentar(entrada_csv):
    """ Alimentar insertando registros desde un archivo CSV """
    ruta = Path(entrada_csv)
    if not ruta.exists():
        click.echo(f"AVISO: {ruta.name} no se encontró.")
        return
    if not ruta.is_file():
        click.echo(f"AVISO: {ruta.name} no es un archivo.")
        return
    click.echo("Alimentando peritos...")
    contador = 0
    with open(ruta, encoding="utf8") as puntero:
        rows = csv.DictReader(puntero)
        for row in rows:
            distrito_str = row["distrito"].strip()
            if distrito_str == "":
                click.echo("  Sin distrito...")
                continue
            distrito = Distrito.query.get(int(distrito_str))
            if distrito is False:
                click.echo(f"  No es válido el distrito {row['distrito']}...")
                continue
            tipo = row["tipo"].strip()
            if not tipo in Perito.TIPOS.keys():
                click.echo(f"  No es válida el tipo {tipo}...")
                continue
            datos = {
                "distrito": distrito,
                "tipo": tipo,
                "nombre": unidecode(row["nombre"].strip()).upper(),  # Sin acentos y en mayúsculas
                "domicilio": unidecode(row["domicilio"].strip()).upper(),  # Sin acentos y en mayúsculas
                "telefono_fijo": row["telefono_fijo"].strip(),
                "telefono_celular": row["telefono_celular"].strip(),
                "email": unidecode(row["email"].strip()).lower(),  # Sin acentos y en minúsculas
                "notas": unidecode(row["notas"].strip()).upper(),  # Sin acentos y en mayúsculas
            }
            Perito(**datos).save()
            contador += 1
            if contador % 100 == 0:
                click.echo(f"  Van {contador} peritos...")
    click.echo(f"- {contador} peritos alimentados.")


@click.command()
@click.argument("salida_csv")
def respaldar(salida_csv):
    """ Respaldar a un archivo CSV """
    ruta = Path(salida_csv)
    if ruta.exists():
        click.echo(f"AVISO: {ruta.name} existe, no voy a sobreescribirlo.")
        return
    click.echo("Respaldando peritos...")
    contador = 0
    peritos = Perito.query.filter(Perito.estatus == "A").order_by(Perito.distrito_id, Perito.tipo, Perito.nombre).all()
    with open(ruta, "w") as puntero:
        escritor = csv.writer(puntero)
        escritor.writerow(["distrito", "tipo", "nombre", "domicilio", "telefono_fijo", "telefono_celular", "email", "renovacion", "notas"])
        for perito in peritos:
            escritor.writerow(
                [
                    perito.distrito.nombre,
                    perito.tipo,
                    perito.nombre,
                    perito.domicilio,
                    perito.telefono_fijo,
                    perito.telefono_celular,
                    perito.email,
                    perito.renovacion.strftime("%Y-%m-%d"),
                    perito.notas,
                ]
            )
            contador += 1
            if contador % 100 == 0:
                click.echo(f"  Van {contador} registros...")
    click.echo(f"Respaldados {contador} registros.")


@click.command()
def borrar(salida_csv):
    """ Borrar todos los peritos """
    cantidad = Perito.query().delete()
    click.echo(f"Han sido borrados {str(cantidad)} registros.")


cli.add_command(alimentar)
cli.add_command(respaldar)
cli.add_command(borrar)

"""
Alimentar Peritos
"""
from pathlib import Path
import csv
import click

from plataforma_web.blueprints.peritos.models import Perito
from plataforma_web.blueprints.distritos.models import Distrito

PERITOS_CSV = "seed/peritos.csv"

def alimentar_peritos():
    """ Alimentar Peritos """
    peritos_csv = Path(PERITOS_CSV)
    if not peritos_csv.exists():
        click.echo(f"- NO se alimentaron los peritos porque no se encontró {PERITOS_CSV}")
        return
    contador = 0
    with open(peritos_csv, encoding="utf8") as puntero:
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
                "nombre": row["nombre"].strip(),
                "domicilio": row["domicilio"].strip(),
                "telefono_fijo": row["telefono_fijo"].strip(),
                "telefono_celular": row["telefono_celular"].strip(),
                "email": row["email"].strip(),
                "notas": row["notas"].strip(),
            }
            Perito(**datos).save()
            contador += 1
            if contador % 100 == 0:
                click.echo(f"  Van {contador} peritos...")
    click.echo(f"- {contador} peritos alimentados.")
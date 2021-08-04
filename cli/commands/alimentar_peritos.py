"""
Alimentar Peritos
"""
from datetime import datetime
from pathlib import Path
import csv
import click
from unidecode import unidecode

from plataforma_web.blueprints.peritos.models import Perito
from plataforma_web.blueprints.distritos.models import Distrito

PERITOS_CSV = "seed/peritos.csv"


def alimentar_peritos():
    """ Alimentar Peritos """
    peritos_csv = Path(PERITOS_CSV)
    if not peritos_csv.exists():
        click.echo(f"NO se alimentaron los peritos porque no se encontró {PERITOS_CSV}")
        return
    contador = 0
    with open(peritos_csv, encoding="utf8") as puntero:
        rows = csv.DictReader(puntero)
        for row in rows:
            distrito_str = row["distrito"].strip()
            if distrito_str == "":
                click.echo("  Sin distrito...")
                continue
            distrito = Distrito.query.filter(Distrito.nombre == distrito_str).first()
            if distrito is None:
                click.echo(f"  No es válido el distrito {row['distrito']}...")
                continue
            tipo = row["tipo"].strip()
            if not tipo in Perito.TIPOS.keys():
                click.echo(f"  No es válida el tipo {tipo}...")
                continue
            renovacion_str = row["renovacion"].strip()
            try:
                renovacion = datetime.strptime(renovacion_str, "%Y-%m-%d")  # Probar que toda la fecha sea correcta
            except ValueError as mensaje:
                try:
                    renovacion = datetime.strptime(renovacion_str[0:8] + "-01", "%Y-%m-%d")  # Probar año y mes correctos
                except ValueError as mensaje:
                    try:
                        renovacion = datetime.strptime(renovacion_str[0:4] + "-01-01", "%Y-%m-%d")  # Probar año correcto
                    except ValueError as mensaje:
                        click.echo(f"  Dato con error: {mensaje}")
            datos = {
                "distrito": distrito,
                "tipo": tipo,
                "nombre": unidecode(row["nombre"].strip()).upper(),  # Sin acentos y en mayúsculas
                "domicilio": unidecode(row["domicilio"].strip()).upper(),  # Sin acentos y en mayúsculas
                "telefono_fijo": row["telefono_fijo"].strip(),
                "telefono_celular": row["telefono_celular"].strip(),
                "email": unidecode(row["email"].strip()).lower(),
                "renovacion": renovacion,
                "notas": unidecode(row["notas"].strip()).upper(),
            }
            Perito(**datos).save()
            contador += 1
            if contador % 100 == 0:
                click.echo(f"  Van {contador} peritos...")
    click.echo(f"  {contador} peritos alimentados.")

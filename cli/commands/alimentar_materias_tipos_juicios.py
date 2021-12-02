"""
Alimentar materias tipos juicios
"""
from pathlib import Path
import csv
import click

from lib.safe_string import safe_string

from plataforma_web.blueprints.materias_tipos_juicios.models import MateriaTipoJuicio

MATERIAS_TIPOS_JUICIOS_CSV = "seed/materias_tipos_juicios.csv"


def alimentar_materias_tipos_juicios():
    """Alimentar materias tipos juicios"""
    ruta = Path(MATERIAS_TIPOS_JUICIOS_CSV)
    if not ruta.exists():
        click.echo(f"AVISO: {ruta.name} no se encontró.")
        return
    if not ruta.is_file():
        click.echo(f"AVISO: {ruta.name} no es un archivo.")
        return
    click.echo("Alimentando materias tipos juicios...")
    contador = 0
    with open(ruta, encoding="utf8") as puntero:
        rows = csv.DictReader(puntero)
        for row in rows:
            materia_tipo_juicio_id = int(row["materia_tipo_juicio_id"])
            if materia_tipo_juicio_id != contador + 1:
                click.echo(f"  AVISO: materia_tipo_juicio_id {materia_tipo_juicio_id} no es consecutivo")
                continue
            MateriaTipoJuicio(
                materia_id=int(row["materia_id"]),
                descripcion=safe_string(row["descripcion"]),
                estatus=row["estatus"],
            ).save()
            contador += 1
            if contador % 100 == 0:
                click.echo(f"  Van {contador}...")
    click.echo(f"  {contador} materias tipos juicios alimentados.")

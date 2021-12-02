"""
Alimentar funcionarios
"""
from pathlib import Path
import csv
import click

from plataforma_web.blueprints.funcionarios.models import Funcionario

FUNCIONARIOS_CSV = "seed/funcionarios.csv"


def alimentar_funcionarios():
    """Alimentar funcionarios"""
    ruta = Path(FUNCIONARIOS_CSV)
    if not ruta.exists():
        click.echo(f"AVISO: {ruta.name} no se encontró.")
        return
    if not ruta.is_file():
        click.echo(f"AVISO: {ruta.name} no es un archivo.")
        return
    click.echo("Alimentando funcionarios...")
    contador = 0
    with open(ruta, encoding="utf-8") as puntero:
        rows = csv.DictReader(puntero)
        for row in rows:
            Funcionario(
                nombres=row["nombres"],
                apellido_paterno=row["apellido_paterno"],
                apellido_materno=row["apellido_materno"],
                curp=row["curp"],
                email=row["email"],
                puesto=row["puesto"],
                en_funciones=(int(row["en_funciones"]) == 1),
                estatus=row["estatus"],
            ).save()
            contador += 1
            if contador % 100 == 0:
                click.echo(f"  Van {contador}...")
    click.echo(f"  {contador} funcionarios alimentados")

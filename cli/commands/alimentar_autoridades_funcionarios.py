"""
Alimentar autoridades-funcionarios
"""
from pathlib import Path
import csv
import click

from plataforma_web.blueprints.autoridades.models import Autoridad
from plataforma_web.blueprints.autoridades_funcionarios.models import AutoridadFuncionario
from plataforma_web.blueprints.funcionarios.models import Funcionario

AUTORIDADES_FUNCIONARIOS_CSV = "seed/funcionarios.csv"


def alimentar_autoridades_funcionarios():
    """Alimentar Autoridades-Funcionarios"""
    ruta = Path(AUTORIDADES_FUNCIONARIOS_CSV)
    if not ruta.exists():
        click.echo(f"AVISO: {ruta.name} no se encontró.")
        return
    if not ruta.is_file():
        click.echo(f"AVISO: {ruta.name} no es un archivo.")
        return
    if Funcionario.query.count() == 0:
        click.echo("AVISO: Faltan de alimentar los funcionarios")
        return
    click.echo("Alimentando autoridades-funcionarios...")
    contador = 0
    autoridad = None
    with open(ruta, encoding="utf-8") as puntero:
        rows = csv.DictReader(puntero)
        for row in rows:
            funcionario_id = int(row["funcionario_id"])
            funcionario = Funcionario.query.get(funcionario_id)
            if funcionario is None:
                click.echo(f"  AVISO: No se encontró el funcionario {funcionario_id}.")
                continue
            if row["autoridades_claves"].strip() == "":
                continue
            for autoridad_clave in row["autoridades_claves"].split(","):
                autoridad_clave = autoridad_clave.strip()
                autoridad = Autoridad.query.filter_by(clave=autoridad_clave).first()
                if autoridad is None:
                    click.echo(f"  AVISO: No se encontró la autoridad {autoridad_clave}.")
                    continue
                AutoridadFuncionario(
                    autoridad=autoridad,
                    funcionario=funcionario,
                    descripcion=f"{funcionario.nombre} en {autoridad.clave}",
                ).save()
                contador += 1
                if contador % 100 == 0:
                    click.echo(f"  Van {contador} autoridades-funcionarios...")
    click.echo(f"  {contador} autoridades-funcionarios alimentados")

"""
Ubicación de Expedientes

- alimentar: Alimentar insertando registros desde un archivo CSV
- borrar: Borrar todos los registros
- respaldar: Respaldar a un archivo CSV
"""
import click


@click.group()
def cli():
    """Ubicación de Expedientes"""


@click.command()
@click.argument("entrada_csv")
def alimentar(entrada_csv):
    """Alimentar insertando registros desde un archivo CSV"""


@click.command()
@click.argument("salida_csv")
def respaldar(salida_csv):
    """Respaldar a un archivo CSV"""


@click.command()
def borrar():
    """Borrar todos los registros"""


cli.add_command(alimentar)
cli.add_command(respaldar)
cli.add_command(borrar)

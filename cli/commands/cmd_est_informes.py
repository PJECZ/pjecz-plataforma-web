"""
Estadisticas Informes

- crear-aleatorios: Crear informes aleatorios
- reiniciar: Eliminar todos los informes y registros
"""
from datetime import datetime, timedelta
import random

import click

from plataforma_web.app import create_app
from plataforma_web.extensions import db

from plataforma_web.blueprints.autoridades.models import Autoridad
from plataforma_web.blueprints.est_informes.models import EstInforme
from plataforma_web.blueprints.est_informes_registros.models import EstInformeRegistro
from plataforma_web.blueprints.est_variables.models import EstVariable

app = create_app()
db.app = app


@click.group()
def cli():
    """Estadisticas Variables"""


@click.command()
@click.option("--fecha", default="", type=str, help="Fecha a consultar")
def crear_aleatorios(fecha):
    """Crear informes aleatorios"""

    # Definir la base de datos para agregar los registros por lotes
    database = db.session

    # Consultar las variables con estatus en 'A'
    est_variables = EstVariable.query.filter_by(estatus="A")
    if est_variables.count() == 0:
        click.echo("No hay variables.")
        return
    click.echo(f"Hay {est_variables.count()} variables.")

    # Consultar las autoridades con estatus en 'A'
    autoridades = Autoridad.query.filter_by(estatus="A")
    autoridades = autoridades.filter_by(es_jurisdiccional=True)  # Con es_jurisdiccional en verdadero
    autoridades = autoridades.filter_by(es_notaria=False)  # Con es_notaria en falso
    autoridades = autoridades.filter_by(es_extinto=False)  # Con es_extinto en falso
    autoridades = autoridades.filter_by(organo_jurisdiccional="JUZGADO DE PRIMERA INSTANCIA")  # Juzgados primera instancia
    if autoridades.count() == 0:
        click.echo("No hay autoridades jurisdiccionales.")
        return
    click.echo(f"Hay {autoridades.count()} autoridades jurisdiccionales.")

    # Si viene la fecha, validarla
    # Si no viene la fecha, usar la fecha del dia ultimo del mes pasado
    if fecha != "":
        try:
            fecha = datetime.strptime(fecha, "%Y-%m-%d").date()
        except ValueError as mensaje:
            click.echo(f"AVISO: Fecha incorrecta {mensaje}")
            return
    else:
        fecha = datetime.today().date()
        fecha = fecha.replace(day=1) - timedelta(days=1)
    click.echo(f"Creando informes aleatorios para la fecha {fecha}...")

    # Bucle para cada autoridad
    for autoridad in autoridades.all():
        # Mostrar la clave de la autoridad
        click.echo(f"- {autoridad.clave} ", nl=False)
        # Crear informe
        est_informe = EstInforme(autoridad_id=autoridad.id, fecha=fecha)
        est_informe.save()
        # Bucle para cada variable
        for est_variable in est_variables.all():
            # Definir la cantidad que es un numero aleatorio entre 1 y 20
            cantidad = random.randint(1, 20)
            # Crear registro en el informe
            est_informe_registro = EstInformeRegistro(
                est_informe_id=est_informe.id,
                est_variable_id=est_variable.id,
                cantidad=cantidad,
            )
            # Agregar al lote
            database.add(est_informe_registro)
            click.echo(".", nl=False)
        # Cambiamos el estado del informa a RECIBIDO
        est_informe.estado = "RECIBIDO"
        est_informe.save()
        # Ejecutar el lote
        database.commit()
        click.echo(" OK.")

    # Mensaje de termino
    click.echo("Terminado.")


@click.command()
def reiniciar():
    """Eliminar todos los informes y registros"""

    # Definir la base de datos
    database = db.session

    # Eliminar todos los est_informes_registros
    click.echo("Eliminando todos los registros de informes...")
    EstInformeRegistro.query.delete()
    database.commit()

    # Eliminar todos los est_informes
    click.echo("Eliminando todos los informes...")
    EstInforme.query.delete()
    database.commit()

    # Poner la secuencia de est_informes_registros_id a cero
    click.echo("Poniendo la secuencia de est_informes_registros_id a cero...")
    database.execute("ALTER SEQUENCE est_informes_registros_id_seq RESTART WITH 1;")
    database.commit()

    # Poner la secuencia de est_informes_id a cero
    click.echo("Poniendo la secuencia de est_informes_id a cero...")
    database.execute("ALTER SEQUENCE est_informes_id_seq RESTART WITH 1;")
    database.commit()


cli.add_command(crear_aleatorios)
cli.add_command(reiniciar)

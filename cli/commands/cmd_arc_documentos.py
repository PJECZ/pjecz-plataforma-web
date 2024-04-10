"""
Archivos - Documentos

- copiar_juzgados_origen_claves: Actualizar los juzgados de origen como claves.
"""
import click

from plataforma_web.app import create_app
from plataforma_web.extensions import db

from plataforma_web.blueprints.arc_documentos.models import ArcDocumento
from plataforma_web.blueprints.arc_juzgados_extintos.models import ArcJuzgadoExtinto 

app = create_app()
db.app = app


@click.group()
def cli():
    """Archivos - Documentos"""


@click.command()
def copiar_juzgados_origen_claves():
    """Actualizar los juzgados de origen como claves"""
    click.echo("Actualizar los juzgados de origen como claves")
    database = db.session
    contador = 0
    documentos = ArcDocumento.query.filter_by(estatus="A").filter(ArcDocumento.arc_juzgado_origen != None).all()
    for documento in documentos:
        # Buscar el juzgado extinto
        juzgado_extinto = ArcJuzgadoExtinto.query.filter(ArcJuzgadoExtinto.id == documento.arc_juzgado_origen_id).first()
        if juzgado_extinto:
            documento.arc_juzgados_origen_claves = juzgado_extinto.clave
            database.add(documento)
            # documento.save()
            contador += 1
            click.echo(".", nl=False)
            if contador % 100 == 0:
                database.commit()
                click.echo(f"  Van {contador}...")
    if contador > 0 and contador % 100 != 0:
        database.commit()
    click.echo(f"Actualizados {contador} documentos")


cli.add_command(copiar_juzgados_origen_claves)

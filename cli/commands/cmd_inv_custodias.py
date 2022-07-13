"""
Inventarios Custodias

- actualizar: Actualizar las cantidades de equipos y fotos de las custodias
"""
import click

from plataforma_web.app import create_app
from plataforma_web.extensions import db

from plataforma_web.blueprints.inv_custodias.models import InvCustodia
from plataforma_web.blueprints.inv_equipos.models import InvEquipo
from plataforma_web.blueprints.inv_equipos_fotos.models import InvEquipoFoto

app = create_app()
db.app = app


@click.group()
def cli():
    """Inventarios Custodias"""


@click.command()
def actualizar():
    """Actualizar las cantidades de equipos y fotos de las custodias"""
    contador = 0
    # Recorrer todas las custodias activas
    for inv_custodia in InvCustodia.query.filter_by(estatus="A").all():
        equipos_cantidad = 0
        equipos_fotos_cantidad = 0
        # Recorrer los equipos de cada custodia
        for inv_equipo in InvEquipo.query.filter_by(inv_custodia_id=inv_custodia.id).filter_by(estatus="A").all():
            # Incrementar la cantidad de equipos
            equipos_cantidad += 1
            # Consultar la cantidad de fotos de los equipos
            equipos_fotos_cantidad += InvEquipoFoto.query.filter_by(inv_equipo_id=inv_equipo.id).filter_by(estatus="A").count()
        hay_que_actualizar = False
        # Si es diferente, actualizar la cantidad de equipos de la custodia
        if inv_custodia.equipos_cantidad != equipos_cantidad:
            inv_custodia.equipos_cantidad = equipos_cantidad
            hay_que_actualizar = True
        # Si es diferente, actualizar la cantidad de fotos de la custodia
        if inv_custodia.equipos_fotos_cantidad != equipos_fotos_cantidad:
            inv_custodia.equipos_fotos_cantidad = equipos_fotos_cantidad
            hay_que_actualizar = True
        # Si hay que actualizar, guardar los cambios
        if hay_que_actualizar:
            inv_custodia.save()
            contador += 1
            if contador % 100 == 0:
                click.echo(f"  Van {contador}...")
    click.echo(f"{contador} custodias actualizadas.")


cli.add_command(actualizar)

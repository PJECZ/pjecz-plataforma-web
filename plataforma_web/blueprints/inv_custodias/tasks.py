"""
Inventarios Custodias, tareas en el fondo

- actualizar: Actualizar las cantidades de equipos y fotos de las custodias
"""

import logging

from lib.tasks import set_task_progress

from plataforma_web.app import create_app
from plataforma_web.extensions import db

from plataforma_web.blueprints.inv_custodias.models import InvCustodia
from plataforma_web.blueprints.inv_equipos.models import InvEquipo
from plataforma_web.blueprints.inv_equipos_fotos.models import InvEquipoFoto

bitacora = logging.getLogger(__name__)
bitacora.setLevel(logging.INFO)
formato = logging.Formatter("%(asctime)s:%(levelname)s:%(message)s")
empunadura = logging.FileHandler("logs/inv_custodias.log")
empunadura.setFormatter(formato)
bitacora.addHandler(empunadura)

app = create_app()
app.app_context().push()
db.app = app


def actualizar():
    """Actualizar las cantidades de equipos y fotos de las custodias"""

    # Iniciar tarea
    mensaje_inicial = "Inicia actualizar las cantidades de equipos y fotos de las custodias"
    set_task_progress(0, mensaje_inicial)
    bitacora.info(mensaje_inicial)

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

    # Terminar tarea
    mensaje_final = f"Termina con {contador} custodias actualizadas en cantidades de equipos y fotos"
    set_task_progress(100, mensaje_final)
    bitacora.info(mensaje_final)
    return mensaje_final

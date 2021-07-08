"""
Rep Reportes, tareas en el fondo

- elaborar: Elaborar reporte
"""
from datetime import datetime
import logging
from lib.tasks import set_task_progress, set_task_error

from plataforma_web.app import create_app
from plataforma_web.blueprints.modulos.models import Modulo
from plataforma_web.blueprints.bitacoras.models import Bitacora
from plataforma_web.blueprints.rep_reportes.models import RepReporte
from plataforma_web.blueprints.rep_resultados.models import RepResultado


bitacora = logging.getLogger(__name__)
bitacora.setLevel(logging.INFO)
formato = logging.Formatter("%(asctime)s:%(levelname)s:%(message)s")
empunadura = logging.FileHandler("rep_reportes.log")
empunadura.setFormatter(formato)
bitacora.addHandler(empunadura)

app = create_app()
app.app_context().push()


def elaborar(reporte_id: int):
    """Elaborar reporte"""

    # Validar reporte
    rep_reporte = RepReporte.query.get(reporte_id)
    if rep_reporte is None:
        mensaje = set_task_error("El reporte no exite.")
        bitacora.error(mensaje)
        return mensaje
    if rep_reporte.estatus != "A":
        mensaje = set_task_error("El reporte no es activo.")
        bitacora.error(mensaje)
        return mensaje
    if rep_reporte.progreso != "PENDIENTE":
        mensaje = set_task_error("El progreso no es PENDIENTE.")
        bitacora.warning(mensaje)
        return mensaje
    if rep_reporte.programado > datetime.now():
        mensaje = set_task_error("El reporte está programado para el futuro.")
        bitacora.warning(mensaje)
        return mensaje
    if len(rep_reporte.rep_resultados) > 0:
        mensaje = set_task_error("El reporte ya tiene resultados; se omite.")
        bitacora.warning(mensaje)
        return mensaje

    # Elaborar reporte de totales por cada módulo
    modulos = Modulo.query.filter(Modulo.estatus == "A").order_by(Modulo.nombre).all()
    cantidad = 0
    for modulo in modulos:
        cantidad = Bitacora.query.filter(Bitacora.modulo == modulo.nombre).filter(Bitacora.creado >= rep_reporte.inicio).filter(Bitacora.creado <= rep_reporte.termino).count()
        RepResultado(
            rep_reporte=rep_reporte,
            modulo=modulo,
            descripcion="Total de operaciones",
            tipo="TOTAL",
            cantidad=cantidad,
        ).save()
        cantidad += 1

    # Cambiar progreso a TERMINADO
    rep_reporte.progreso = "TERMINADO"
    rep_reporte.save()

    # Terminar tarea
    if cantidad > 0:
        mensaje = f"Para {rep_reporte.descripcion} hay {cantidad} resultados y cambia su progreso a TERMINADO."
    else:
        mensaje = f"Para {rep_reporte.descripcion} no hay resultados."
    set_task_progress(100)
    bitacora.info(mensaje)
    return mensaje

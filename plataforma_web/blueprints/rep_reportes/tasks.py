"""
Rep Reportes, tareas en el fondo
"""
from datetime import date, datetime, timedelta
import logging
from lib.tasks import set_task_progress, set_task_error

from plataforma_web.app import create_app
from plataforma_web.blueprints.modulos.models import Modulo
from plataforma_web.blueprints.bitacoras.models import Bitacora
from plataforma_web.blueprints.rep_graficas.models import RepGrafica
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


def preparar_diarios(rep_grafica: RepGrafica, desde: date, hasta: date):
    """Preparar los reportes diarios de una gráfica"""
    contador = 0
    puntero = desde
    while puntero <= hasta:
        inicio = datetime(
            year=puntero.year,
            month=puntero.month,
            day=puntero.day,
            hour=0,
            minute=0,
            second=0,
        )
        termino = datetime(
            year=puntero.year,
            month=puntero.month,
            day=puntero.day,
            hour=23,
            minute=59,
            second=59,
        )
        siguiente_dia = (termino + timedelta(days=1)).date()
        programado = datetime(
            year=siguiente_dia.year,
            month=siguiente_dia.month,
            day=siguiente_dia.day,
            hour=0,
            minute=0,
            second=0,
        )
        RepReporte(
            rep_grafica=rep_grafica,
            descripcion="Reporte diario",
            desde=inicio,
            hasta=termino,
            programado=programado,
            progreso="PENDIENTE",
        ).save()
        puntero += timedelta(days=1)
        contador += 1
    return f"Se prepararon {contador} reportes diarios."


def elaborar(reporte_id: int):
    """Elaborar reporte"""
    bitacora.info("Inicia")
    cantidad = 0

    # Validar reporte
    reporte = RepReporte.query.get(reporte_id)
    if reporte is None:
        mensaje = set_task_error("El reporte no exite.")
        bitacora.error(mensaje)
        return mensaje
    if reporte.estatus != "A":
        mensaje = set_task_error("El reporte no es activo.")
        bitacora.error(mensaje)
        return mensaje
    if reporte.progreso != "PENDIENTE":
        mensaje = set_task_error("El progreso no es PENDIENTE.")
        bitacora.error(mensaje)
        return mensaje
    if reporte.programado > datetime.now():
        mensaje = set_task_error("El reporte está programado para el futuro.")
        bitacora.error(mensaje)
        return mensaje

    # Elaborar reporte de totales por cada módulo
    modulos = Modulo.query.filter(Modulo.estatus == "A").order_by(Modulo.nombre).all()
    for modulo in modulos:
        cantidad = Bitacora.query.filter(Bitacora.modulo == modulo.nombre).filter(Bitacora.creado >= reporte.desde).filter(Bitacora.creado <= reporte.hasta).count()
        RepResultado(
            reporte=reporte,
            modulo=modulo,
            descripcion="Total de operaciones",
            tipo="TOTAL",
            cantidad=cantidad,
        ).save()
        cantidad += 1

    # Cambiar progreso a TERMINADO
    reporte.progreso = "TERMINADO"
    reporte.save()

    # Terminar tarea
    mensaje = f"Termina con {cantidad} resultados."
    set_task_progress(100)
    bitacora.info(mensaje)
    return mensaje

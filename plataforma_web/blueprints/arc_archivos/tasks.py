"""
Archivo, tareas para ejecutar en el fondo
"""
from datetime import date, timedelta
import locale
import logging

from dotenv import load_dotenv

from lib.tasks import set_task_progress, set_task_error
from plataforma_web.app import create_app
from plataforma_web.blueprints.arc_solicitudes.models import ArcSolicitud
from plataforma_web.blueprints.arc_solicitudes_bitacoras.models import ArcSolicitudBitacora
from plataforma_web.blueprints.arc_remesas.models import ArcRemesa

load_dotenv()  # Take environment variables from .env

DIAS_ANTIGUEDAD = 5

bitacora = logging.getLogger(__name__)
bitacora.setLevel(logging.INFO)
formato = logging.Formatter("%(asctime)s:%(levelname)s:%(message)s")
empunadura = logging.FileHandler("archivo.log")
empunadura.setFormatter(formato)
bitacora.addHandler(empunadura)

app = create_app()
app.app_context().push()

locale.setlocale(locale.LC_TIME, "es_MX.utf8")


def pasar_al_historial_solicitudes_remesas():
    """Pasar al historial las solicitudes y remesas con mucha antigüedad habiendo sido procesadas correctamente"""

    # Fecha
    fecha_limite = date.today() - timedelta(days=DIAS_ANTIGUEDAD)
    contador = 0

    # Selección de solicitudes con más de tantos días de antigüedad y en estado de recibidos
    solicitudes = ArcSolicitud.query.filter_by(estado="ENTREGADO").filter(ArcSolicitud.tiempo_recepcion >= fecha_limite).all()
    for solicitud in solicitudes:
        solicitud.esta_archivado = True
        solicitud.save()
        contador += 1
        # Añadir acción a la bitácora de Solicitudes
        ArcSolicitudBitacora(
            arc_solicitud=solicitud,
            usuario=current_user,  # TODO: Usuario quien reporta. ROBOT.
            accion="PASADA AL HISTORIAL",
            observaciones="Tarea programada",
        ).save()
    bitacora.info("Se han pasado al historial %d solicitudes con fechas de recibido mayor a %d días.", contador, DIAS_ANTIGUEDAD)

    # Terminar tarea
    set_task_progress(100)
    mensaje_final = "Terminado satisfactoriamente"
    bitacora.info(mensaje_final)
    return mensaje_final

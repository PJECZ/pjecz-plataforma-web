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
from plataforma_web.blueprints.arc_remesas_bitacoras.models import ArcRemesaBitacora
from plataforma_web.blueprints.usuarios.models import Usuario

load_dotenv()  # Take environment variables from .env

DIAS_ANTIGUEDAD = 5
USUARIO_DEFECTO = "archivo@pjecz.gob.mx"

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

    # Ubicar al usuario responsable para dicha operación
    usuario = Usuario.query.filter_by(email=USUARIO_DEFECTO).filter_by(estatus="A").first()
    if not usuario:
        mensaje_final = f"ERROR: usuario por defecto no localizado '{USUARIO_DEFECTO}'"
        bitacora.error(mensaje_final)
        return mensaje_final

    set_task_progress(1)

    # Selección de solicitudes con más de tantos días de antigüedad y en estado de recibidos
    solicitudes = ArcSolicitud.query.filter_by(estado="ENTREGADO").filter_by(esta_archivado=False).filter(ArcSolicitud.tiempo_recepcion <= fecha_limite).all()
    contador = 0
    for solicitud in solicitudes:
        solicitud.esta_archivado = True
        solicitud.save()
        contador += 1
        # Añadir acción a la bitácora de Solicitudes
        ArcSolicitudBitacora(
            arc_solicitud=solicitud,
            usuario=usuario,
            accion="PASADA AL HISTORIAL",
            observaciones="Tarea programada",
        ).save()
    bitacora.info("Se han pasado al historial %d solicitudes con fechas de recibido mayor a %d días.", contador, DIAS_ANTIGUEDAD)

    set_task_progress(50)

    # Selección de remesas con más de tantos días de antigüedad y en estado de ARCHIVADO
    remesas = ArcRemesa.query.filter_by(estado="ARCHIVADO").filter_by(esta_archivado=False).filter(ArcRemesa.modificado <= fecha_limite).all()
    contador = 0
    for remesa in remesas:
        remesa.esta_archivado = True
        remesa.save()
        contador += 1
        # Añadir acción a la bitácora de remesas
        ArcRemesaBitacora(
            arc_remesa=remesa,
            usuario=usuario,
            accion="PASADA AL HISTORIAL",
            observaciones="Tarea programada",
        ).save()
    bitacora.info("Se han pasado al historial %d remesas con fechas de recibido mayor a %d días.", contador, DIAS_ANTIGUEDAD)

    # Terminar tarea
    set_task_progress(100)
    mensaje_final = "Terminado satisfactoriamente"
    bitacora.info(mensaje_final)
    return mensaje_final

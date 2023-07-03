"""
Sentencias, tareas para ejecutar en el fondo
"""
import base64
import csv
from datetime import datetime, date
import locale
import logging
import os
from pathlib import Path
import random
import re

from dateutil.tz import tzlocal
from dotenv import load_dotenv
from google.cloud import storage
import sendgrid
from sendgrid.helpers.mail import Attachment, ContentId, Disposition, Email, FileContent, FileName, FileType, To, Content, Mail

from lib.tasks import set_task_progress, set_task_error
from plataforma_web.app import create_app
from plataforma_web.blueprints.autoridades.models import Autoridad
from plataforma_web.blueprints.sentencias.models import Sentencia
from plataforma_web.blueprints.usuarios.models import Usuario

load_dotenv()  # Take environment variables from .env

bitacora = logging.getLogger(__name__)
bitacora.setLevel(logging.INFO)
formato = logging.Formatter("%(asctime)s:%(levelname)s:%(message)s")
empunadura = logging.FileHandler("sentencias.log")
empunadura.setFormatter(formato)
bitacora.addHandler(empunadura)

app = create_app()
app.app_context().push()

locale.setlocale(locale.LC_TIME, "es_MX.utf8")

SUBDIRECTORIO = "Sentencias"


def enviar_reporte():
    """Enviar via correo electronico el reporte de sentencias"""

    # Fecha
    fecha = date.today()

    # Momento en que se elabora este reporte
    momento = datetime.now()
    momento_str = momento.strftime("%d/%B/%Y %I:%M%p")
    subject = f"Sentencias del {fecha.strftime('%d/%B/%Y')}"

    # Definir la ruta al archivo temporal CSV
    random_hex = "%030x" % random.randrange(16 ** 30)
    reporte_ruta = Path("/tmp/reporte-sentencias-" + random_hex + ".csv")
    reporte_archivo = f"reporte-sentencias-{fecha.strftime('%Y-%m-%d')}.csv"

    # Cabecera
    bitacora.info("Inicia enviar reporte de %s", momento_str)
    contenidos = [f"<h1>PJECZ Plataforma Web</h1><h2>{subject}</h2><p>Fecha de elaboración: {momento_str}.<br>ESTE MENSAJE ES ELABORADO POR UN PROGRAMA. FAVOR DE NO RESPONDER.</p>"]

    # Contenido
    sentencias = Sentencia.query.order_by(Sentencia.id.desc()).limit(50).all()
    if len(sentencias) == 0:
        bitacora.warning("No hay sentencias")
    else:
        contador = 0
        with open(reporte_ruta, "w", encoding="utf8") as puntero:
            reporte = csv.writer(puntero)
            reporte.writerow(
                [
                    "ID",
                    "Autoridades",
                    "Fechas",
                    "Sentencias",
                    "Expedientes",
                    "Materias",
                    "Tipos de Juicios",
                    "URLs",
                ]
            )
            for sentencia in sentencias:
                reporte.writerow(
                    [
                        sentencia.id,
                        sentencia.autoridad.clave,
                        sentencia.fecha,
                        sentencia.sentencia,
                        sentencia.expediente,
                        sentencia.materia_tipo_juicio.materia.nombre,
                        sentencia.materia_tipo_juicio.descripcion,
                        sentencia.url,
                    ]
                )
                contador += 1
        bitacora.info("Se han escrito %d sentencias en el archivo CSV.", contador)

    # Si no hay contenido, no enviar nada
    if contador == 0:
        mensaje = "No se va enviar nada porque no hay sentencias."
        bitacora.info(mensaje)
    else:
        # Preparar el mensaje para manadr con SendGrid
        api_key = os.getenv("SENDGRID_API_KEY", "")
        if api_key == "":
            mensaje = "No se pudo enviar el reporte de listas de acuerdos porque no esta definida la variable de entorno SENDGRID_API_KEY"
            bitacora.warning(mensaje)
            return set_task_error(mensaje)
        sendgrid_client = sendgrid.SendGridAPIClient(api_key=api_key)
        from_str = os.getenv("SENDGRID_FROM_EMAIL", "")
        if from_str == "":
            mensaje = "No se pudo enviar el reporte de listas de acuerdos porque no esta definida la variable de entorno SENDGRID_FROM_EMAIL"
            bitacora.warning(mensaje)
            return set_task_error(mensaje)
        from_email = Email(from_str)
        to_str = os.getenv("SENDGRID_TO_EMAIL_REPORTES", "")
        if to_str == "":
            mensaje = "No se pudo enviar el reporte de listas de acuerdos porque no esta definida la variable de entorno SENDGRID_TO_EMAIL_REPORTES"
            bitacora.warning(mensaje)
            return set_task_error(mensaje)
        to_email = To(to_str)
        content = Content("text/html", "<br>".join(contenidos))
        mail = Mail(from_email, to_email, subject, content)
        # Adjuntar el archivo CSV
        with open(reporte_ruta, "r", encoding="utf8") as puntero:
            datos = puntero.read()
            puntero.close()
        encoded = base64.b64encode(bytes(datos, "utf8")).decode("utf8")
        attachment = Attachment()
        attachment.file_content = FileContent(encoded)
        attachment.file_type = FileType("text/csv")
        attachment.file_name = FileName(reporte_archivo)
        attachment.disposition = Disposition("attachment")
        attachment.content_id = ContentId("ArchivoCSV")
        mail.attachment = attachment
        # Enviar el mensaje
        sendgrid_client.client.mail.send.post(request_body=mail.get())
        # Eliminar el archivo CSV
        reporte_ruta.unlink(missing_ok=True)

    # Terminar tarea
    set_task_progress(100)
    mensaje_final = "Terminado satisfactoriamente"
    bitacora.info(mensaje_final)
    return mensaje_final


def refrescar(autoridad_id: int, usuario_id: int = None):
    """Rastrear las sentencias para agregar las que no tiene y dar de baja las que no existen en la BD"""
    bitacora.info("Inicia")

    # Para validar la fecha
    anos_limite = 20
    hoy = date.today()
    hoy_dt = datetime(year=hoy.year, month=hoy.month, day=hoy.day)
    limite_dt = datetime(year=hoy.year - anos_limite, month=1, day=1)

    # Validad usuario
    usuario = None
    if usuario_id is not None:
        usuario = Usuario.query.get(usuario_id)
        if usuario is None or usuario.estatus != "A":
            return set_task_error("El usuario no existe o no es activo")
        bitacora.info("- Usuario %s", usuario.email)

    # Validar autoridad
    autoridad = Autoridad.query.get(autoridad_id)
    if autoridad is None or autoridad.estatus != "A":
        return set_task_error("La autoridad no existe o no es activa")
    if autoridad.directorio_sentencias is None or autoridad.directorio_sentencias == "":
        return set_task_error("La autoridad no tiene directorio para sentencias")
    bitacora.info("- Autoridad %s", autoridad.clave)

    # Consultar las sentencias (activos e inactivos) y elaborar lista de archivos
    sentencias = Sentencia.query.filter(Sentencia.autoridad == autoridad).all()
    total_en_bd = len(sentencias)
    bitacora.info("- Tiene %d registros en la base de datos", total_en_bd)

    # Obtener archivos en el depósito
    deposito = os.environ.get("CLOUD_STORAGE_DEPOSITO_SENTENCIAS", "pjecz-pruebas")
    bucket = storage.Client().get_bucket(deposito)
    subdirectorio = f"{SUBDIRECTORIO}/{autoridad.directorio_sentencias}"
    blobs = list(bucket.list_blobs(prefix=subdirectorio))
    total_en_deposito = len(blobs)
    if total_en_deposito == 0:
        return set_task_error(f"No existe o no hay archivos en {subdirectorio}")
    bitacora.info("- Tiene %d archivos en el depósito", total_en_deposito)

    # Precompilar expresión regular para "NO" letras y digitos
    letras_digitos_regex = re.compile("[^0-9a-zA-Z]+")

    # Iniciar la tarea y contadores
    set_task_progress(0)
    contador_incorrectos = 0
    contador_insertados = 0
    contador_presentes = 0

    # Bucle por los archivos en el depósito
    for blob in blobs:

        # Validar que sea PDF
        ruta = Path(blob.name)
        if ruta.suffix.lower() != ".pdf":
            continue

        # Saltar y quitar de la lista si se encuentra en la consulta
        esta_en_bd = False
        for indice, sentencia in enumerate(sentencias):
            if blob.public_url == sentencia.url:
                sentencias.pop(indice)
                esta_en_bd = True
                break
        if esta_en_bd:
            contador_presentes += 1
            continue

        # A partir de aquí tenemos un archivo que no está en la base de datos
        # El nombre del archivo para una sentencia debe ser como
        # AAAA-MM-DD-EEEE-EEEE-SENT-SENT-G-IDHASED.pdf

        # Separar elementos del nombre del archivo
        nombre_sin_extension = ruta.name[:-4]
        elementos = re.sub(letras_digitos_regex, "-", nombre_sin_extension).strip("-").split("-")

        # Tomar la fecha
        try:
            ano = int(elementos[0])
            mes = int(elementos[1])
            dia = int(elementos[2])
            fecha = date(ano, mes, dia)
        except (IndexError, ValueError):
            bitacora.warning("X Fecha incorrecta: %s", ruta)
            contador_incorrectos += 1
            continue

        # Descartar fechas en el futuro o muy en el pasado
        if not limite_dt <= datetime(year=fecha.year, month=fecha.month, day=fecha.day) <= hoy_dt:
            bitacora.warning("X Fecha fuera de rango: %s", ruta)
            contador_incorrectos += 1
            continue

        # Tomar la sentencia
        try:
            numero = int(elementos[3])
            ano = int(elementos[4])
            sentencia = str(numero) + "/" + str(ano)
        except (IndexError, ValueError):
            bitacora.warning("X Sentencia incorrecta: %s", ruta)
            contador_incorrectos += 1
            continue

        # Tomar el expediente
        try:
            numero = int(elementos[5])
            ano = int(elementos[6])
            expediente = str(numero) + "/" + str(ano)
        except (IndexError, ValueError):
            bitacora.warning("X Expediente incorrecto: %s", ruta)
            contador_incorrectos += 1
            continue

        # Tomar la paridad de género
        es_perspectiva_genero = False
        if len(elementos) > 7 and elementos[7].upper() == "G":
            es_perspectiva_genero = True

        # Insertar
        tiempo_local = blob.time_created.astimezone(tzlocal())
        Sentencia(
            creado=tiempo_local,
            modificado=tiempo_local,
            autoridad=autoridad,
            fecha=fecha,
            sentencia=sentencia,
            expediente=expediente,
            es_perspectiva_genero=es_perspectiva_genero,
            archivo=ruta.name,
            url=blob.public_url,
        ).save()
        contador_insertados += 1

    # Los registros que no se encontraron serán dados de baja
    contador_borrados = 0
    for sentencia in sentencias:
        if sentencia.estatus == "A":
            sentencia.delete()
            contador_borrados += 1

    # Mensaje final
    mensajes = []
    if contador_insertados > 0:
        mensajes.append(f"Se insertaron {contador_insertados} registros")
    else:
        mensajes.append("No se insertaron registros")
    if contador_borrados > 0:
        mensajes.append(f"Se borraron {contador_borrados} registros")
    else:
        mensajes.append("No se borraron registros")
    if contador_presentes > 0:
        mensajes.append(f"Están presentes {contador_presentes}")
    if contador_incorrectos > 0:
        mensajes.append(f"Hay {contador_incorrectos} archivos con nombres incorrectos")
    mensaje_final = "- " + ". ".join(mensajes) + "."

    # Terminar tarea
    set_task_progress(100)
    bitacora.info(mensaje_final)
    bitacora.info("Termina")
    return mensaje_final

"""
Listas de Acuerdos, tareas para ejecutar en el fondo

- refrescar: Rastrear las listas de acuerdos para agregar las que no tiene y dar de baja las que no existen en la BD
- enviar_reporte: Enviar via correo electronico el reporte de listas de acuerdos
"""
import locale
import logging
import os
import re
from datetime import datetime, date
from pathlib import Path

from dateutil.tz import tzlocal
from dotenv import load_dotenv
from google.cloud import storage
from hashids import Hashids
import pandas as pd
import sendgrid
from sendgrid.helpers.mail import Email, To, Content, Mail

from lib.safe_string import safe_string
from lib.tasks import set_task_progress, set_task_error
from plataforma_web.app import create_app
from plataforma_web.extensions import db
from plataforma_web.blueprints.autoridades.models import Autoridad
from plataforma_web.blueprints.distritos.models import Distrito
from plataforma_web.blueprints.listas_de_acuerdos.models import ListaDeAcuerdo
from plataforma_web.blueprints.usuarios.models import Usuario

load_dotenv()  # Take environment variables from .env

bitacora = logging.getLogger(__name__)
bitacora.setLevel(logging.INFO)
formato = logging.Formatter("%(asctime)s:%(levelname)s:%(message)s")
empunadura = logging.FileHandler("listas_de_acuerdos.log")
empunadura.setFormatter(formato)
bitacora.addHandler(empunadura)

app = create_app()
app.app_context().push()
db.app = app

locale.setlocale(locale.LC_TIME, "es_MX.utf8")

SUBDIRECTORIO = "Listas de Acuerdos"


def refrescar(autoridad_id: int, usuario_id: int = None):
    """Rastrear las listas de acuerdos para agregar las que no tiene y dar de baja las que no existen en la BD"""
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
    if autoridad.directorio_listas_de_acuerdos is None or autoridad.directorio_listas_de_acuerdos == "":
        return set_task_error("La autoridad no tiene directorio para listas de acuerdos")
    bitacora.info("- Autoridad %s", autoridad.clave)

    # Consultar las listas de acuerdos (activos e inactivos) y elaborar lista de fechas
    listas_de_acuerdos = ListaDeAcuerdo.query.filter(ListaDeAcuerdo.autoridad == autoridad).all()
    total_en_bd = len(listas_de_acuerdos)
    bitacora.info("- Tiene %d registros en la base de datos", total_en_bd)

    # Obtener el nombre del deposito
    deposito = os.getenv("CLOUD_STORAGE_DEPOSITO_LISTAS_DE_ACUERDOS", "")
    if deposito == "":
        mensaje = "Falta la variable de entorno CLOUD_STORAGE_DEPOSITO_LISTAS_DE_ACUERDOS"
        bitacora.error(mensaje)
        return set_task_error(mensaje)

    # Obtener archivos en el depósito
    bucket = storage.Client().get_bucket(deposito)
    subdirectorio = f"{SUBDIRECTORIO}/{autoridad.directorio_listas_de_acuerdos}"
    blobs = list(bucket.list_blobs(prefix=subdirectorio))
    total_en_deposito = len(blobs)
    if total_en_deposito == 0:
        return set_task_error(f"No existe o no hay archivos en {subdirectorio}")
    bitacora.info("- Tiene %d archivos en el depósito", total_en_deposito)

    # Precompilar expresión regular para "NO" letras y digitos
    letras_digitos_regex = re.compile("[^0-9a-zA-Z]+")

    # Precompilar expresión regular para hashid
    hashid_regexp = re.compile("[0-9a-zA-Z]{8}")

    # Obtener el HASH para descifrar los IDs
    salt = os.getenv("SALT", "")
    if salt == "":
        mensaje = "Falta la variable de entorno SALT"
        bitacora.error(mensaje)
        return set_task_error(mensaje)
    hashids = Hashids(salt=salt, min_length=8)

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
        for indice, lista_de_acuerdo in enumerate(listas_de_acuerdos):
            if blob.public_url == lista_de_acuerdo.url:
                listas_de_acuerdos.pop(indice)
                esta_en_bd = True
                break
        if esta_en_bd:
            contador_presentes += 1
            continue

        # A partir de aquí tenemos un archivo que no está en la base de datos
        # El nombre del archivo para una lista de acuerdos debe ser como
        # AAAA-MM-DD-LISTA-DE-ACUERDOS-IDHASED.pdf

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

        # Tomar la descripción, sin el hash del id de estar presente
        if len(elementos) > 3:
            if re.match(hashid_regexp, elementos[-1]) is None:
                descripcion = safe_string(" ".join(elementos[3:]))
            else:
                decodificado = hashids.decode(elementos[-1])
                if isinstance(decodificado, tuple) and len(decodificado) > 0:
                    descripcion = safe_string(" ".join(elementos[3:-1]))
                else:
                    descripcion = safe_string(" ".join(elementos[3:]))
        else:
            descripcion = "LISTA DE ACUERDOS"

        # Insertar si no está
        tiempo_local = blob.time_created.astimezone(tzlocal())
        ListaDeAcuerdo(
            creado=tiempo_local,
            modificado=tiempo_local,
            autoridad=autoridad,
            fecha=fecha,
            descripcion=descripcion,
            archivo=ruta.name,
            url=blob.public_url,
        ).save()
        contador_insertados += 1

    # Los registros que no se encontraron serán dados de baja
    contador_borrados = 0
    for lista_de_acuerdo in listas_de_acuerdos:
        if lista_de_acuerdo.estatus == "A":
            lista_de_acuerdo.delete()
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


def enviar_reporte(fecha: date = None):
    """Enviar via correo electronico el reporte de listas de acuerdos"""

    # Fecha a consultar
    if fecha is None:
        fecha = date.today()

    # Momento en que se elabora este reporte
    momento = datetime.now()
    momento_str = momento.strftime("%d/%B/%Y %I:%M%p")
    subject = f"Listas de Acuerdos del {fecha.strftime('%d/%B/%Y')}"

    # Cabecera
    bitacora.info("Inicia enviar reporte de %s", momento_str)
    contenidos = [f"<h1>PJECZ Plataforma Web</h1><h2>{subject}</h2><p>Fecha de elaboración: {momento_str}.<br>ESTE MENSAJE ES ELABORADO POR UN PROGRAMA. FAVOR DE NO RESPONDER.</p>"]

    # Distritos
    distritos_select = db.session.query(Distrito.id, Distrito.nombre).filter(Distrito.es_distrito_judicial == True).filter(Distrito.estatus == "A").statement
    distritos = pd.read_sql_query(sql=distritos_select, con=db.engine)
    total = 0
    for distrito_index, distrito_row in distritos.iterrows():

        # Juzgados
        autoridades_select = (
            db.session.query(Autoridad.id, Autoridad.clave, Autoridad.descripcion_corta)
            .filter(Autoridad.distrito_id == distrito_row["id"])
            .filter(Autoridad.es_jurisdiccional == True)
            .filter(Autoridad.es_notaria == False)
            .filter(Autoridad.estatus == "A")
            .order_by(Autoridad.clave)
            .statement
        )
        autoridades = pd.read_sql_query(sql=autoridades_select, con=db.engine)

        # Listas de acuerdos
        listas_de_acuerdos_select = (
            db.session.query(Autoridad.clave, ListaDeAcuerdo.fecha, ListaDeAcuerdo.url)
            .join(Autoridad)
            .filter(ListaDeAcuerdo.autoridad_id.in_(autoridades.id))
            .filter(ListaDeAcuerdo.fecha == fecha)
            .filter(ListaDeAcuerdo.estatus == "A")
            .order_by(Autoridad.clave, ListaDeAcuerdo.creado)
            .statement
        )
        listas_de_acuerdos = pd.read_sql_query(sql=listas_de_acuerdos_select, con=db.engine)
        listas_de_acuerdos.columns = ["clave2", "fecha", "url"]

        # Reporte
        diario = pd.merge(autoridades, listas_de_acuerdos, left_on="clave", right_on="clave2", how="left").drop("clave", axis=1).drop("clave2", axis=1).drop("id", axis=1)
        contenidos.append("<h3>" + distrito_row["nombre"] + "</h3>" + diario.to_html())

        # A bitacora
        cantidad = len(listas_de_acuerdos)
        bitacora.info("- En %s hay %s", distrito_row["nombre"], cantidad)
        total += cantidad

    # Agregar el total a la bitacora
    bitacora.info("Total %s", str(total))

    # Pie del mensaje
    contenidos.append("<p>ESTE MENSAJE ES ELABORADO POR UN PROGRAMA. FAVOR DE NO RESPONDER.</p>")

    # Enviar mensaje via correo electronico
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
    sendgrid_client.client.mail.send.post(request_body=mail.get())

    # Terminar tarea
    set_task_progress(100)
    mensaje_final = "Terminado satisfactoriamente"
    bitacora.info(mensaje_final)
    return mensaje_final

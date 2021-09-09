"""
Listas de Acuerdos, tareas para ejecutar en el fondo

- refrescar: Rastrear las listas de acuerdos para agregar las que no tiene y dar de baja las que no existen en la BD
- enviar_reporte: Enviar via correo electronico el reporte de listas de acuerdos
"""
import logging
import os
import re
from datetime import datetime, date
from pathlib import Path

from dateutil.tz import tzlocal
from google.cloud import storage
from hashids import Hashids
from rq import get_current_job
import pandas as pd

import sendgrid
from sendgrid.helpers.mail import Email, To, Content, Mail

from lib.safe_string import safe_string

from plataforma_web.app import create_app
from plataforma_web.extensions import db

from plataforma_web.blueprints.autoridades.models import Autoridad
from plataforma_web.blueprints.distritos.models import Distrito
from plataforma_web.blueprints.listas_de_acuerdos.models import ListaDeAcuerdo
from plataforma_web.blueprints.tareas.models import Tarea
from plataforma_web.blueprints.usuarios.models import Usuario

bitacora = logging.getLogger(__name__)
bitacora.setLevel(logging.INFO)
formato = logging.Formatter("%(asctime)s:%(levelname)s:%(message)s")
empunadura = logging.FileHandler("listas_de_acuerdos.log")
empunadura.setFormatter(formato)
bitacora.addHandler(empunadura)

app = create_app()
app.app_context().push()
db.app = app

SUBDIRECTORIO = "Listas de Acuerdos"


def set_task_progress(progress: int, mensaje: str = None):
    """Cambiar el progreso de la tarea"""
    job = get_current_job()
    if job:
        job.meta["progress"] = progress
        job.save_meta()
        tarea = Tarea.query.get(job.get_id())
        if tarea:
            if progress >= 100:
                tarea.ha_terminado = True
            if mensaje is not None:
                tarea.descripcion = mensaje
            tarea.save()


def set_task_error(mensaje: str):
    """Al fallar la tarea debe tomar el mensaje y terminarla"""
    job = get_current_job()
    if job:
        job.meta["progress"] = 100
        job.save_meta()
        tarea = Tarea.query.get(job.get_id())
        if tarea:
            tarea.ha_terminado = True
            tarea.descripcion = mensaje
            tarea.save()
    bitacora.error(mensaje)
    bitacora.info("Termina")
    return mensaje


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

    # Obtener archivos en el depósito
    deposito = os.environ.get("CLOUD_STORAGE_DEPOSITO", "pjecz-pruebas")
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

    # Para descifrar los hash ids
    hashids = Hashids(salt=os.environ.get("SALT", "Esta es una muy mala cadena aleatoria"), min_length=8)

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


def enviar_reporte():
    """Enviar via correo electronico el reporte de listas de acuerdos"""

    # Tiempos
    momento = datetime.now()
    momento_str = momento.strftime("%d/%B/%Y %I:%M%p")
    hoy = date.today()

    # Cabecera
    bitacora.info("Reporte diario del %s", momento_str)
    contenidos = [
        "<h1>PJECZ Plataforma Web</h1>",
        f"<p>Reporte diario de <strong>Listas de Acuerdos</strong> del {momento_str}</p>",
    ]

    # Distritos
    distritos_select = db.session.query(Distrito.id, Distrito.nombre).filter(Distrito.es_distrito_judicial == True).filter(Distrito.estatus == "A").statement
    distritos = pd.read_sql_query(sql=distritos_select, con=db.engine)
    total = 0
    for distrito in distritos:
        contenidos.append(f"<h3>{distrito.nombre}</h3>")

        # Juzgados
        autoridades_select = (
            db.session.query(Autoridad.id, Autoridad.clave, Autoridad.descripcion_corta)
            .filter(Autoridad.distrito_id == distrito.id)
            .filter(Autoridad.es_jurisdiccional == True)
            .filter(Autoridad.es_notaria == False)
            .filter(Autoridad.estatus == "A")
            .order_by(Autoridad.clave)
            .statement
        )
        autoridades = pd.read_sql_query(sql=autoridades_select, con=db.engine)

        # Listas de acuerdos
        listas_de_acuerdos_select = (
            db.session.query(Autoridad.clave, ListaDeAcuerdo.archivo, ListaDeAcuerdo.creado)
            .join(Autoridad)
            .filter(ListaDeAcuerdo.autoridad_id.in_(autoridades.id))
            .filter(ListaDeAcuerdo.fecha == hoy)
            .filter(ListaDeAcuerdo.estatus == "A")
            .order_by(ListaDeAcuerdo.creado)
            .statement
        )
        listas_de_acuerdos = pd.read_sql_query(sql=listas_de_acuerdos_select, con=db.engine)
        listas_de_acuerdos.columns = ["clave2", "archivo", "creado"]

        # Reporte
        diario = pd.merge(autoridades, listas_de_acuerdos, left_on="clave", right_on="clave2", how="left").drop("clave2", axis=1)
        contenidos.append(diario.to_html())

        # A bitacora
        cantidad = len(listas_de_acuerdos)
        bitacora.info("- En %s hay %s", distrito.nombre_corto, cantidad)
        total += cantidad

    # Pie del mensaje
    contenidos.append("Este mensaje de crea de forma automatica. Favor de no responder.")

    # Mensaje via correo electronico
    api_key = os.environ.get("SENDGRID_API_KEY", "Debe estar definida como variable de entorno")
    sg = sendgrid.SendGridAPIClient(api_key=api_key)
    from_email = Email("informatica@pjecz.gob.mx")
    to_email = To("guillermo.valdes@pjecz.gob.mx")
    subject = "Plataforma Web - Listas de Acuerdos"
    content = Content("text/html", "/n".join(contenidos))
    mail = Mail(from_email, to_email, subject, content)
    response = sg.client.mail.send.post(request_body=mail.get())
    bitacora.info(response.status_code)
    bitacora.info(response.body)
    bitacora.info(response.headers)

    # Terminar tarea
    set_task_progress(100)
    mensaje_final = "Total " + str(total)
    bitacora.info(mensaje_final)
    return mensaje_final

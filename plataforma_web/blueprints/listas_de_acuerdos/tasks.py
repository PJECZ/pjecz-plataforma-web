"""
Listas de Acuerdos, tareas para ejecutar en el fondo

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


def enviar_reporte(fecha: date = None):
    """Enviar via correo electronico el reporte de listas de acuerdos"""

    # Fecha a consultar
    if fecha is None:
        fecha = date.today()

    # Iniciar tarea
    mensaje_inicial = f"Inicia enviar reporte del {fecha} de listas de acuerdos"
    set_task_progress(0, mensaje_inicial)
    bitacora.info(mensaje_inicial)

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
    mensaje_final = f"Termina enviar reporte del {fecha} de listas de acuerdos"
    set_task_progress(100, mensaje_final)
    bitacora.info(mensaje_final)
    return mensaje_final

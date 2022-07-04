"""
Financieros Vales, tareas en el fondo
"""
from datetime import datetime
import json
import logging
import os

from dotenv import load_dotenv
import requests

from lib.tasks import set_task_progress, set_task_error

from plataforma_web.app import create_app
from plataforma_web.blueprints.fin_vales.models import FinVale
from plataforma_web.blueprints.usuarios.models import Usuario

load_dotenv()  # Take environment variables from .env
FIN_VALES_EFIRMA_SER_FIRMA_CADENA_URL = os.getenv("FIN_VALES_EFIRMA_SER_FIRMA_CADENA_URL")
FIN_VALES_EFIRMA_CAN_FIRMA_CADENA_URL = os.getenv("FIN_VALES_EFIRMA_CAN_FIRMA_CADENA_URL")
FIN_VALES_EFIRMA_APP_ID = os.getenv("FIN_VALES_EFIRMA_APP_ID")
FIN_VALES_EFIRMA_APP_PASS = os.getenv("FIN_VALES_EFIRMA_APP_PASS")

bitacora = logging.getLogger(__name__)
bitacora.setLevel(logging.INFO)
formato = logging.Formatter("%(asctime)s:%(levelname)s:%(message)s")
empunadura = logging.FileHandler("fin_vales.log")
empunadura.setFormatter(formato)
bitacora.addHandler(empunadura)

app = create_app()
app.app_context().push()


def solicitar(fin_vale_id: int, contrasena: str):
    """Firmar electronicamente el vale por quien solicita"""

    # Validar configuracion
    if FIN_VALES_EFIRMA_SER_FIRMA_CADENA_URL is None:
        mensaje = "Falta configurar FIN_VALES_EFIRMA_SER_FIRMA_CADENA_URL"
        bitacora.error(mensaje)
        return set_task_error(mensaje)
    if FIN_VALES_EFIRMA_APP_ID is None:
        mensaje = "Falta configurar FIN_VALES_EFIRMA_APP_ID"
        bitacora.error(mensaje)
        return set_task_error(mensaje)
    if FIN_VALES_EFIRMA_APP_PASS is None:
        mensaje = "Falta configurar FIN_VALES_EFIRMA_APP_PASS"
        bitacora.error(mensaje)
        return set_task_error(mensaje)

    # Consultar el vale
    fin_vale = FinVale.query.get(fin_vale_id)
    if fin_vale is None:
        mensaje = f"No se encontró el vale {fin_vale_id}"
        bitacora.error(mensaje)
        return set_task_error(mensaje)
    if fin_vale.estatus != "A":
        mensaje = f"El vale {fin_vale_id} esta eliminado"
        bitacora.error(mensaje)
        return set_task_error(mensaje)
    if fin_vale.estado != "PENDIENTE":
        mensaje = f"El vale {fin_vale_id} no está en estado PENDIENTE"
        bitacora.error(mensaje)
        return set_task_error(mensaje)

    # Consultar el usuario que solicita
    solicita = Usuario.query.filter_by(email=fin_vale.solicito_email).first()
    if solicita is None:
        mensaje = f"No se encontró el usuario {fin_vale.solicito_email} que solicita"
        bitacora.error(mensaje)
        return set_task_error(mensaje)
    if solicita.efirma_registro_id is None or solicita.efirma_registro_id == 0:
        mensaje = f"El usuario {fin_vale.solicito_email} no tiene registro en el motor de firma"
        bitacora.error(mensaje)
        return set_task_error(mensaje)

    # Juntar los elementos del vale para armar la cadena
    elementos = {
        "id": fin_vale.id,
        "creado": fin_vale.creado.strftime("%Y-%m-%d %H:%M:%S"),
        "justificacion": fin_vale.justificacion,
        "monto": fin_vale.monto,
        "solicito": fin_vale.solicito_nombre,
        "tipo": fin_vale.tipo,
    }

    # Preparar los datos que se van a enviar al motor de firma
    data = {
        "cadenaOriginal": json.dumps(elementos),
        "idRegistro": solicita.efirma_registro_id,
        "contrasenaRegistro": contrasena,
        "idAplicacion": FIN_VALES_EFIRMA_APP_ID,
        "contrasenaAplicacion": FIN_VALES_EFIRMA_APP_PASS,
        "referencia": fin_vale_id,
        "verificarUrl": True,
    }

    # Enviar la solicitud al motor de firma
    try:
        response = requests.post(
            FIN_VALES_EFIRMA_SER_FIRMA_CADENA_URL,
            data=data,
            verify=False,
        )
    except Exception as error:
        mensaje = f"Error al solicitar el vale: {error}"
        bitacora.error(mensaje)
        return set_task_error(mensaje)

    # Si el motor de firma no entrega el estado 200, se registra el error
    if response.status_code != 200:
        mensaje = f"Error al solicitar el vale porque la respuesta no es 200: {response.text}"
        fin_vale.solicito_efirma_mensaje = mensaje
        fin_vale.save()
        bitacora.error(mensaje)
        return set_task_error(mensaje)

    # Ejemplo de la respuesta
    #   "success": true,
    #   "folio": 000001,
    #   "mensaje": "La operación se ha realizado exitosamente.",
    #   "cadenaOriginal": "",
    #   "fecha": "27/06/2022 13:47:11",
    #   "selloDigital": "",
    #   "url": "https://servidor/eFirmaServicios/verificaFirmaCadena.do?verificar=ZhSsI%2FYUG9soc%2FkTfsWVvoUpylEwvoq%2F",
    #   "ip": "172.1.1.1",
    #   "huella": "Primer mensaje de prueba"

    # Convertir la respuesta del motor de firma a un diccionario
    texto = response.text.replace('"{', "{").replace('}"', "}")
    try:
        datos = json.loads(texto)
    except json.JSONDecodeError:
        mensaje = f"Error al solicitar el vale porque la respuesta no es JSON: {response.text}"
        fin_vale.solicito_efirma_mensaje = mensaje
        fin_vale.estado = "ELIMINADO POR SOLICITANTE"
        fin_vale.save()
        bitacora.error(mensaje)
        return set_task_error(mensaje)

    # Validar que se haya firmado correctamente
    if datos["success"] is False:
        mensaje = f"Error al solicitar el vale porque no se firmó correctamente: {response.text}"
        fin_vale.solicito_efirma_mensaje = mensaje
        fin_vale.estado = "ELIMINADO POR SOLICITANTE"
        fin_vale.save()
        bitacora.error(mensaje)
        return set_task_error(mensaje)

    # Actualizar el vale, ahora su estado es SOLICITADO
    fin_vale.solicito_efirma_tiempo = datetime.strptime(datos["fecha"], "%d/%m/%Y %H:%M:%S")
    fin_vale.solicito_efirma_folio = datos["folio"]
    fin_vale.solicito_efirma_selloDigital = datos["selloDigital"]
    fin_vale.solicito_efirma_url = datos["url"]
    fin_vale.solicito_efirma_qr_url = ""  # Pendiente
    fin_vale.estado = "SOLICITADO"
    fin_vale.save()

    # Terminar tarea
    mensaje_final = f"Vale {fin_vale_id} solicitado"
    set_task_progress(100)
    bitacora.info(mensaje_final)
    return mensaje_final


def cancelar_solicitar(fin_vale_id: int, contrasena: str):
    """Cancelar la firma electronica de un vale por quien solicita"""

    # Validar configuracion
    if FIN_VALES_EFIRMA_CAN_FIRMA_CADENA_URL is None:
        mensaje = "Falta configurar FIN_VALES_EFIRMA_CAN_FIRMA_CADENA_URL"
        bitacora.error(mensaje)
        return set_task_error(mensaje)
    if FIN_VALES_EFIRMA_APP_ID is None:
        mensaje = "Falta configurar FIN_VALES_EFIRMA_APP_ID"
        bitacora.error(mensaje)
        return set_task_error(mensaje)
    if FIN_VALES_EFIRMA_APP_PASS is None:
        mensaje = "Falta configurar FIN_VALES_EFIRMA_APP_PASS"
        bitacora.error(mensaje)
        return set_task_error(mensaje)

    # Consultar el vale
    fin_vale = FinVale.query.get(fin_vale_id)
    if fin_vale is None:
        mensaje = f"No se encontró el vale {fin_vale_id}"
        bitacora.error(mensaje)
        return set_task_error(mensaje)
    if fin_vale.estatus != "A":
        mensaje = f"El vale {fin_vale_id} esta eliminado"
        bitacora.error(mensaje)
        return set_task_error(mensaje)
    if fin_vale.estado != "SOLICITADO":
        mensaje = f"El vale {fin_vale_id} no está en estado SOLICITADO"
        bitacora.error(mensaje)
        return set_task_error(mensaje)
    if fin_vale.solicito_efirma_folio is None:
        mensaje = f"El vale {fin_vale_id} no tiene folio de solicitud"
        bitacora.error(mensaje)
        return set_task_error(mensaje)

    # Consultar el usuario que solicita, para cancelar la firma
    solicita = Usuario.query.filter_by(email=fin_vale.solicito_email).first()
    if solicita is None:
        mensaje = f"No se encontró el usuario {fin_vale.solicito_email} que solicita"
        bitacora.error(mensaje)
        return set_task_error(mensaje)
    if solicita.efirma_registro_id is None or solicita.efirma_registro_id == 0:
        mensaje = f"El usuario {fin_vale.solicito_email} no tiene registro en el motor de firma"
        bitacora.error(mensaje)
        return set_task_error(mensaje)

    # Preparar los datos que se van a enviar al motor de firma
    data = {
        "idAplicacion": FIN_VALES_EFIRMA_APP_ID,
        "contrasenaAplicacion": FIN_VALES_EFIRMA_APP_PASS,
        "idRegistro": solicita.efirma_registro_id,
        "contrasenaRegistro": contrasena,
        "folios": fin_vale.solicito_efirma_folio,
    }

    # Enviar la solicitud al motor de firma
    try:
        response = requests.post(
            FIN_VALES_EFIRMA_CAN_FIRMA_CADENA_URL,
            data=data,
            verify=False,
        )
    except Exception as error:
        mensaje = f"Error al cancelar el vale solicitado: {error}"
        bitacora.error(mensaje)
        return set_task_error(mensaje)

    # Actualizar el vale, ahora su estado es CANCELADO POR SOLICITANTE
    fin_vale.estado = "CANCELADO POR SOLICITANTE"
    fin_vale.save()

    # Terminar tarea
    mensaje_final = f"Vale {fin_vale_id} cancelado su solicitud"
    set_task_progress(100)
    bitacora.info(mensaje_final)
    return mensaje_final


def autorizar(fin_vale_id: int, contrasena: str):
    """Firmar electronicamente el vale por quien autoriza"""

    # Validar configuracion
    if FIN_VALES_EFIRMA_SER_FIRMA_CADENA_URL is None:
        mensaje = "Falta configurar FIN_VALES_EFIRMA_SER_FIRMA_CADENA_URL"
        bitacora.error(mensaje)
        return set_task_error(mensaje)
    if FIN_VALES_EFIRMA_APP_ID is None:
        mensaje = "Falta configurar FIN_VALES_EFIRMA_APP_ID"
        bitacora.error(mensaje)
        return set_task_error(mensaje)
    if FIN_VALES_EFIRMA_APP_PASS is None:
        mensaje = "Falta configurar FIN_VALES_EFIRMA_APP_PASS"
        bitacora.error(mensaje)
        return set_task_error(mensaje)

    # Consultar el vale
    fin_vale = FinVale.query.get(fin_vale_id)
    if fin_vale is None:
        mensaje = f"No se encontró el vale {fin_vale_id}"
        bitacora.error(mensaje)
        return set_task_error(mensaje)
    if fin_vale.estatus != "A":
        mensaje = f"El vale {fin_vale_id} esta eliminado"
        bitacora.error(mensaje)
        return set_task_error(mensaje)
    if fin_vale.estado != "SOLICITADO":
        mensaje = f"El vale {fin_vale_id} no está en estado SOLICITADO"
        bitacora.error(mensaje)
        return set_task_error(mensaje)

    # Consultar el usuario que autoriza
    autoriza = Usuario.query.filter_by(email=fin_vale.autorizo_email).first()
    if autoriza is None:
        mensaje = f"No se encontró el usuario {fin_vale.autorizo_email} que autoriza"
        bitacora.error(mensaje)
        return set_task_error(mensaje)
    if autoriza.efirma_registro_id is None or autoriza.efirma_registro_id == 0:
        mensaje = f"El usuario {fin_vale.autorizo_email} no tiene registro en el motor de firma"
        bitacora.error(mensaje)
        return set_task_error(mensaje)

    # Juntar los elementos del vale para armar la cadena
    elementos = {
        "id": fin_vale.id,
        "autorizo": fin_vale.autorizo_nombre,
        "creado": fin_vale.creado.strftime("%Y-%m-%d %H:%M:%S"),
        "justificacion": fin_vale.justificacion,
        "monto": fin_vale.monto,
        "solicito": fin_vale.solicito_nombre,
        "tipo": fin_vale.tipo,
    }

    # Preparar los datos que se van a enviar al motor de firma
    data = {
        "cadenaOriginal": json.dumps(elementos),
        "idRegistro": autoriza.efirma_registro_id,
        "contrasenaRegistro": contrasena,
        "idAplicacion": FIN_VALES_EFIRMA_APP_ID,
        "contrasenaAplicacion": FIN_VALES_EFIRMA_APP_PASS,
        "referencia": fin_vale_id,
        "verificarUrl": True,
    }

    # Enviar la solicitud al motor de firma
    try:
        response = requests.post(
            FIN_VALES_EFIRMA_SER_FIRMA_CADENA_URL,
            data=data,
            verify=False,
        )
    except Exception as error:
        mensaje = f"Error al solicitar el vale: {error}"
        bitacora.error(mensaje)
        return set_task_error(mensaje)

    # Si el motor de firma no entrega el estado 200, se registra el error
    if response.status_code != 200:
        mensaje = f"Error al autorizar el vale porque la respuesta no es 200: {response.text}"
        fin_vale.autorizo_efirma_mensaje = mensaje
        fin_vale.save()
        bitacora.error(mensaje)
        return set_task_error(mensaje)

    # Ejemplo de la respuesta
    #   "success": true,
    #   "folio": 000001,
    #   "mensaje": "La operación se ha realizado exitosamente.",
    #   "cadenaOriginal": "",
    #   "fecha": "27/06/2022 13:47:11",
    #   "selloDigital": "",
    #   "url": "https://servidor/eFirmaServicios/verificaFirmaCadena.do?verificar=ZhSsI%2FYUG9soc%2FkTfsWVvoUpylEwvoq%2F",
    #   "ip": "172.1.1.1",
    #   "huella": "Primer mensaje de prueba"

    # Convertir la respuesta del motor de firma a un diccionario
    texto = response.text.replace('"{', "{").replace('}"', "}")
    try:
        datos = json.loads(texto)
    except json.JSONDecodeError:
        mensaje = f"Error al autorizar el vale porque la respuesta no es JSON: {response.text}"
        fin_vale.autorizo_efirma_mensaje = mensaje
        fin_vale.estado = "ELIMINADO POR AUTORIZADOR"
        fin_vale.save()
        bitacora.error(mensaje)
        return set_task_error(mensaje)

    # Validar que se haya firmado correctamente
    if datos["success"] is False:
        mensaje = f"Error al autorizar el vale porque no se firmó correctamente: {response.text}"
        fin_vale.autorizo_efirma_mensaje = mensaje
        fin_vale.estado = "ELIMINADO POR AUTORIZADOR"
        fin_vale.save()
        bitacora.error(mensaje)
        return set_task_error(mensaje)

    # Actualizar el vale, ahora su estado es AUTORIZADO
    fin_vale.autorizo_efirma_tiempo = datetime.strptime(datos["fecha"], "%d/%m/%Y %H:%M:%S")
    fin_vale.autorizo_efirma_folio = datos["folio"]
    fin_vale.autorizo_efirma_selloDigital = datos["selloDigital"]
    fin_vale.autorizo_efirma_url = datos["url"]
    fin_vale.autorizo_efirma_qr_url = ""  # Pendiente
    fin_vale.estado = "AUTORIZADO"
    fin_vale.save()

    # Enviar un mensaje via correo electrónico al usuario para que vaya a recoger el vale

    # Terminar tarea
    mensaje_final = f"Vale {fin_vale_id} autorizado"
    set_task_progress(100)
    bitacora.info(mensaje_final)
    return mensaje_final


def cancelar_autorizar(fin_vale_id: int, contrasena: str):
    """Cancelar la firma electronica de un vale por quien autoriza"""

    # Validar configuracion
    if FIN_VALES_EFIRMA_CAN_FIRMA_CADENA_URL is None:
        mensaje = "Falta configurar FIN_VALES_EFIRMA_CAN_FIRMA_CADENA_URL"
        bitacora.error(mensaje)
        return set_task_error(mensaje)
    if FIN_VALES_EFIRMA_APP_ID is None:
        mensaje = "Falta configurar FIN_VALES_EFIRMA_APP_ID"
        bitacora.error(mensaje)
        return set_task_error(mensaje)
    if FIN_VALES_EFIRMA_APP_PASS is None:
        mensaje = "Falta configurar FIN_VALES_EFIRMA_APP_PASS"
        bitacora.error(mensaje)
        return set_task_error(mensaje)

    # Consultar el vale
    fin_vale = FinVale.query.get(fin_vale_id)
    if fin_vale is None:
        mensaje = f"No se encontró el vale {fin_vale_id}"
        bitacora.error(mensaje)
        return set_task_error(mensaje)
    if fin_vale.estatus != "A":
        mensaje = f"El vale {fin_vale_id} esta eliminado"
        bitacora.error(mensaje)
        return set_task_error(mensaje)
    if fin_vale.estado != "AUTORIZADO":
        mensaje = f"El vale {fin_vale_id} no está en estado AUTORIZADO"
        bitacora.error(mensaje)
        return set_task_error(mensaje)
    if fin_vale.solicito_efirma_folio is None:
        mensaje = f"El vale {fin_vale_id} no tiene folio de solicitud"
        bitacora.error(mensaje)
        return set_task_error(mensaje)

    # Consultar el usuario que autoriza
    autoriza = Usuario.query.filter_by(email=fin_vale.autorizo_email).first()
    if autoriza is None:
        mensaje = f"No se encontró el usuario {fin_vale.autorizo_email} que autoriza"
        bitacora.error(mensaje)
        return set_task_error(mensaje)
    if autoriza.efirma_registro_id is None or autoriza.efirma_registro_id == 0:
        mensaje = f"El usuario {fin_vale.autorizo_email} no tiene registro en el motor de firma"
        bitacora.error(mensaje)
        return set_task_error(mensaje)

    # Preparar los datos que se van a enviar al motor de firma
    data = {
        "idAplicacion": FIN_VALES_EFIRMA_APP_ID,
        "contrasenaAplicacion": FIN_VALES_EFIRMA_APP_PASS,
        "idRegistro": autoriza.efirma_registro_id,
        "contrasenaRegistro": contrasena,
        "folios": fin_vale.autorizo_efirma_folio,
    }

    # Enviar la solicitud al motor de firma
    try:
        response = requests.post(
            FIN_VALES_EFIRMA_CAN_FIRMA_CADENA_URL,
            data=data,
            verify=False,
        )
    except Exception as error:
        mensaje = f"Error al cancelar el vale autorizado: {error}"
        bitacora.error(mensaje)
        return set_task_error(mensaje)

    # Actualizar el vale, ahora su estado es CANCELADO POR AUTORIZADOR
    fin_vale.estado = "CANCELADO POR AUTORIZADOR"
    fin_vale.save()

    # Terminar tarea
    mensaje_final = f"Vale {fin_vale_id} cancelado su autorizacion"
    set_task_progress(100)
    bitacora.info(mensaje_final)
    return mensaje_final

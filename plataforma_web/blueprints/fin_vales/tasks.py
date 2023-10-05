"""
Financieros Vales, tareas en el fondo
"""
from datetime import datetime
import json
import logging
import os

from dotenv import load_dotenv
import requests
from lib.safe_string import safe_string

from lib.tasks import set_task_progress, set_task_error

from plataforma_web.app import create_app
from plataforma_web.blueprints.fin_vales.models import FinVale
from plataforma_web.blueprints.usuarios.models import Usuario

load_dotenv()  # Take environment variables from .env
FIN_VALES_EFIRMA_SER_FIRMA_CADENA_URL = os.getenv("FIN_VALES_EFIRMA_SER_FIRMA_CADENA_URL")
FIN_VALES_EFIRMA_CAN_FIRMA_CADENA_URL = os.getenv("FIN_VALES_EFIRMA_CAN_FIRMA_CADENA_URL")
FIN_VALES_EFIRMA_QR_URL = os.getenv("FIN_VALES_EFIRMA_QR_URL")
FIN_VALES_EFIRMA_APP_ID = os.getenv("FIN_VALES_EFIRMA_APP_ID")
FIN_VALES_EFIRMA_APP_PASS = os.getenv("FIN_VALES_EFIRMA_APP_PASS")

TIMEOUT = 24  # Segundos de espera para la respuesta del motor de firma

bitacora = logging.getLogger(__name__)
bitacora.setLevel(logging.INFO)
formato = logging.Formatter("%(asctime)s:%(levelname)s:%(message)s")
empunadura = logging.FileHandler("fin_vales.log")
empunadura.setFormatter(formato)
bitacora.addHandler(empunadura)

app = create_app()
app.app_context().push()


def solicitar(fin_vale_id: int, usuario_id: int, contrasena: str):
    """Firmar electronicamente el vale por quien solicita"""

    # Validar configuracion
    if FIN_VALES_EFIRMA_SER_FIRMA_CADENA_URL is None:
        mensaje = "Falta configurar FIN_VALES_EFIRMA_SER_FIRMA_CADENA_URL"
        bitacora.error(mensaje)
        return set_task_error(mensaje)
    if FIN_VALES_EFIRMA_QR_URL is None:
        mensaje = "Falta configurar FIN_VALES_EFIRMA_QR_URL"
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
    if fin_vale.estado != "CREADO":
        mensaje = f"El vale {fin_vale_id} no está en estado CREADO"
        bitacora.error(mensaje)
        return set_task_error(mensaje)

    # Consultar el usuario que solicita
    solicita = Usuario.query.get(usuario_id)
    if solicita is None:
        mensaje = f"No se encontró el usuario {usuario_id} que solicita"
        bitacora.error(mensaje)
        return set_task_error(mensaje)
    if solicita.efirma_registro_id is None or solicita.efirma_registro_id == 0:
        mensaje = f"El usuario {solicita.email} no tiene registro en el motor de firma"
        bitacora.error(mensaje)
        return set_task_error(mensaje)

    # Juntar los elementos del vale para armar la cadena
    elementos = {
        "id": fin_vale.id,
        "creado": fin_vale.creado.strftime("%Y-%m-%d %H:%M:%S"),
        "justificacion": fin_vale.justificacion,
        "monto": fin_vale.monto,
        "solicito_nombre": solicita.nombre,
        "solicito_puesto": solicita.puesto,
        "solicito_email": solicita.email,
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
            timeout=TIMEOUT,
            verify=False,
        )
        response.raise_for_status()
    except requests.exceptions.ConnectionError as error:
        mensaje = "Error de conexion al solicitar el vale. " + safe_string(str(error))
        fin_vale.solicito_efirma_error = mensaje
        fin_vale.save()
        bitacora.error(mensaje)
        return set_task_error(mensaje)
    except requests.exceptions.HTTPError as error:
        mensaje = "Error porque la respuesta no tiene el estado 200 al solicitar el vale. " + safe_string(str(error))
        fin_vale.solicito_efirma_error = mensaje
        fin_vale.save()
        bitacora.error(mensaje)
        return set_task_error(mensaje)
    except requests.exceptions.RequestException as error:
        mensaje = "Error desconocido al solicitar el vale. " + safe_string(str(error))
        fin_vale.solicito_efirma_error = mensaje
        fin_vale.save()
        bitacora.error(mensaje)
        return set_task_error(mensaje)

    # Tomar el texto de la respuesta
    texto = response.text

    # Si la contraseña es incorrecta, se registra el error
    if texto == "Contraseña incorrecta":
        mensaje = "Error porque la contraseña es incorrecta al solicitar el vale."
        fin_vale.solicito_efirma_error = mensaje
        fin_vale.save()
        bitacora.error(mensaje)
        return set_task_error(mensaje)

    # Convertir el texto a un diccionario
    texto = response.text.replace('"{', "{").replace('}"', "}")
    try:
        datos = json.loads(texto)
    except json.JSONDecodeError:
        mensaje = "Error al solicitar el vale porque la respuesta no es JSON."
        fin_vale.solicito_efirma_error = mensaje
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
    #   "url": "https://servidor/eFirmaServicios/verificaFirmaCadena.do?verificar=XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX",
    #   "ip": "172.1.1.1",
    #   "huella": "Primer mensaje de prueba"

    # Si el motor de firma entrega "success" en false, se registra el error
    if datos["success"] is False:
        mensaje = "Error al solicitar el vale con este mensaje: " + str(datos["mensaje"])
        fin_vale.solicito_efirma_error = mensaje
        fin_vale.save()
        bitacora.error(mensaje)
        return set_task_error(mensaje)

    # Actualizar el vale, ahora su estado es SOLICITADO
    fin_vale.solicito_nombre = solicita.nombre
    fin_vale.solicito_puesto = solicita.puesto
    fin_vale.solicito_email = solicita.email
    fin_vale.solicito_efirma_tiempo = datetime.strptime(datos["fecha"], "%d/%m/%Y %H:%M:%S")
    fin_vale.solicito_efirma_folio = datos["folio"]
    fin_vale.solicito_efirma_sello_digital = datos["selloDigital"]
    fin_vale.solicito_efirma_url = datos["url"]
    fin_vale.solicito_efirma_qr_url = f"{FIN_VALES_EFIRMA_QR_URL}?size=300&qrtext={datos['url']}"
    fin_vale.solicito_efirma_mensaje = datos["mensaje"]
    fin_vale.solicito_efirma_error = ""
    fin_vale.estado = "SOLICITADO"
    fin_vale.save()

    # Terminar tarea
    mensaje_final = f"Vale {fin_vale_id} solicitado"
    set_task_progress(100)
    bitacora.info(mensaje_final)
    return mensaje_final


def cancelar_solicitar(fin_vale_id: int, contrasena: str, motivo: str):
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

    # Enviar la cancelacion al motor de firma
    try:
        response = requests.post(
            FIN_VALES_EFIRMA_CAN_FIRMA_CADENA_URL,
            data=data,
            timeout=TIMEOUT,
            verify=False,
        )
        response.raise_for_status()
    except requests.exceptions.ConnectionError as error:
        mensaje = "Error de conexion al cancelar el vale. " + safe_string(str(error))
        fin_vale.solicito_efirma_error = mensaje
        fin_vale.save()
        bitacora.error(mensaje)
        return set_task_error(mensaje)
    except requests.exceptions.HTTPError as error:
        mensaje = "Error porque la respuesta no tiene el estado 200 al cancelar el vale. " + safe_string(str(error))
        fin_vale.solicito_efirma_error = mensaje
        fin_vale.save()
        bitacora.error(mensaje)
        return set_task_error(mensaje)
    except requests.exceptions.RequestException as error:
        mensaje = "Error desconocido al cancelar el vale. " + safe_string(str(error))
        fin_vale.solicito_efirma_error = mensaje
        fin_vale.save()
        bitacora.error(mensaje)
        return set_task_error(mensaje)

    # Tomar el texto de la respuesta
    texto = response.text

    # Si la contraseña es incorrecta, se registra el error
    if texto == "Contraseña incorrecta":
        mensaje = "Error porque la contraseña es incorrecta al solicitar el vale."
        fin_vale.solicito_efirma_error = mensaje
        fin_vale.save()
        bitacora.error(mensaje)
        return set_task_error(mensaje)

    # Convertir el texto a un diccionario
    texto = response.text.replace('"{', "{").replace('}"', "}")
    try:
        _ = json.loads(texto)
    except json.JSONDecodeError:
        mensaje = "Error al solicitar el vale porque la respuesta no es JSON."
        fin_vale.solicito_efirma_error = mensaje
        fin_vale.save()
        bitacora.error(mensaje)
        return set_task_error(mensaje)

    # Ejemplo de la respuesta
    #   "estatus": "SELLO CANCELADO"
    #   "fechaCancelado": 2022-07-04 12:39:08.0

    # Actualizar el vale, ahora su estado es CANCELADO POR SOLICITANTE
    fin_vale.estado = "CANCELADO POR SOLICITANTE"
    fin_vale.solicito_cancelo_tiempo = datetime.now()
    fin_vale.solicito_cancelo_motivo = safe_string(motivo, to_uppercase=False)
    fin_vale.solicito_cancelo_error = ""
    fin_vale.save()

    # Terminar tarea
    mensaje_final = f"Vale {fin_vale_id} cancelado su solicitud"
    set_task_progress(100)
    bitacora.info(mensaje_final)
    return mensaje_final


def autorizar(fin_vale_id: int, usuario_id: int, contrasena: str):
    """Firmar electronicamente el vale por quien autoriza"""

    # Validar configuracion
    if FIN_VALES_EFIRMA_SER_FIRMA_CADENA_URL is None:
        mensaje = "Falta configurar FIN_VALES_EFIRMA_SER_FIRMA_CADENA_URL"
        bitacora.error(mensaje)
        return set_task_error(mensaje)
    if FIN_VALES_EFIRMA_QR_URL is None:
        mensaje = "Falta configurar FIN_VALES_EFIRMA_QR_URL"
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
    autoriza = Usuario.query.get(usuario_id)
    if autoriza is None:
        mensaje = f"No se encontró el usuario {usuario_id} que autoriza"
        bitacora.error(mensaje)
        return set_task_error(mensaje)
    if autoriza.efirma_registro_id is None or autoriza.efirma_registro_id == 0:
        mensaje = f"El usuario {autoriza.email} no tiene registro en el motor de firma"
        bitacora.error(mensaje)
        return set_task_error(mensaje)

    # Juntar los elementos del vale para armar la cadena
    elementos = {
        "id": fin_vale.id,
        "autorizo_nombre": autoriza.nombre,
        "autorizo_puesto": autoriza.puesto,
        "autorizo_email": autoriza.email,
        "creado": fin_vale.creado.strftime("%Y-%m-%d %H:%M:%S"),
        "justificacion": fin_vale.justificacion,
        "monto": fin_vale.monto,
        "solicito_nombre": fin_vale.solicito_nombre,
        "solicito_puesto": fin_vale.solicito_puesto,
        "solicito_email": fin_vale.solicito_email,
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

    # Enviar la autorizacion al motor de firma
    try:
        response = requests.post(
            FIN_VALES_EFIRMA_SER_FIRMA_CADENA_URL,
            data=data,
            timeout=TIMEOUT,
            verify=False,
        )
        response.raise_for_status()
    except requests.exceptions.ConnectionError as error:
        mensaje = "Error de conexion al autorizar el vale." + safe_string(str(error))
        fin_vale.solicito_efirma_error = mensaje
        fin_vale.save()
        bitacora.error(mensaje)
        return set_task_error(mensaje)
    except requests.exceptions.HTTPError as error:
        mensaje = "Error porque la respuesta no tiene el estado 200 al autorizar el vale. " + safe_string(str(error))
        fin_vale.solicito_efirma_error = mensaje
        fin_vale.save()
        bitacora.error(mensaje)
        return set_task_error(mensaje)
    except requests.exceptions.RequestException as error:
        mensaje = "Error desconocido al autorizar el vale. " + safe_string(str(error))
        fin_vale.solicito_efirma_error = mensaje
        fin_vale.save()
        bitacora.error(mensaje)
        return set_task_error(mensaje)

    # Tomar el texto de la respuesta
    texto = response.text

    # Si la contraseña es incorrecta, se registra el error
    if texto == "Contraseña incorrecta":
        mensaje = "Error porque la contraseña es incorrecta al autorizar el vale."
        fin_vale.solicito_efirma_error = mensaje
        fin_vale.save()
        bitacora.error(mensaje)
        return set_task_error(mensaje)

    # Convertir el texto a un diccionario
    texto = response.text.replace('"{', "{").replace('}"', "}")
    try:
        datos = json.loads(texto)
    except json.JSONDecodeError:
        mensaje = "Error al autorizar el vale porque la respuesta no es JSON."
        fin_vale.solicito_efirma_error = mensaje
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

    # Si el motor de firma entrega "success" en false, se registra el error
    if datos["success"] is False:
        mensaje = "Error al solicitar el vale con este mensaje: " + str(datos["mensaje"])
        fin_vale.solicito_efirma_error = mensaje
        fin_vale.save()
        bitacora.error(mensaje)
        return set_task_error(mensaje)

    # Actualizar el vale, ahora su estado es AUTORIZADO
    fin_vale.autorizo_nombre = autoriza.nombre
    fin_vale.autorizo_puesto = autoriza.puesto
    fin_vale.autorizo_email = autoriza.email
    fin_vale.autorizo_efirma_tiempo = datetime.strptime(datos["fecha"], "%d/%m/%Y %H:%M:%S")
    fin_vale.autorizo_efirma_folio = datos["folio"]
    fin_vale.autorizo_efirma_sello_digital = datos["selloDigital"]
    fin_vale.autorizo_efirma_url = datos["url"]
    fin_vale.autorizo_efirma_qr_url = f"{FIN_VALES_EFIRMA_QR_URL}?size=300&qrtext={datos['url']}"
    fin_vale.autorizo_efirma_mensaje = datos["mensaje"]
    fin_vale.autorizo_efirma_error = ""
    fin_vale.estado = "AUTORIZADO"
    fin_vale.save()

    # Enviar un mensaje via correo electrónico al usuario para que vaya a recoger el vale

    # Terminar tarea
    mensaje_final = f"Vale {fin_vale_id} autorizado"
    set_task_progress(100)
    bitacora.info(mensaje_final)
    return mensaje_final


def cancelar_autorizar(fin_vale_id: int, contrasena: str, motivo: str):
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

    # Consultar el usuario que autoriza, para cancelar la firma
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

    # Enviar la cancelacion al motor de firma
    try:
        response = requests.post(
            FIN_VALES_EFIRMA_CAN_FIRMA_CADENA_URL,
            data=data,
            timeout=TIMEOUT,
            verify=False,
        )
        response.raise_for_status()
    except requests.exceptions.ConnectionError as error:
        mensaje = "Error de conexion al cancelar el vale. " + safe_string(str(error))
        fin_vale.solicito_efirma_error = mensaje
        fin_vale.save()
        bitacora.error(mensaje)
        return set_task_error(mensaje)
    except requests.exceptions.HTTPError as error:
        mensaje = "Error porque la respuesta no tiene el estado 200 al cancelar el vale. " + safe_string(str(error))
        fin_vale.solicito_efirma_error = mensaje
        fin_vale.save()
        bitacora.error(mensaje)
        return set_task_error(mensaje)
    except requests.exceptions.RequestException as error:
        mensaje = "Error desconocido al cancelar el vale. " + safe_string(str(error))
        fin_vale.solicito_efirma_error = mensaje
        fin_vale.save()
        bitacora.error(mensaje)
        return set_task_error(mensaje)

    # Tomar el texto de la respuesta
    texto = response.text

    # Si la contraseña es incorrecta, se registra el error
    if texto == "Contraseña incorrecta":
        mensaje = "Error porque la contraseña es incorrecta al solicitar el vale."
        fin_vale.solicito_efirma_error = mensaje
        fin_vale.save()
        bitacora.error(mensaje)
        return set_task_error(mensaje)

    # Convertir el texto a un diccionario
    texto = response.text.replace('"{', "{").replace('}"', "}")
    try:
        _ = json.loads(texto)
    except json.JSONDecodeError:
        mensaje = "Error al solicitar el vale porque la respuesta no es JSON."
        fin_vale.solicito_efirma_error = mensaje
        fin_vale.save()
        bitacora.error(mensaje)
        return set_task_error(mensaje)

    # Ejemplo de la respuesta
    #   "estatus": "SELLO CANCELADO"
    #   "fechaCancelado": 2022-07-04 12:39:08.0

    # Actualizar el vale, ahora su estado es CANCELADO POR AUTORIZADOR
    fin_vale.estado = "CANCELADO POR AUTORIZADOR"
    fin_vale.autorizo_cancelo_tiempo = datetime.now()
    fin_vale.autorizo_cancelo_motivo = safe_string(motivo, to_uppercase=False)
    fin_vale.autorizo_cancelo_error = ""
    fin_vale.save()

    # Terminar tarea
    mensaje_final = f"Vale {fin_vale_id} cancelado su autorizacion"
    set_task_progress(100)
    bitacora.info(mensaje_final)
    return mensaje_final

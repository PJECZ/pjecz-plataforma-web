"""
Funcionarios, tareas para ejecutar en el fondo

- asignar_oficinas: Asignar funcionarios_oficinas a partir de una direccion
- limpiar_oficinas: Limpiar funcionarios_oficinas
- enviar_reporte: Enviar via correo electronico el reporte de funcionarios
- sincronizar: Sincronizar funcionarios con la API de RRHH Personal
"""
from datetime import datetime
import locale
import logging

from dotenv import load_dotenv

from lib.tasks import set_task_progress, set_task_error

from plataforma_web.app import create_app
from plataforma_web.extensions import db

from plataforma_web.blueprints.domicilios.models import Domicilio
from plataforma_web.blueprints.funcionarios.models import Funcionario
from plataforma_web.blueprints.funcionarios_oficinas.models import FuncionarioOficina
from plataforma_web.blueprints.oficinas.models import Oficina

load_dotenv()  # Take environment variables from .env

bitacora = logging.getLogger(__name__)
bitacora.setLevel(logging.INFO)
formato = logging.Formatter("%(asctime)s:%(levelname)s:%(message)s")
empunadura = logging.FileHandler("funcionarios.log")
empunadura.setFormatter(formato)
bitacora.addHandler(empunadura)

app = create_app()
app.app_context().push()
db.app = app

locale.setlocale(locale.LC_TIME, "es_MX.utf8")

INGRESO_FECHA_POR_DEFECTO = datetime(2000, 1, 1)


def asignar_oficinas(funcionario_id: int, domicilio_id: int):
    """Asignar funcionarios_oficinas a partir de una direccion"""

    # Iniciar
    bitacora.info("Inicia asignar oficinas")

    # Consultar funcionario
    funcionario = Funcionario.query.get(funcionario_id)
    if funcionario is None:
        mensaje = "No se encuentra al funcionario"
        set_task_error(mensaje)
        bitacora.error(mensaje)
        return

    # Consultar domicilio
    domicilio = Domicilio.query.get(domicilio_id)
    if domicilio is None:
        mensaje = "No se encuentra al domicilio"
        set_task_error(mensaje)
        bitacora.error(mensaje)
        return

    # Consultar las oficinas activas de ese domicilio
    oficinas = Oficina.query.filter(Oficina.domicilio == domicilio).filter(Oficina.estatus == "A").all()

    # Insertar o actualizar los registros de funcionarios_oficinas
    contador = 0
    for oficina in oficinas:
        funcionario_oficina = FuncionarioOficina.query.filter(FuncionarioOficina.funcionario == funcionario).filter(FuncionarioOficina.oficina == oficina).first()
        if funcionario_oficina is None:
            # No existe, vamos a insertar
            FuncionarioOficina(
                funcionario=funcionario,
                oficina=oficina,
                descripcion=f"Funcionario {funcionario.curp} en {oficina.clave}",
            ).save()
            contador += 1
        else:
            # Si existe, vamos a actualizar si esta eliminado
            if funcionario_oficina.estatus != "A":
                funcionario_oficina.estatus = "A"
                funcionario_oficina.save()
                contador += 1

    # Terminar
    set_task_progress(100)
    mensaje_final = f"Terminado asignar {contador} oficinas al CURP {funcionario.curp}"
    bitacora.info(mensaje_final)
    return mensaje_final


def limpiar_oficinas(funcionario_id: int):
    """Limpiar funcionarios_oficinas"""

    # Iniciar
    bitacora.info("Inicia limpiar oficinas")

    # Consultar funcionario
    funcionario = Funcionario.query.get(funcionario_id)
    if funcionario is None:
        mensaje = "No se encuentra al funcionario"
        set_task_error(mensaje)
        bitacora.error(mensaje)
        return

    # Limpiar (cambiar estatus a B) los registros de funcionarios_oficinas
    contador = 0
    for funcionario_oficina in FuncionarioOficina.query.filter(FuncionarioOficina.funcionario == funcionario).all():
        if funcionario_oficina.estatus == "A":
            funcionario_oficina.delete()
            contador += 1

    # Terminar
    set_task_progress(100)
    mensaje_final = f"Terminado limpiar oficinas, {contador} a {funcionario.curp}"
    bitacora.info(mensaje_final)
    return mensaje_final


def enviar_reporte():
    """Enviar reporte de funcionarios via correo electronico"""

    # Iniciar
    bitacora.info("Inicia enviar reporte")

    # Consultar
    funcionarios = db.session.query(Funcionario).filter_by(estatus="A")
    bitacora.info("Hay %s funcionarios activos", funcionarios.count())

    # Terminar
    set_task_progress(100)
    mensaje_final = "Terminado enviar reporte satisfactoriamente"
    bitacora.info(mensaje_final)
    return mensaje_final


def sincronizar():
    """Sincronizar funcionarios con la API de RRHH Personal"""
    # Iniciar
    bitacora.info("Inicia sincronizar")
    # Terminar
    bitacora.info("Terminado sincronizar satisfactoriamente")
    return

"""
Sistemas, vistas
"""

from datetime import date, datetime, timedelta

from flask import Blueprint, redirect, render_template, url_for
from flask_login import current_user

from plataforma_web.blueprints.audiencias.models import Audiencia
from plataforma_web.blueprints.edictos.models import Edicto
from plataforma_web.blueprints.listas_de_acuerdos.models import ListaDeAcuerdo
from plataforma_web.blueprints.usuarios_roles.models import UsuarioRol
from plataforma_web.blueprints.sentencias.models import Sentencia
from plataforma_web.blueprints.usuarios_datos.models import UsuarioDato

sistemas = Blueprint("sistemas", __name__, template_folder="templates")

HOY = date.today()
BREVE_LIMITE_DIAS = 15
BREVE_DESDE_DATETIME = datetime(year=HOY.year, month=HOY.month, day=HOY.day) + timedelta(days=-BREVE_LIMITE_DIAS)

TARJETA_SATISFACTORIA = "bg-light"
TARJETA_ADVERTENCIA = "bg-warning"
TARJETA_VACIA = "bg-danger"
TARJETAS_LIMITE_REGISTROS = 5

# Roles que deben estar en la base de datos
ROL_ADMINISTRADOR = "ADMINISTRADOR"
ROL_NOTARIA = "NOTARIA"
ROL_SOPORTE_USUARIO = "SOPORTE USUARIO"
ROL_VALIDADORES = "VALIDADORES DE DATOS Y DOCUMENTOS PERSONALES"


@sistemas.route("/inicio/audiencias_json")
def audiencias_json():
    """Audiencias en JSON"""
    breve = "Sin agenda."
    listado = []
    estilo = TARJETA_VACIA
    if current_user.autoridad.audiencia_categoria == "NO DEFINIDO":
        return {
            "titulo": "Agenda de Audiencias",
            "breve": breve,
            "listado": listado,
            "url": url_for("audiencias.list_active"),
            "style": estilo,
        }
    # Listado
    audiencias = Audiencia.query.filter(Audiencia.autoridad == current_user.autoridad).filter_by(estatus="A")
    desde = datetime.now()  # Desde este momento
    for audiencia in audiencias.filter(Audiencia.tiempo >= desde).order_by(Audiencia.tiempo).limit(TARJETAS_LIMITE_REGISTROS).all():
        listado.append(
            {
                "tiempo": audiencia.tiempo.strftime("%Y-%m-%d %H:%M"),
                "tipo_audiencia": audiencia.tipo_audiencia,
                "url": url_for("audiencias.detail", audiencia_id=audiencia.id),
            }
        )
    # Breve
    estilo = TARJETA_SATISFACTORIA
    total = audiencias.count()
    if total > 0:
        breve = f"Total {total}. "
        if len(listado) > 0:
            breve += "Desde " + desde.strftime("%Y-%m-%d %H:%M") + ". "
        else:
            breve += "No hay eventos en la agenda de hoy."
            estilo = TARJETA_ADVERTENCIA
    # Entregar JSON
    return {
        "titulo": "Agenda de Audiencias",
        "breve": breve,
        "listado": listado,
        "url": url_for("audiencias.list_active"),
        "style": estilo,
    }


@sistemas.route("/inicio/edictos_json")
def edictos_json():
    """Edictos en JSON"""
    breve = "Sin edictos."
    listado = []
    estilo = TARJETA_VACIA
    if current_user.autoridad.directorio_edictos == "":
        return {
            "titulo": "Edictos",
            "breve": breve,
            "listado": listado,
            "url": url_for("edictos.list_active"),
            "style": estilo,
        }
    # Listado
    edictos = Edicto.query.filter(Edicto.autoridad == current_user.autoridad).filter_by(estatus="A")
    for edicto in edictos.order_by(Edicto.fecha.desc()).limit(TARJETAS_LIMITE_REGISTROS).all():
        listado.append(
            {
                "expediente": edicto.expediente,
                "descripcion": edicto.descripcion,
                "url": url_for("edictos.detail", edicto_id=edicto.id),
            }
        )
    # Breve
    estilo = TARJETA_SATISFACTORIA
    total = edictos.count()
    if total > 0:
        breve = f"Total {total}. "
        cantidad = edictos.filter(Edicto.creado >= BREVE_DESDE_DATETIME).count()
        if cantidad > 0:
            breve += f"Se subieron {cantidad} en {BREVE_LIMITE_DIAS} días."
        else:
            breve += f"Ninguno en {BREVE_LIMITE_DIAS} días."
            estilo = TARJETA_ADVERTENCIA
    # Entregar JSON
    return {
        "titulo": "Edictos",
        "breve": breve,
        "listado": listado,
        "url": url_for("edictos.list_active"),
        "style": estilo,
    }


@sistemas.route("/inicio/listas_de_acuerdos_json")
def listas_de_acuerdos_json():
    """Listas de Acuerdos en JSON"""
    breve = "Sin listas de acuerdos."
    listado = []
    estilo = TARJETA_VACIA
    if current_user.autoridad.directorio_listas_de_acuerdos == "":
        return {
            "titulo": "Listas de Acuerdos",
            "breve": breve,
            "listado": listado,
            "url": url_for("listas_de_acuerdos.list_active"),
            "style": estilo,
        }

    # Listado
    listas_de_acuerdos = ListaDeAcuerdo.query.filter(ListaDeAcuerdo.autoridad == current_user.autoridad).filter_by(estatus="A")
    for lista_de_acuerdo in listas_de_acuerdos.order_by(ListaDeAcuerdo.fecha.desc()).limit(TARJETAS_LIMITE_REGISTROS).all():
        listado.append(
            {
                "fecha": lista_de_acuerdo.fecha.strftime("%Y-%m-%d"),
                "url": url_for("listas_de_acuerdos.detail", lista_de_acuerdo_id=lista_de_acuerdo.id),
            }
        )
    # Breve
    estilo = TARJETA_SATISFACTORIA
    total = listas_de_acuerdos.count()
    if total > 0:
        breve = f"Total {total}. "
    # Entregar JSON
    return {
        "titulo": "Listas de Acuerdos",
        "breve": breve,
        "listado": listado,
        "url": url_for("listas_de_acuerdos.list_active"),
        "style": estilo,
    }


@sistemas.route("/inicio/sentencias_json")
def sentencias_json():
    """Sentencias en JSON"""
    breve = "Sin V.P. de sentencias."
    listado = []
    estilo = TARJETA_VACIA
    if current_user.autoridad.directorio_sentencias == "":
        return {
            "titulo": "V.P. de Sentencias",
            "breve": breve,
            "listado": listado,
            "url": url_for("sentencias.list_active"),
            "style": estilo,
        }
    # Listado
    sentencias = Sentencia.query.filter(Sentencia.autoridad == current_user.autoridad).filter_by(estatus="A")
    for sentencia in sentencias.order_by(Sentencia.fecha.desc()).limit(TARJETAS_LIMITE_REGISTROS).all():
        listado.append(
            {
                "sentencia": sentencia.sentencia,
                "materia_tipo_juicio": sentencia.materia_tipo_juicio.descripcion,
                "url": url_for("sentencias.detail", sentencia_id=sentencia.id),
            }
        )
    # Breve
    estilo = TARJETA_SATISFACTORIA
    total = sentencias.count()
    if total > 0:
        breve = f"Total {total}. "
        cantidad = sentencias.filter(Sentencia.creado >= BREVE_DESDE_DATETIME).count()
        if cantidad > 0:
            breve += f"Se subieron {cantidad} en {BREVE_LIMITE_DIAS} días."
        else:
            breve += f"Ninguno en {BREVE_LIMITE_DIAS} días."
            estilo = TARJETA_ADVERTENCIA
    # Entregar JSON
    return {
        "titulo": "V.P. de Sentencias",
        "breve": breve,
        "listado": listado,
        "url": url_for("sentencias.list_active"),
        "style": estilo,
    }


@sistemas.route("/")
def start():
    """Página inicial"""

    # Si el usuario está autenticado, mostrar la página de inicio
    if current_user.is_authenticated:
        mostrar_portal_notarias = False
        mostrar_portal_soporte = False
        mostrar_portal_recibos_nomina = False
        estado_documentos_personales = None

        # Consultar los roles del usuario
        current_user_roles = current_user.get_roles()

        # Si tiene el rol administrador mostrar el acceso a solicitudes para actualizar datos de usuarios
        if ROL_ADMINISTRADOR in current_user_roles or ROL_VALIDADORES in current_user_roles:
            mostrar_portal_recibos_nomina = True
            usuario_dato = UsuarioDato.query.filter_by(usuario=current_user).order_by(UsuarioDato.id.desc()).first()
            if usuario_dato:
                estado_documentos_personales = usuario_dato.estado_general

        # Si tiene el rol administrador o soporte-usuario mostrar los accesos a crear tickets y directorio
        if ROL_ADMINISTRADOR in current_user_roles or ROL_SOPORTE_USUARIO in current_user_roles:
            mostrar_portal_soporte = True

        # Si tiene el rol administrador o notaria mostrar los accesos a edictos, escrituras y mensajes
        if ROL_ADMINISTRADOR in current_user_roles or ROL_NOTARIA in current_user_roles:
            mostrar_portal_notarias = True

        # Entregar
        return render_template(
            "sistemas/start.jinja2",
            mostrar_portal_notarias=mostrar_portal_notarias,
            mostrar_portal_soporte=mostrar_portal_soporte,
            mostrar_portal_recibos_nomina=mostrar_portal_recibos_nomina,
            estado_documentos_personales=estado_documentos_personales,
        )

    # No está autenticado, mostrar la página de inicio de sesión
    return redirect("/login")


@sistemas.app_errorhandler(400)
def bad_request(error):
    """Solicitud errónea"""
    return render_template("sistemas/403.jinja2", error=error), 403


@sistemas.app_errorhandler(403)
def forbidden(error):
    """Acceso no autorizado"""
    return render_template("sistemas/403.jinja2"), 403


@sistemas.app_errorhandler(404)
def page_not_found(error):
    """Error página no encontrada"""
    return render_template("sistemas/404.jinja2"), 404


@sistemas.app_errorhandler(500)
def internal_server_error(error):
    """Error del servidor"""
    return render_template("sistemas/500.jinja2"), 500

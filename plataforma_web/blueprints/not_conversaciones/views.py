"""
Mensajes, vistas
"""
import json
import datetime

from flask import Blueprint, flash, redirect, render_template, url_for, request
from flask_login import current_user, login_required
from sqlalchemy import and_, or_

from lib.datatables import get_datatable_parameters, output_datatable_json
from lib.safe_string import safe_string
from plataforma_web.blueprints.usuarios.decorators import permission_required
from plataforma_web.extensions import db

from plataforma_web.blueprints.permisos.models import Permiso
from plataforma_web.blueprints.not_conversaciones.models import NotConversacion
from plataforma_web.blueprints.not_mensajes.models import NotMensaje
from plataforma_web.blueprints.not_conversaciones.forms import NotConversacionNewForm
from plataforma_web.blueprints.autoridades.models import Autoridad

MODULO = "NOT CONVERSACIONES"

not_conversaciones = Blueprint("not_conversaciones", __name__, template_folder="templates")


@not_conversaciones.before_request
@login_required
@permission_required(MODULO, Permiso.VER)
def before_request():
    """Permiso por defecto"""


@not_conversaciones.route("/not_conversaciones/conversaciones/datatable_json_conversaciones", methods=["GET", "POST"])
def datatable_json_conversaciones():
    """DataTable JSON para listado de Conversaciones"""
    # Tomar parámetros de Datatables
    draw, start, rows_per_page = get_datatable_parameters()
    # Consultar
    consulta = db.session.query(NotConversacion, NotMensaje).join(NotMensaje, NotConversacion.ultimo_mensaje_id == NotMensaje.id)
    if "estatus" in request.form:
        consulta = consulta.filter(NotConversacion.estatus == request.form["estatus"])
    else:
        consulta = consulta.filter(NotConversacion.estatus == "A")
    if "estado" in request.form:
        consulta = consulta.filter(NotConversacion.estado == request.form["estado"])
    if current_user.can_admin(MODULO) == False:
        consulta = consulta.filter(or_(NotConversacion.autor == current_user.autoridad, NotConversacion.destinatario == current_user.autoridad))

    registros = consulta.order_by(NotConversacion.modificado.desc()).order_by(NotConversacion.leido.desc()).offset(start).limit(rows_per_page).all()
    total = consulta.count()
    # Elaborar datos para DataTable
    data = []
    for resultado in registros:
        data.append(
            {
                "detalle": {
                    "clave": resultado.NotConversacion.autor.clave if resultado.NotConversacion.destinatario == current_user.autoridad else resultado.NotConversacion.destinatario.clave,
                    "url": url_for("autoridades.detail", autoridad_id=resultado.NotConversacion.autor_id if resultado.NotConversacion.destinatario == current_user.autoridad else resultado.NotConversacion.destinatario.id),
                },
                "lectura": {
                    "estado": True if current_user.autoridad_id == resultado.NotMensaje.autoridad_id else resultado.NotConversacion.leido,
                    "cantidad": 5,
                },
                "fecha_hora": resultado.NotConversacion.modificado.strftime("%Y/%m/%d %H:%M"),
                "mensaje": {
                    "mensaje": resultado.NotMensaje.contenido,
                    "url": url_for("not_conversaciones.detail", conversacion_id=resultado.NotConversacion.id),
                },
            }
        )
    # Entregar JSON
    return output_datatable_json(draw, total, data)


@not_conversaciones.route("/not_conversaciones")
def list_active():
    """Listado de Conversaciones Activas"""
    return render_template(
        "not_conversaciones/list.jinja2",
        filtros=json.dumps({"estatus": "A", "estado": "ACTIVO"}),
        titulo="Conversaciones",
        tipo=current_user_juzgado_notaria(),
        estatus="A",
        estado="ACTIVO",
    )


@not_conversaciones.route("/not_conversaciones/archivadas")
def list_archive():
    """Listado de Conversaciones Archivadas"""
    return render_template(
        "not_conversaciones/list.jinja2",
        filtros=json.dumps({"estatus": "A", "estado": "ARCHIVADO"}),
        titulo="Conversaciones Archivadas",
        tipo=current_user_juzgado_notaria(),
        estatus="A",
        estado="ARCHIVADO",
    )


@not_conversaciones.route("/not_conversaciones/<int:conversacion_id>")
def detail(conversacion_id):
    """Detalle de una Conversación"""
    conversacion = NotConversacion.query.get_or_404(conversacion_id)
    if current_user.can_admin(MODULO) == False:
        if conversacion.autor_id != current_user.autoridad_id and conversacion.destinatario_id != current_user.autoridad_id:
            flash("No tiene persmisos para ver esta conversación", "danger")
            return redirect(url_for("not_conversaciones.list_active"))
    if conversacion.leido is False:
        ultimo_mensaje = NotMensaje.query.get_or_404(conversacion.ultimo_mensaje_id)
        if ultimo_mensaje.autoridad_id != current_user.autoridad_id:
            ultimo_mensaje.leido = True
            ultimo_mensaje.save()
            conversacion.leido = True
            conversacion.save()
    mensajes = NotMensaje.query.filter_by(estatus="A").filter_by(not_conversacion=conversacion).order_by(NotMensaje.creado).all()
    fecha_mensaje_anterior = None
    fechas = {}
    for mensaje in mensajes:
        if fecha_mensaje_anterior is None:
            fecha_mensaje_anterior = mensaje.creado.strftime("%Y/%m/%d")
            fechas[mensaje] = mensaje.creado.strftime("%Y/%m/%d")
        else:
            if fecha_mensaje_anterior == mensaje.creado.strftime("%Y/%m/%d"):
                fechas[mensaje] = None
            else:
                fechas[mensaje] = mensaje.creado.strftime("%Y/%m/%d")
                fecha_mensaje_anterior = mensaje.creado.strftime("%Y/%m/%d")
        if fechas[mensaje] == datetime.date.today().strftime("%Y/%m/%d"):
            fechas[mensaje] = "Hoy"
        elif fechas[mensaje] == (datetime.date.today() - datetime.timedelta(days=1)).strftime("%Y/%m/%d"):
            fechas[mensaje] = "Ayer"

    return render_template(
        "not_conversaciones/detail.jinja2",
        conversacion=conversacion,
        titulo="Conversación",
        tipo=current_user_juzgado_notaria(),
        mensajes=mensajes,
        fechas=fechas,
    )


def current_user_juzgado_notaria():
    """Verifica si el usuario actual es juzgado o notaría"""
    if current_user.autoridad.es_notaria:
        return "NOTARIA"
    if current_user.autoridad.es_jurisdiccional:
        return "JUZGADO"
    return None


@not_conversaciones.route("/not_conversaciones/nueva", methods=["GET", "POST"])
@permission_required(MODULO, Permiso.CREAR)
def new():
    """Nueva Conversación"""
    form = NotConversacionNewForm()
    if form.validate_on_submit():
        destinatario = Autoridad.query.get_or_404(form.destinatario.data)
        conversacion = NotConversacion(
            autor=current_user.autoridad,
            destinatario=destinatario,
            leido=False,
            estado="ACTIVO",
            ultimo_mensaje_id=0,
        )
        conversacion.save()
        mensaje = NotMensaje(
            autoridad=current_user.autoridad,
            not_conversacion=conversacion,
            contenido=safe_string(form.mensaje.data),
            leido=False,
        )
        mensaje.save()
        conversacion.ultimo_mensaje_id = mensaje.id
        conversacion.save()
        flash("Conversacion creada correctamente.", "success")
        return redirect(url_for("not_conversaciones.list_active"))
    form.autor.data = current_user.nombre
    tipo = "NOTARIA" if current_user_juzgado_notaria() == "JUZGADO" else "JUZGADO"
    return render_template("not_conversaciones/new.jinja2", tipo=tipo, form=form)


@not_conversaciones.route("/not_conversaciones/nuevo_mensaje/<int:conversacion_id>", methods=["GET", "POST"])
def new_message(conversacion_id):
    """Nuevo Mensaje"""
    contenido = safe_string(request.form["contenido"])
    if contenido:
        conversacion = NotConversacion.query.get_or_404(conversacion_id)
        if conversacion.autor != current_user.autoridad and conversacion.destinatario != current_user.autoridad:
            flash("No tiene permitido escribir en esta conversación", "danger")
            return redirect(url_for("not_conversaciones.list_active"))
        elif conversacion.estado != "ACTIVO":
            flash("Esta conversación no está activa", "warning")
            return redirect(url_for("not_conversaciones.list_active"))
        else:
            mensaje = NotMensaje(
                autoridad=current_user.autoridad,
                not_conversacion=conversacion,
                contenido=contenido,
                leido=False,
            )
            mensaje.save()
            conversacion.leido = False
            conversacion.ultimo_mensaje_id = mensaje.id
            conversacion.save()
    else:
        flash("Escriba algo en el mensaje", "warning")
    return redirect(url_for("not_conversaciones.detail", conversacion_id=conversacion_id))


@not_conversaciones.route("/not_conversaciones/archivar/<int:conversacion_id>")
def archive(conversacion_id):
    """Archivar conversación"""
    conversacion = NotConversacion.query.get_or_404(conversacion_id)
    if current_user_juzgado_notaria() != "JUZGADO" or conversacion.autor != current_user.autoridad and conversacion.destinatario != current_user.autoridad:
        flash("No tiene permitido Archivar esta conversación", "danger")
        return redirect(url_for("not_conversaciones.list_active"))
    conversacion.leido = True
    conversacion.estado = "ARCHIVADO"
    conversacion.save()
    flash("Conversación Archivada correctamente.", "success")
    return redirect(url_for("not_conversaciones.list_active"))

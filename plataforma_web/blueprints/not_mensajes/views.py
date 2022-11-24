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
from plataforma_web.blueprints.not_mensajes.models import NotMsgConversacion, NotMsgMensaje
from plataforma_web.blueprints.not_mensajes.forms import NotMsgConversacionNewForm
from plataforma_web.blueprints.autoridades.models import Autoridad

MODULO = "NOT MENSAJES"

not_mensajes = Blueprint("not_mensajes", __name__, template_folder="templates")


@not_mensajes.before_request
@login_required
@permission_required(MODULO, Permiso.VER)
def before_request():
    """Permiso por defecto"""


@not_mensajes.route("/not_mensajes/conversaciones/datatable_json_conversaciones", methods=["GET", "POST"])
def datatable_json_conversaciones():
    """DataTable JSON para listado de Conversaciones"""
    # Tomar parámetros de Datatables
    draw, start, rows_per_page = get_datatable_parameters()
    # Consultar
    consulta = db.session.query(NotMsgConversacion, NotMsgMensaje).join(NotMsgMensaje, NotMsgConversacion.ultimo_mensaje_id == NotMsgMensaje.id)
    if "estatus" in request.form:
        consulta = consulta.filter(NotMsgConversacion.estatus == request.form["estatus"])
    else:
        consulta = consulta.filter(NotMsgConversacion.estatus == "A")
    if "estado" in request.form:
        consulta = consulta.filter(NotMsgConversacion.estado == request.form["estado"])
    if current_user.can_admin(MODULO) == False:
        consulta = consulta.filter(or_(NotMsgConversacion.autor == current_user.autoridad, NotMsgConversacion.destinatario == current_user.autoridad))

    registros = consulta.order_by(NotMsgConversacion.modificado.desc()).order_by(NotMsgConversacion.leido.desc()).offset(start).limit(rows_per_page).all()
    total = consulta.count()
    # Elaborar datos para DataTable
    data = []
    for resultado in registros:
        data.append(
            {
                "detalle": {
                    "clave": resultado.NotMsgConversacion.autor.clave if resultado.NotMsgConversacion.destinatario == current_user.autoridad else resultado.NotMsgConversacion.destinatario.clave,
                    "url": url_for("autoridades.detail", autoridad_id=resultado.NotMsgConversacion.autor_id if resultado.NotMsgConversacion.destinatario == current_user.autoridad else resultado.NotMsgConversacion.destinatario.id),
                },
                "lectura": {
                    "estado": True if current_user.autoridad_id == resultado.NotMsgMensaje.autoridad_id else resultado.NotMsgConversacion.leido,
                    "cantidad": 5,
                },
                "fecha_hora": resultado.NotMsgConversacion.modificado.strftime("%Y/%m/%d %H:%M"),
                "mensaje": {
                    "mensaje": resultado.NotMsgMensaje.contenido,
                    "url": url_for("not_mensajes.detail", conversacion_id=resultado.NotMsgConversacion.id),
                },
            }
        )
    # Entregar JSON
    return output_datatable_json(draw, total, data)


@not_mensajes.route("/not_mensajes")
def list_active():
    """Listado de Conversaciones Activas"""
    return render_template(
        "not_mensajes/list.jinja2",
        filtros=json.dumps({"estatus": "A", "estado": "ACTIVO"}),
        titulo="Conversaciones",
        tipo=current_user_juzgado_notaria(),
        estatus="A",
        estado="ACTIVO",
    )


@not_mensajes.route("/not_mensajes/archivadas")
def list_archive():
    """Listado de Conversaciones Archivadas"""
    if current_user.can_admin(MODULO) == False and current_user_juzgado_notaria() != "JUZGADO":
        return redirect(url_for("not_mensajes.list_active"))

    return render_template(
        "not_mensajes/list.jinja2",
        filtros=json.dumps({"estatus": "A", "estado": "ARCHIVADO"}),
        titulo="Conversaciones Archivadas",
        tipo=current_user_juzgado_notaria(),
        estatus="A",
        estado="ARCHIVADO",
    )


@not_mensajes.route("/not_mensajes/<int:conversacion_id>")
def detail(conversacion_id):
    """Detalle de una Conversación"""
    conversacion = NotMsgConversacion.query.get_or_404(conversacion_id)
    if current_user.can_admin(MODULO) == False:
        if conversacion.autor_id != current_user.autoridad_id and conversacion.destinatario_id != current_user.autoridad_id:
            flash("No tiene persmisos para ver esta conversación", "danger")
            return redirect(url_for("not_mensajes.list_active"))
    if conversacion.leido is False:
        ultimo_mensaje = NotMsgMensaje.query.get_or_404(conversacion.ultimo_mensaje_id)
        if ultimo_mensaje.autoridad_id != current_user.autoridad_id:
            ultimo_mensaje.leido = True
            ultimo_mensaje.save()
            conversacion.leido = True
            conversacion.save()
    mensajes = NotMsgMensaje.query.filter_by(estatus="A").filter_by(not_msg_conversacion=conversacion).order_by(NotMsgMensaje.creado).all()
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
        "not_mensajes/detail.jinja2",
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


@not_mensajes.route("/not_mensajes/nueva", methods=["GET", "POST"])
@permission_required(MODULO, Permiso.CREAR)
def new():
    """Nueva Conversación"""
    form = NotMsgConversacionNewForm()
    if form.validate_on_submit():
        destinatario = Autoridad.query.get_or_404(form.destinatario.data)
        conversacion = NotMsgConversacion(
            autor=current_user.autoridad,
            destinatario=destinatario,
            leido=False,
            estado="ACTIVO",
            ultimo_mensaje_id=0,
        )
        conversacion.save()
        mensaje = NotMsgMensaje(
            autoridad=current_user.autoridad,
            not_msg_conversacion=conversacion,
            contenido=safe_string(form.mensaje.data),
            leido=False,
        )
        mensaje.save()
        conversacion.ultimo_mensaje_id = mensaje.id
        conversacion.save()
        flash("Conversacion creada correctamente.", "success")
        return redirect(url_for("not_mensajes.list_active"))
    form.autor.data = current_user.nombre
    tipo = "NOTARIA" if current_user_juzgado_notaria() == "JUZGADO" else "JUZGADO"
    return render_template("not_mensajes/new.jinja2", tipo=tipo, form=form)


@not_mensajes.route("/not_mensajes/nuevo_mensaje/<int:conversacion_id>", methods=["GET", "POST"])
def new_message(conversacion_id):
    """Nuevo Mensaje"""
    contenido = safe_string(request.form["contenido"])
    if contenido:
        conversacion = NotMsgConversacion.query.get_or_404(conversacion_id)
        if conversacion.autor != current_user.autoridad and conversacion.destinatario != current_user.autoridad:
            flash("No tiene permitido escribir en esta conversación", "danger")
            return redirect(url_for("not_mensajes.list_active"))
        elif conversacion.estado != "ACTIVO":
            flash("Esta conversación no está activa", "warning")
            return redirect(url_for("not_mensajes.list_active"))
        else:
            mensaje = NotMsgMensaje(
                autoridad=current_user.autoridad,
                not_msg_conversacion=conversacion,
                contenido=contenido,
                leido=False,
            )
            mensaje.save()
            conversacion.leido = False
            conversacion.ultimo_mensaje_id = mensaje.id
            conversacion.save()
    else:
        flash("Escriba algo en el mensaje", "warning")
    return redirect(url_for("not_mensajes.detail", conversacion_id=conversacion_id))


@not_mensajes.route("/not_mensajes/archivar/<int:conversacion_id>")
def archive(conversacion_id):
    """Archivar conversación"""
    conversacion = NotMsgConversacion.query.get_or_404(conversacion_id)
    if current_user_juzgado_notaria() != "JUZGADO" or conversacion.autor != current_user.autoridad and conversacion.destinatario != current_user.autoridad:
        flash("No tiene permitido Archivar esta conversación", "danger")
        return redirect(url_for("not_mensajes.list_active"))
    conversacion.leido = True
    conversacion.estado = "ARCHIVADO"
    conversacion.save()
    flash("Conversación Archivada correctamente.", "success")
    return redirect(url_for("not_mensajes.list_active"))

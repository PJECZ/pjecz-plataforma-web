"""
Mensajes, vistas
"""
from flask import Blueprint, flash, redirect, render_template, url_for
from flask_login import current_user, login_required
from sqlalchemy import or_

from lib.safe_string import safe_string
from plataforma_web.blueprints.usuarios.decorators import permission_required
from plataforma_web.extensions import db

from plataforma_web.blueprints.permisos.models import Permiso
from plataforma_web.blueprints.mensajes.models import Mensaje, MensajeRespuesta
from plataforma_web.blueprints.mensajes.forms import MensajeForm, MensajeRespuestaForm
from plataforma_web.blueprints.usuarios.models import Usuario

MODULO = "MENSAJES"

mensajes = Blueprint("mensajes", __name__, template_folder="templates")


@mensajes.before_request
@login_required
@permission_required(MODULO, Permiso.VER)
def before_request():
    """Permiso por defecto"""


@mensajes.route("/mensajes")
def list_active():
    """Listado de Mensajes activos"""
    nuevos_mensajes = Mensaje.query.filter(Mensaje.estatus == "A").filter(Mensaje.leido == False).filter(Mensaje.destinatario == current_user).all()
    respuestas = db.session.query(Mensaje, MensajeRespuesta).filter(MensajeRespuesta.estatus == "A").filter(MensajeRespuesta.leido == False).filter(Mensaje.autor == current_user.email).filter(Mensaje.id == MensajeRespuesta.respuesta_id).all()
    viejos_mensajes = Mensaje.query.filter(Mensaje.estatus == "A").filter(Mensaje.leido == True).filter(or_(Mensaje.destinatario_id == current_user.id, Mensaje.autor == current_user.email)).order_by(Mensaje.creado.desc()).limit(500).all()
    return render_template(
        "mensajes/list.jinja2",
        nuevos=nuevos_mensajes,
        respuestas=respuestas,
        viejos=viejos_mensajes,
        titulo="Mensajes",
        estatus="A",
    )


@mensajes.route("/mensajes/inactivos")
@permission_required(MODULO, Permiso.MODIFICAR)
def list_inactive():
    """Listado de Mensajes inactivos"""
    nuevos_mensajes = Mensaje.query.filter(Mensaje.estatus == "B").filter(Mensaje.leido == False).all()
    respuestas = MensajeRespuesta.query.filter(MensajeRespuesta.estatus == "B").filter(MensajeRespuesta.leido == False).all()
    viejos_mensajes = Mensaje.query.filter(Mensaje.estatus == "B").filter(Mensaje.leido == True).limit(500).all()
    return render_template(
        "mensajes/list.jinja2",
        nuevos=nuevos_mensajes,
        respuestas=respuestas,
        viejos=viejos_mensajes,
        titulo="Mensajes inactivos",
        estatus="B",
    )


@mensajes.route("/mensajes/<int:mensaje_id>")
def detail(mensaje_id):
    """Detalle de un Mensajes"""
    mensaje = Mensaje.query.get_or_404(mensaje_id)
    if mensaje.leido is False:
        mensaje.leido = True
        mensaje.save()
    respuestas = MensajeRespuesta.query.filter(MensajeRespuesta.estatus == "A").filter(MensajeRespuesta.respuesta_id == mensaje_id).all()
    return render_template("mensajes/detail.jinja2", mensaje_id=mensaje_id, mensaje=mensaje, respuestas=respuestas, mensaje_con_respuestas=True)


@mensajes.route("/mensajes/respuesta/<int:mensaje_id>")
def detail_response(mensaje_id):
    """Detalle de un Mensajes"""
    mensaje = MensajeRespuesta.query.get_or_404(mensaje_id)
    if mensaje.leido is False:
        mensaje.leido = True
        mensaje.save()
    return render_template("mensajes/detail.jinja2", mensaje_id=mensaje.respuesta_id, mensaje=mensaje, mensaje_con_respuestas=False)


@mensajes.route("/mensajes/nuevo", methods=["GET", "POST"])
@permission_required(MODULO, Permiso.CREAR)
def new():
    """Nuevo Mensaje"""
    form = MensajeForm()
    if form.validate_on_submit():
        destinatario = Usuario.query.get_or_404(form.destinatario.data.id)
        mensaje = Mensaje(
            autor=current_user.email,
            destinatario=destinatario,
            asunto=safe_string(form.asunto.data),
            contenido=safe_string(form.contenido.data),
            leido=False,
        )
        mensaje.save()
        flash("Mensaje envíado correctamente.", "success")
        return redirect(url_for("mensajes.list_active"))
    return render_template("mensajes/new.jinja2", form=form)


@mensajes.route("/mensajes/nueva_respuesta/<int:mensaje_id>", methods=["GET", "POST"])
@permission_required(MODULO, Permiso.MODIFICAR)
def new_response(mensaje_id):
    """Nuevo Mensaje de Respuesta"""
    mensaje = Mensaje.query.get_or_404(mensaje_id)
    form = MensajeRespuestaForm()
    if form.validate_on_submit():
        respuesta = MensajeRespuesta(
            respuesta=mensaje,
            autor=current_user,
            asunto=safe_string(form.asunto.data),
            contenido=safe_string(form.respuesta.data),
            leido=False,
        )
        respuesta.save()
        flash("Respueta envíada correctamente.", "success")
        return redirect(url_for("mensajes.list_active"))
    return render_template("mensajes/new_response.jinja2", mensaje_id=mensaje_id, form=form, mensaje=mensaje)


def _eliminar_respuestas(mensaje_id):
    """Eliminar Respuestas de un Mensaje"""
    respuesta = MensajeRespuesta.query.filter(MensajeRespuesta.estatus == "A").filter(MensajeRespuesta.respuesta_id == mensaje_id).first()
    while respuesta is not None:
        respuesta.delete()
        respuesta = MensajeRespuesta.query.filter(MensajeRespuesta.estatus == "A").filter(MensajeRespuesta.respuesta_id == mensaje_id).first()


@mensajes.route("/mensajes/eliminar/<int:mensaje_id>")
@permission_required(MODULO, Permiso.MODIFICAR)
def delete(mensaje_id):
    """Eliminar Mensajes"""
    mensaje = Mensaje.query.get_or_404(mensaje_id)
    if mensaje.estatus == "A":
        mensaje.delete()
        _eliminar_respuestas(mensaje_id)
        flash("Mensaje eliminado.", "success")
    return redirect(url_for("mensajes.detail", mensaje_id=mensaje.id))


@mensajes.route("/mensajes/eliminar_respuesta/<int:mensaje_id>")
@permission_required(MODULO, Permiso.MODIFICAR)
def delete_response(mensaje_id):
    """Eliminar Mensaje de Respuesta"""
    mensaje = MensajeRespuesta.query.get_or_404(mensaje_id)
    if mensaje.estatus == "A":
        mensaje.delete()
        flash("Respuesta eliminada.", "success")
    return redirect(url_for("mensajes.detail", mensaje_id=mensaje.respuesta_id, mensaje=mensaje, mesaje_con_respuesta=True))


def _recuperar_respuestas(mensaje_id):
    """Recuperar Respuestas de un Mensaje"""
    respuesta = MensajeRespuesta.query.filter(MensajeRespuesta.estatus == "B").filter(MensajeRespuesta.respuesta_id == mensaje_id).first()
    while respuesta is not None:
        respuesta.recover()
        respuesta = MensajeRespuesta.query.filter(MensajeRespuesta.estatus == "B").filter(MensajeRespuesta.respuesta_id == mensaje_id).first()


@mensajes.route("/mensajes/recuperar/<int:mensaje_id>")
@permission_required(MODULO, Permiso.MODIFICAR)
def recover(mensaje_id):
    """Recuperar Mensajes"""
    mensaje = Mensaje.query.get_or_404(mensaje_id)
    if mensaje.estatus == "B":
        mensaje.recover()
        _recuperar_respuestas(mensaje_id)
        flash("Mensaje recuperado.", "success")
    return redirect(url_for("mensajes.detail", mensaje_id=mensaje.id))


@mensajes.route("/mensajes/recuperar_respuesta/<int:mensaje_id>")
@permission_required(MODULO, Permiso.MODIFICAR)
def recover_response(mensaje_id):
    """Recuperar Mensjaes"""
    mensaje = MensajeRespuesta.query.get_or_404(mensaje_id)
    if mensaje.estatus == "B":
        mensaje.recover()
        flash("Respuesta recuperada.", "success")
    return redirect(url_for("mensajes.detail", mensaje_id=mensaje.respuesta_id))

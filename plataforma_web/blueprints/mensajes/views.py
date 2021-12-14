"""
Mensajes, vistas
"""
import json
from typing import List
from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from lib import datatables
from lib.safe_string import safe_string, safe_message
from plataforma_web.blueprints.usuarios.decorators import permission_required

from plataforma_web.blueprints.bitacoras.models import Bitacora
from plataforma_web.blueprints.modulos.models import Modulo
from plataforma_web.blueprints.permisos.models import Permiso
from plataforma_web.blueprints.mensajes.models import Mensaje, MensajeRespuesta

from .forms import MensajeForm, MensajeRespuestaForm

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
    nuevos_mensajes = Mensaje.query.filter(Mensaje.estatus == "A").filter(Mensaje.leido == False).all()
    respuestas = MensajeRespuesta.query.filter(MensajeRespuesta.estatus == "A").filter(MensajeRespuesta.leido == False).all()
    viejos_mensajes = Mensaje.query.filter(Mensaje.estatus == "A").filter(Mensaje.leido == True).limit(500).all()
    return render_template(
        "mensajes/list.jinja2",
        nuevos=nuevos_mensajes,
        respuetas=respuestas,
        viejos=viejos_mensajes,
        titulo="Mensajes",
        estatus="A",
    )


@mensajes.route("/mensajes/inactivos")
@permission_required(MODULO, Permiso.MODIFICAR)
def list_inactive():
    """Listado de Mensajes inactivos"""
    inactivos = Mensaje.query.filter(Mensaje.estatus == "B").all()
    return render_template(
        "mensajes/list.jinja2",
        registros=inactivos,
        titulo="Mensajes inactivos",
        estatus="B",
    )


@mensajes.route("/mensajes/<int:mensaje_id>")
def detail(mensaje_id):
    """Detalle de un Mensajes"""
    mensaje = Mensaje.query.get_or_404(mensaje_id)
    mensaje.leido = True
    mensaje.save()
    respuestas = MensajeRespuesta.query.filter(MensajeRespuesta.estatus == "A").filter(MensajeRespuesta.respuesta_id == mensaje_id).all()
    return render_template("mensajes/detail.jinja2", mensaje=mensaje, respuestas=respuestas)


@mensajes.route("/mensajes/respuesta/<int:mensaje_id>")
def detail_response(mensaje_id):
    """Detalle de un Mensajes"""
    mensaje = Mensaje.query.get_or_404(mensaje_id)
    mensaje.estado = "R"
    mensaje.save()
    return render_template("mensajes/detail.jinja2", mensaje=mensaje)


@mensajes.route("/mensajes/nuevo", methods=["GET", "POST"])
@permission_required(MODULO, Permiso.CREAR)
def new():
    """Nuevo Mensaje"""
    form = MensajeForm()
    if form.validate_on_submit():
        mensaje = Mensaje(
            autor=form.autor.data,
            asunto=form.asunto.data,
            contenido=form.contenido.data,
            leido=False,
        )
        mensaje.save()
        flash("Mensaje guardado.", "success")
        return redirect(url_for("mensajes.detail", mensaje_id=mensaje.id))
    return render_template("mensajes/new.jinja2", form=form)


@mensajes.route("/mensajes/nueva_respuesta/<int:mensaje_id>", methods=["GET", "POST"])
@permission_required(MODULO, Permiso.MODIFICAR)
def new_response(mensaje_id):
    """Nuevo Mensaje de Respuesta"""
    mensaje = Mensaje.query.get_or_404(mensaje_id)
    form = MensajeRespuestaForm()
    if form.validate_on_submit():
        respuesta = Mensaje(
            inicial=False,
            autor=form.autor.data,
            mensaje=form.respuesta.data,
            estado="N",
            sig_mensaje=None,
        )
        respuesta.save()
        # Guadar el ligado de la respuesta a la pregunta inicial
        mensaje.sig_mensaje = respuesta.id
        mensaje.save()
        flash(f"Respueta guardada correctamente.", "success")
        return redirect(url_for("mensajes.detail", mensaje_id=mensaje.id))
    return render_template("mensajes/new_response.jinja2", mensaje_id=mensaje_id, form=form, mensaje=mensaje)


@mensajes.route("/mensajes/edicion/<int:mensaje_id>", methods=["GET", "POST"])
@permission_required(MODULO, Permiso.MODIFICAR)
def edit(mensaje_id):
    """Editar Mensajes"""
    mensaje = Mensaje.query.get_or_404(mensaje_id)
    form = MensajeForm()
    if form.validate_on_submit():
        mensaje.mensaje = form.mensaje.data
        mensaje.save()
        flash(f"Mensajes {mensaje.mensaje} guardado.", "success")
        return redirect(url_for("mensajes.detail", mensaje_id=mensaje.id))
    form.mensaje.data = mensaje.mensaje
    return render_template("mensajes/edit.jinja2", form=form, mensaje=mensaje)


@mensajes.route("/mensajes/eliminar/<int:mensaje_id>")
@permission_required(MODULO, Permiso.MODIFICAR)
def delete(mensaje_id):
    """Eliminar Mensajes"""
    mensaje = Mensaje.query.get_or_404(mensaje_id)
    if mensaje.estatus == "A":
        mensaje.delete()
        flash(f"Mensajes {mensaje.mensaje} eliminado.", "success")
    return redirect(url_for("mensajes.detail", mensaje_id=mensaje.id))


@mensajes.route("/mensajes/recuperar/<int:mensaje_id>")
@permission_required(MODULO, Permiso.MODIFICAR)
def recover(mensaje_id):
    """Recuperar Mensjaes"""
    mensaje = Mensaje.query.get_or_404(mensaje_id)
    if mensaje.estatus == "B":
        mensaje.recover()
        flash(f"Mensjaes {mensaje.mensaje} recuperado.", "success")
    return redirect(url_for("mensajes.detail", mensaje_id=mensaje.id))

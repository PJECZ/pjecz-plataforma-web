"""
Transcripciones, vistas
"""
from flask import Blueprint, flash, redirect, render_template, url_for
from flask_login import login_required
from plataforma_web.blueprints.roles.models import Permiso
from plataforma_web.blueprints.usuarios.decorators import permission_required

from plataforma_web.blueprints.transcripciones.models import Transcripcion
from plataforma_web.blueprints.transcripciones.forms import TranscripcionNewForm, TranscripcionEditForm

transcripciones = Blueprint("transcripciones", __name__, template_folder="templates")


@transcripciones.before_request
@login_required
@permission_required(Permiso.VER_TAREAS)
def before_request():
    """ Permiso por defecto """


@transcripciones.route("/transcripciones")
def list_active():
    """ Listado de Transcripciones activas """
    transcripciones_activas = Transcripcion.query.filter(Transcripcion.estatus == "A").limit(100).all()
    return render_template("transcripciones/list.jinja2", transcripciones=transcripciones_activas, estatus="A")


@transcripciones.route("/transcripciones/inactivas")
def list_inactive():
    """ Listado de Transcripciones inactivas """
    transcripciones_inactivas = Transcripcion.query.filter(Transcripcion.estatus == "B").limit(100).all()
    return render_template("transcripciones/list.jinja2", transcripciones=transcripciones_inactivas, estatus="B")


@transcripciones.route("/transcripciones/<int:transcripcion_id>")
def detail(transcripcion_id):
    """ Detalle de una Transcripción """
    transcripcion = Transcripcion.query.get_or_404(transcripcion_id)
    return render_template("transcripciones/detail.jinja2", transcripcion=transcripcion)


@transcripciones.route("/transcripciones/nueva", methods=["GET", "POST"])
@permission_required(Permiso.CREAR_TAREAS)
def new():
    """ Nueva Transcripción """
    form = TranscripcionNewForm()
    if form.validate_on_submit():
        transcripcion = Transcripcion(descripcion=form.descripcion.data)
        transcripcion.save()
        flash(f"Transcripción {transcripcion.descripcion} guardado.", "success")
        return redirect(url_for("transcripciones.list_active"))
    return render_template("transcripciones/new.jinja2", form=form)

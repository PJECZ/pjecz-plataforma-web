"""
Transcripciones, vistas
"""
from flask import Blueprint, flash, redirect, render_template, url_for
from flask_login import login_required

from plataforma_web.blueprints.roles.models import Permiso
from plataforma_web.blueprints.usuarios.decorators import permission_required
from plataforma_web.blueprints.transcripciones.models import Transcripcion
from plataforma_web.blueprints.transcripciones.forms import TranscripcionNewForm, TranscripcionEditForm, TranscripcionSearchForm

transcripciones = Blueprint("transcripciones", __name__, template_folder="templates")


@transcripciones.before_request
@login_required
@permission_required(Permiso.VER_CUENTAS)
def before_request():
    """Permiso por defecto"""


@transcripciones.route("/transcripciones")
def list_active():
    """Listado de Transcripciones activas"""
    return render_template(
        "transcripciones/list.jinja2",
        transcripciones=Transcripcion.query.filter_by(estatus="A").all(),
        titulo="Transcripciones",
        estatus="A",
    )


@transcripciones.route("/transcripciones/inactivas")
@permission_required(Permiso.MODIFICAR_CUENTAS)
def list_inactive():
    """Listado de Transcripciones inactivas"""
    return render_template(
        "transcripciones/list.jinja2",
        transcripciones=Transcripcion.query.filter_by(estatus="B").all(),
        titulo="Transcripciones inactivas",
        estatus="B",
    )


@transcripciones.route("/transcripciones/<int:transcripcion_id>")
def detail(transcripcion_id):
    """Detalle de una Transcripción"""
    transcripcion = Transcripcion.query.get_or_404(transcripcion_id)
    return render_template("transcripciones/detail.jinja2", transcripcion=transcripcion)


@transcripciones.route("/transcripciones/nueva", methods=["GET", "POST"])
@permission_required(Permiso.CREAR_CUENTAS)
def new():
    """Nueva Transcripción"""
    form = TranscripcionNewForm()
    if form.validate_on_submit():
        transcripcion = Transcripcion(descripcion=form.descripcion.data)
        transcripcion.save()
        flash(f"Transcripción {transcripcion.descripcion} guardado.", "success")
        return redirect(url_for("transcripciones.list_active"))
    return render_template("transcripciones/new.jinja2", form=form)

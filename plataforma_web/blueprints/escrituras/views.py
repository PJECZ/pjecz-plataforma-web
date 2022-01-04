"""
Escrituras, vistas
"""
import datetime
from flask import Blueprint, flash, redirect, render_template, url_for
from flask_login import current_user, login_required

from lib.safe_string import safe_expediente, safe_string, safe_message
from plataforma_web.blueprints.usuarios.decorators import permission_required

from plataforma_web.blueprints.bitacoras.models import Bitacora
from plataforma_web.blueprints.escrituras.models import Escritura
from plataforma_web.blueprints.escrituras.forms import EscrituraForm, EscrituraEditAdminForm
from plataforma_web.blueprints.modulos.models import Modulo
from plataforma_web.blueprints.permisos.models import Permiso

MODULO = "ESCRITURAS"

escrituras = Blueprint("escrituras", __name__, template_folder="templates")


@escrituras.before_request
@login_required
@permission_required(MODULO, Permiso.VER)
def before_request():
    """Permiso por defecto"""


@escrituras.route("/escrituras")
def list_active():
    """Listado de Escrituras activas"""
    escrituras_activas = Escritura.query.filter(Escritura.estatus == "A").all()
    return render_template(
        "escrituras/list.jinja2",
        escrituras=escrituras_activas,
        titulo="Escrituras",
        estatus="A",
    )


@escrituras.route("/escrituras/inactivos")
@permission_required(MODULO, Permiso.MODIFICAR)
def list_inactive():
    """Listado de Escrituras inactivos"""
    escrituras_inactivas = Escritura.query.filter(Escritura.estatus == "B").all()
    return render_template(
        "escrituras/list.jinja2",
        escrituras=escrituras_inactivas,
        titulo="Escrituras inactivos",
        estatus="B",
    )


@escrituras.route("/escrituras/<int:escritura_id>")
def detail(escritura_id):
    """Detalle de una Escritura"""
    escritura = Escritura.query.get_or_404(escritura_id)
    return render_template("escrituras/detail.jinja2", escritura=escritura)


@escrituras.route("/escrituras/nuevo", methods=["GET", "POST"])
@permission_required(MODULO, Permiso.CREAR)
def new():
    """Nueva Escritura"""
    autoridad = current_user.autoridad
    if autoridad is None or autoridad.estatus != "A":
        flash("El juzgado/autoridad no existe o no es activa.", "warning")
        return redirect(url_for("escrituras.list_active"))
    if not autoridad.distrito.es_distrito_judicial:
        flash("El juzgado/autoridad no está en un distrito jurisdiccional.", "warning")
        return redirect(url_for("escrituras.list_active"))
    if not autoridad.es_notaria:
        flash("La autoridad no es una notaria.", "warning")
        return redirect(url_for("escrituras.list_active"))
    form = EscrituraForm()
    if form.validate_on_submit():
        escritura = Escritura(
            autoridad=autoridad,
            envio_fecha=datetime.date.today(),
            etapa=Escritura.ETAPAS[0],
            expediente=safe_expediente(form.expediente.data),
            tipo=form.tipo.data,
            texto=safe_string(form.texto.data),
        )
        escritura.save()
        bitacora = Bitacora(
            modulo=Modulo.query.filter_by(nombre=MODULO).first(),
            usuario=current_user,
            descripcion=safe_message(f"Nueva Escritura expediente {escritura.expediente}"),
            url=url_for("escrituras.detail", escritura_id=escritura.id),
        )
        bitacora.save()
        flash(bitacora.descripcion, "success")
        return redirect(bitacora.url)
    form.distrito.data = autoridad.distrito.nombre
    form.autoridad.data = autoridad.descripcion
    return render_template("escrituras/new.jinja2", form=form)


@escrituras.route("/escrituras/edicion/<int:escritura_id>", methods=["GET", "POST"])
@permission_required(MODULO, Permiso.MODIFICAR)
def edit(escritura_id):
    """Editar Escritura"""
    escritura = Escritura.query.get_or_404(escritura_id)
    form = EscrituraForm()
    if form.validate_on_submit():
        escritura.expediente = safe_string(form.expediente.data)
        escritura.tipo = form.tipo.data
        escritura.texto = safe_string(form.texto.data)
        escritura.save()
        bitacora = Bitacora(
            modulo=Modulo.query.filter_by(nombre=MODULO).first(),
            usuario=current_user,
            descripcion=safe_message(f"Editada Escritura expediente {escritura.expediente}"),
            url=url_for("escrituras.detail", escritura_id=escritura.id),
        )
        bitacora.save()
        flash(bitacora.descripcion, "success")
    form.expediente.data = escritura.expediente
    form.tipo.data = escritura.tipo
    form.texto.data = escritura.texto
    return render_template("escrituras/edit.jinja2", form=form, escritura=escritura)


@escrituras.route('/escrituras/eliminar/<int:escritura_id>')
@permission_required(MODULO, Permiso.MODIFICAR)
def delete(escritura_id):
    """ Eliminar Escritura """
    escritura = Escritura.query.get_or_404(escritura_id)
    if escritura.estatus == 'A':
        escritura.delete()
        bitacora = Bitacora(
            modulo=Modulo.query.filter_by(nombre=MODULO).first(),
            usuario=current_user,
            descripcion=safe_message(f"Eliminado Escritura {escritura.expediente}"),
            url=url_for("escrituras.detail", escritura_id=escritura.id),
        )
        bitacora.save()
        flash(bitacora.descripcion, "success")
    return redirect(url_for('escrituras.detail', escritura_id=escritura.id))


@escrituras.route('/escrituras/recuperar/<int:escritura_id>')
@permission_required(MODULO, Permiso.MODIFICAR)
def recover(escritura_id):
    """ Recuperar Escritura """
    escritura = Escritura.query.get_or_404(escritura_id)
    if escritura.estatus == 'B':
        escritura.recover()
        bitacora = Bitacora(
            modulo=Modulo.query.filter_by(nombre=MODULO).first(),
            usuario=current_user,
            descripcion=safe_message(f"Recuperado Escritura {escritura.expediente}"),
            url=url_for("escrituras.detail", escritura_id=escritura.id),
        )
        bitacora.save()
        flash(bitacora.descripcion, "success")
    return redirect(url_for('escrituras.detail', escritura_id=escritura.id))

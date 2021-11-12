"""
Ventanillas, vistas
"""
from flask import Blueprint, flash, redirect, render_template, url_for
from flask_login import current_user, login_required

from lib.safe_string import safe_message

from plataforma_web.blueprints.bitacoras.models import Bitacora
from plataforma_web.blueprints.modulos.models import Modulo
from plataforma_web.blueprints.permisos.models import Permiso
from plataforma_web.blueprints.usuarios.decorators import permission_required
from plataforma_web.blueprints.ventanillas.models import Ventanilla
from plataforma_web.blueprints.ventanillas.forms import VentanillaForm

MODULO = "VENTANILLAS"

ventanillas = Blueprint("ventanillas", __name__, template_folder="templates")


@ventanillas.before_request
@login_required
@permission_required(MODULO, Permiso.VER)
def before_request():
    """Permiso por defecto"""


@ventanillas.route("/ventanillas")
def list_active():
    """Listado de Ventanillas activas"""
    ventanillas_activas = Ventanilla.query.filter(Ventanilla.estatus == "A").all()
    return render_template(
        "ventanillas/list.jinja2",
        ventanillas=ventanillas_activas,
        titulo="Ventanillas",
        estatus="A",
    )


@ventanillas.route("/ventanillas/inactivos")
@permission_required(MODULO, Permiso.MODIFICAR)
def list_inactive():
    """Listado de Ventanillas inactivas"""
    ventanillas_inactivas = Ventanilla.query.filter(Ventanilla.estatus == "B").all()
    return render_template(
        "ventanillas/list.jinja2",
        ventanillas=ventanillas_inactivas,
        titulo="Ventanillas inactivos",
        estatus="B",
    )


@ventanillas.route("/ventanillas/<int:ventanilla_id>")
def detail(ventanilla_id):
    """Detalle de una Ventanilla"""
    ventanilla = Ventanilla.query.get_or_404(ventanilla_id)
    return render_template("ventanillas/detail.jinja2", ventanilla=ventanilla)


@ventanillas.route("/ventanillas/nuevo", methods=["GET", "POST"])
@permission_required(MODULO, Permiso.CREAR)
def new():
    """Nuevo Ventanilla"""
    form = VentanillaForm()
    if form.validate_on_submit():
        autoridad = form.autoridad.data
        numero = form.numero.data
        ventanilla = Ventanilla(
            autoridad=autoridad,
            numero=numero,
            descripcion=f"Ventanilla {numero} en {autoridad.clave}"
        )
        ventanilla.save()
        bitacora = Bitacora(
            modulo=Modulo.query.filter_by(nombre=MODULO).first(),
            usuario=current_user,
            descripcion=safe_message(f'Nueva ventanilla {ventanilla.descripcion}'),
            url=url_for('ventanillas.detail', ventanilla_id=ventanilla.id),
        )
        bitacora.save()
        flash(bitacora.descripcion, 'success')
        return redirect(bitacora.url)
    return render_template("ventanillas/new.jinja2", form=form)


@ventanillas.route('/ventanillas/edicion/<int:ventanilla_id>', methods=['GET', 'POST'])
@permission_required(MODULO, Permiso.MODIFICAR)
def edit(ventanilla_id):
    """ Editar Ventanilla """
    ventanilla = Ventanilla.query.get_or_404(ventanilla_id)
    form = VentanillaForm()
    if form.validate_on_submit():
        ventanilla.autoridad = form.autoridad.data
        ventanilla.numero = form.numero.data
        ventanilla.descripcion = f"Ventanilla {ventanilla.numero} en {ventanilla.autoridad.clave}"
        ventanilla.save()
        bitacora = Bitacora(
            modulo=Modulo.query.filter_by(nombre=MODULO).first(),
            usuario=current_user,
            descripcion=safe_message(f'Editada la ventanilla {ventanilla.descripcion}'),
            url=url_for('ventanillas.detail', ventanilla_id=ventanilla.id),
        )
        bitacora.save()
        flash(bitacora.descripcion, 'success')
        return redirect(bitacora.url)
    form.autoridad.data = ventanilla.autoridad
    form.numero.data = ventanilla.numero
    return render_template('ventanillas/edit.jinja2', form=form, ventanilla=ventanilla)


@ventanillas.route('/ventanillas/eliminar/<int:ventanilla_id>')
@permission_required(MODULO, Permiso.MODIFICAR)
def delete(ventanilla_id):
    """ Eliminar Ventanilla """
    ventanilla = Ventanilla.query.get_or_404(ventanilla_id)
    if ventanilla.estatus == 'A':
        ventanilla.delete()
        flash(f'Ventanilla {ventanilla.descripcion} eliminada.', 'success')
    return redirect(url_for('ventanillas.detail', ventanilla_id=ventanilla.id))


@ventanillas.route('/ventanillas/recuperar/<int:ventanilla_id>')
@permission_required(MODULO, Permiso.MODIFICAR)
def recover(ventanilla_id):
    """ Recuperar Ventanilla """
    ventanilla = Ventanilla.query.get_or_404(ventanilla_id)
    if ventanilla.estatus == 'B':
        ventanilla.recover()
        flash(f'Ventanilla {ventanilla.descripcion} recuperado.', 'success')
    return redirect(url_for('ventanillas.detail', ventanilla_id=ventanilla.id))

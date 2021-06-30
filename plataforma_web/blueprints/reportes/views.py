"""
Reportes, vistas
"""
from flask import Blueprint, flash, redirect, render_template, url_for
from flask_login import login_required
from plataforma_web.blueprints.roles.models import Permiso
from plataforma_web.blueprints.usuarios.decorators import permission_required

from plataforma_web.blueprints.reportes.models import Reporte
from plataforma_web.blueprints.reportes.forms import ReporteForm

reportes = Blueprint("reportes", __name__, template_folder="templates")


@reportes.before_request
@login_required
@permission_required(Permiso.VER_CUENTAS)
def before_request():
    """Permiso por defecto"""


@reportes.route("/reportes")
def list_active():
    """Listado de Reportes activos"""
    reportes_activos = Reporte.query.filter(Reporte.estatus == "A").order_by(Reporte.creado.desc()).limit(100).all()
    return render_template("reportes/list.jinja2", reportes=reportes_activos, estatus="A")


@reportes.route('/reportes/inactivos')
@permission_required(Permiso.MODIFICAR_CUENTAS)
def list_inactive():
    """ Listado de Reportes inactivos """
    reportes_inactivos = Reporte.query.filter(Reporte.estatus == 'B').order_by(Reporte.creado.desc()).limit(100).all()
    return render_template('reportes/list.jinja2', reportes=reportes_inactivos, estatus='B')


@reportes.route("/reportes/<int:reporte_id>")
def detail(reporte_id):
    """Detalle de un Reporte"""
    reporte = Reporte.query.get_or_404(reporte_id)
    return render_template("reportes/detail.jinja2", reporte=reporte)


@reportes.route("/reportes/nuevo", methods=["GET", "POST"])
@permission_required(Permiso.CREAR_CUENTAS)
def new():
    """Nuevo Reporte"""
    form = ReporteForm()
    if form.validate_on_submit():
        reporte = Reporte(descripcion=form.descripcion.data)
        reporte.save()
        flash(f"Reporte {reporte.descripcion} guardado.", "success")
        return redirect(url_for("reportes.detail", reporte_id=reporte.id))
    return render_template("reportes/new.jinja2", form=form)


@reportes.route("/reportes/edicion/<int:reporte_id>", methods=["GET", "POST"])
@permission_required(Permiso.MODIFICAR_CUENTAS)
def edit(reporte_id):
    """Editar Reporte"""
    reporte = Reporte.query.get_or_404(reporte_id)
    form = ReporteForm()
    if form.validate_on_submit():
        reporte.descripcion = form.descripcion.data
        reporte.save()
        flash(f"Reporte {reporte.descripcion} guardado.", "success")
        return redirect(url_for("reportes.detail", reporte_id=reporte.id))
    form.descripcion.data = reporte.descripcion
    return render_template("reportes/edit.jinja2", form=form, reporte=reporte)


@reportes.route("/reportes/eliminar/<int:reporte_id>")
@permission_required(Permiso.MODIFICAR_CUENTAS)
def delete(reporte_id):
    """Eliminar Reporte"""
    reporte = Reporte.query.get_or_404(reporte_id)
    if reporte.estatus == "A":
        reporte.delete()
        flash(f"Reporte {reporte.descripcion} eliminado.", "success")
    return redirect(url_for("reportes.detail", reporte_id=reporte.id))


@reportes.route("/reportes/recuperar/<int:reporte_id>")
@permission_required(Permiso.MODIFICAR_CUENTAS)
def recover(reporte_id):
    """Recuperar Reporte"""
    reporte = Reporte.query.get_or_404(reporte_id)
    if reporte.estatus == "B":
        reporte.recover()
        flash(f"Reporte {reporte.descripcion} recuperado.", "success")
    return redirect(url_for("reportes.detail", reporte_id=reporte.id))

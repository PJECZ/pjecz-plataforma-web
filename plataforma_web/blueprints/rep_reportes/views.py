"""
Rep Reportes, vistas
"""
from flask import Blueprint, flash, redirect, render_template, url_for
from flask_login import login_required
from plataforma_web.blueprints.roles.models import Permiso
from plataforma_web.blueprints.usuarios.decorators import permission_required

from plataforma_web.blueprints.rep_reportes.models import RepReporte
from plataforma_web.blueprints.rep_reportes.forms import RepReporteForm
from plataforma_web.blueprints.rep_resultados.models import RepResultado

rep_reportes = Blueprint("reportes", __name__, template_folder="templates")


@rep_reportes.before_request
@login_required
@permission_required(Permiso.VER_CUENTAS)
def before_request():
    """Permiso por defecto"""


@rep_reportes.route("/rep_reportes")
def list_active():
    """Listado de Reportes activos"""
    reportes_activos = RepReporte.query.filter(RepReporte.estatus == "A").order_by(RepReporte.creado.desc()).limit(100).all()
    return render_template("rep_reportes/list.jinja2", reportes=reportes_activos, estatus="A")


@rep_reportes.route("/rep_reportes/inactivos")
@permission_required(Permiso.MODIFICAR_CUENTAS)
def list_inactive():
    """Listado de Reportes inactivos"""
    reportes_inactivos = RepReporte.query.filter(RepReporte.estatus == "B").order_by(RepReporte.creado.desc()).limit(100).all()
    return render_template("rep_reportes/list.jinja2", reportes=reportes_inactivos, estatus="B")


@rep_reportes.route("/rep_reportes/<int:reporte_id>")
def detail(reporte_id):
    """Detalle de un Reporte"""
    reporte = RepReporte.query.get_or_404(reporte_id)
    resultados = RepResultado.query.filter(RepResultado.reporte == reporte).filter(RepResultado.estatus == "A").all()
    return render_template("rep_reportes/detail.jinja2", reporte=reporte, resultados=resultados)


@rep_reportes.route("/rep_reportes/nuevo", methods=["GET", "POST"])
@permission_required(Permiso.CREAR_CUENTAS)
def new():
    """Nuevo Reporte"""
    form = RepReporteForm()
    if form.validate_on_submit():
        reporte = RepReporte(
            descripcion=form.descripcion.data,
            desde=form.desde.data,
            hasta=form.hasta.data,
            programado=form.programado.data,
            progreso=form.progreso.data,
        )
        reporte.save()
        flash(f"Reporte {reporte.descripcion} guardado.", "success")
        return redirect(url_for("reportes.detail", reporte_id=reporte.id))
    return render_template("rep_reportes/new.jinja2", form=form)


@rep_reportes.route("/rep_reportes/edicion/<int:reporte_id>", methods=["GET", "POST"])
@permission_required(Permiso.MODIFICAR_CUENTAS)
def edit(reporte_id):
    """Editar Reporte"""
    reporte = RepReporte.query.get_or_404(reporte_id)
    form = RepReporteForm()
    if form.validate_on_submit():
        reporte.descripcion = form.descripcion.data
        reporte.desde = form.desde.data
        reporte.hasta = form.hasta.data
        reporte.programado = form.programado.data
        reporte.progreso = form.progreso.data
        reporte.save()
        flash(f"Reporte {reporte.descripcion} guardado.", "success")
        return redirect(url_for("reportes.detail", reporte_id=reporte.id))
    form.descripcion.data = reporte.descripcion
    form.desde.data = reporte.desde
    form.hasta.data = reporte.hasta
    form.programado.data = reporte.programado
    form.progreso.data = reporte.progreso
    return render_template("rep_reportes/edit.jinja2", form=form, reporte=reporte)


@rep_reportes.route("/rep_reportes/eliminar/<int:reporte_id>")
@permission_required(Permiso.MODIFICAR_CUENTAS)
def delete(reporte_id):
    """Eliminar Reporte"""
    reporte = RepReporte.query.get_or_404(reporte_id)
    if reporte.estatus == "A":
        reporte.delete()
        flash(f"Reporte {reporte.descripcion} eliminado.", "success")
    return redirect(url_for("reportes.detail", reporte_id=reporte.id))


@rep_reportes.route("/rep_reportes/recuperar/<int:reporte_id>")
@permission_required(Permiso.MODIFICAR_CUENTAS)
def recover(reporte_id):
    """Recuperar Reporte"""
    reporte = RepReporte.query.get_or_404(reporte_id)
    if reporte.estatus == "B":
        reporte.recover()
        flash(f"Reporte {reporte.descripcion} recuperado.", "success")
    return redirect(url_for("reportes.detail", reporte_id=reporte.id))

"""
Rep Reportes, vistas
"""
import json
from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import login_required

from lib import datatables
from plataforma_web.blueprints.roles.models import Permiso
from plataforma_web.blueprints.usuarios.decorators import permission_required
from plataforma_web.blueprints.rep_reportes.forms import RepReporteForm
from plataforma_web.blueprints.rep_graficas.models import RepGrafica
from plataforma_web.blueprints.rep_reportes.models import RepReporte

rep_reportes = Blueprint("rep_reportes", __name__, template_folder="templates")

MODULO = "REPORTES"


@rep_reportes.before_request
@login_required
@permission_required(Permiso.VER_CUENTAS)
def before_request():
    """Permiso por defecto"""


@rep_reportes.route("/rep_reportes")
def list_active():
    """Listado de Reportes activos"""
    return render_template(
        "rep_reportes/list.jinja2",
        filtros=json.dumps({"estatus": "A"}),
        titulo="Reportes",
        estatus="A",
    )


@rep_reportes.route("/rep_reportes/inactivos")
@permission_required(Permiso.MODIFICAR_CUENTAS)
def list_inactive():
    """Listado de Reportes inactivos"""
    return render_template(
        "rep_reportes/list.jinja2",
        filtros=json.dumps({"estatus": "B"}),
        titulo="Reportes inactivos",
        estatus="B",
    )


@rep_reportes.route("/rep_reportes/datatable_json", methods=["GET", "POST"])
def datatable_json():
    """DataTable JSON para listado de Reportes"""
    # Tomar parámetros de Datatables
    draw, start, rows_per_page = datatables.get_parameters()
    # Consultar
    consulta = RepReporte.query
    if "estatus" in request.form:
        consulta = consulta.filter_by(estatus=request.form["estatus"])
    else:
        consulta = consulta.filter_by(estatus="A")
    if request.form["rep_grafica_id"]:
        rep_grafica = RepGrafica.query.get(request.form["rep_grafica_id"])
        if rep_grafica:
            consulta = consulta.filter(RepReporte.rep_grafica == rep_grafica)
    registros = consulta.order_by(RepReporte.creado.desc()).offset(start).limit(rows_per_page).all()
    total = consulta.count()
    # Elaborar datos para DataTable
    data = []
    for reporte in registros:
        data.append(
            {
                "creado": reporte.creado.strftime("%Y-%m-%d %H:%M:%S"),
                "detalle": {
                    "descripcion": reporte.descripcion,
                    "url": url_for("rep_reportes.detail", rep_reporte_id=reporte.id),
                },
                "inicio": reporte.inicio.strftime("%Y-%m-%d %H:%M:%S"),
                "termino": reporte.termino.strftime("%Y-%m-%d %H:%M:%S"),
                "programado": reporte.programado.strftime("%Y-%m-%d %H:%M:%S"),
                "progreso": reporte.progreso,
            }
        )
    # Entregar JSON
    return datatables.output(draw, total, data)


@rep_reportes.route("/rep_reportes/<int:rep_reporte_id>")
def detail(rep_reporte_id):
    """Detalle de un Reporte"""
    rep_reporte = RepReporte.query.get_or_404(rep_reporte_id)
    return render_template("rep_reportes/detail.jinja2", rep_reporte=rep_reporte)


@rep_reportes.route("/rep_reportes/nuevo/<int:rep_grafica_id>", methods=["GET", "POST"])
@permission_required(Permiso.CREAR_CUENTAS)
def new(rep_grafica_id):
    """Nuevo Reporte"""
    rep_grafica = RepGrafica.query.get_or_404(rep_grafica_id)
    form = RepReporteForm()
    if form.validate_on_submit():
        rep_reporte = RepReporte(
            rep_grafica=rep_grafica,
            descripcion=form.descripcion.data,
            inicio=form.inicio.data,
            termino=form.termino.data,
            programado=form.programado.data,
            progreso=form.progreso.data,
        )
        rep_reporte.save()
        flash(f"Reporte {rep_reporte.descripcion} guardado.", "success")
        return redirect(url_for("rep_reportes.detail", rep_reporte_id=rep_reporte.id))
    form.rep_grafica.data = rep_grafica.descripcion  # Read only
    return render_template("rep_reportes/new.jinja2", form=form, rep_grafica=rep_grafica)


@rep_reportes.route("/rep_reportes/edicion/<int:rep_reporte_id>", methods=["GET", "POST"])
@permission_required(Permiso.MODIFICAR_CUENTAS)
def edit(rep_reporte_id):
    """Editar Reporte"""
    rep_reporte = RepReporte.query.get_or_404(rep_reporte_id)
    form = RepReporteForm()
    if form.validate_on_submit():
        rep_reporte.descripcion = form.descripcion.data
        rep_reporte.inicio = form.inicio.data
        rep_reporte.termino = form.termino.data
        rep_reporte.programado = form.programado.data
        rep_reporte.progreso = form.progreso.data
        rep_reporte.save()
        flash(f"Reporte {rep_reporte.descripcion} guardado.", "success")
        return redirect(url_for("rep_reportes.detail", rep_reporte_id=rep_reporte.id))
    form.rep_grafica.data = rep_reporte.rep_grafica.descripcion  # Read only
    form.descripcion.data = rep_reporte.descripcion
    form.inicio.data = rep_reporte.inicio
    form.termino.data = rep_reporte.termino
    form.programado.data = rep_reporte.programado
    form.progreso.data = rep_reporte.progreso
    return render_template("rep_reportes/edit.jinja2", form=form, rep_reporte=rep_reporte)


@rep_reportes.route("/rep_reportes/eliminar/<int:rep_reporte_id>")
@permission_required(Permiso.MODIFICAR_CUENTAS)
def delete(rep_reporte_id):
    """Eliminar Reporte"""
    rep_reporte = RepReporte.query.get_or_404(rep_reporte_id)
    if rep_reporte.estatus == "A":
        rep_reporte.delete()
        flash(f"Reporte {rep_reporte.descripcion} eliminado.", "success")
    return redirect(url_for("rep_reportes.detail", rep_reporte_id=rep_reporte.id))


@rep_reportes.route("/rep_reportes/recuperar/<int:rep_reporte_id>")
@permission_required(Permiso.MODIFICAR_CUENTAS)
def recover(rep_reporte_id):
    """Recuperar Reporte"""
    rep_reporte = RepReporte.query.get_or_404(rep_reporte_id)
    if rep_reporte.estatus == "B":
        rep_reporte.recover()
        flash(f"Reporte {rep_reporte.descripcion} recuperado.", "success")
    return redirect(url_for("rep_reportes.detail", rep_reporte_id=rep_reporte.id))

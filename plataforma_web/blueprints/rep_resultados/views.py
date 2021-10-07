"""
Rep Resultados, vistas
"""
import json
from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import login_required

from lib import datatables
from plataforma_web.blueprints.usuarios.decorators import permission_required

from plataforma_web.blueprints.rep_reportes.models import RepReporte
from plataforma_web.blueprints.rep_resultados.models import RepResultado
from plataforma_web.blueprints.permisos.models import Permiso

MODULO = "REP RESULTADOS"

rep_resultados = Blueprint("rep_resultados", __name__, template_folder="templates")


@rep_resultados.before_request
@login_required
@permission_required(MODULO, Permiso.VER)
def before_request():
    """Permiso por defecto"""


@rep_resultados.route("/rep_resultados")
def list_active():
    """Listado de Resultados activos"""
    return render_template(
        "rep_resultados/list.jinja2",
        filtros=json.dumps({"estatus": "A"}),
        titulo="Resultados",
        estatus="A",
    )


@rep_resultados.route("/rep_resultados/inactivos")
@permission_required(MODULO, Permiso.MODIFICAR)
def list_inactive():
    """Listado de Resultados inactivos"""
    return render_template(
        "rep_resultados/list.jinja2",
        filtros=json.dumps({"estatus": "B"}),
        titulo="Resultados inactivos",
        estatus="B",
    )


@rep_resultados.route("/rep_resultados/datatable_json", methods=["GET", "POST"])
def datatable_json():
    """DataTable JSON para listado de Resultados"""
    # Tomar parámetros de Datatables
    draw, start, rows_per_page = datatables.get_parameters()
    # Consultar
    consulta = RepResultado.query
    if "estatus" in request.form:
        consulta = consulta.filter_by(estatus=request.form["estatus"])
    else:
        consulta = consulta.filter_by(estatus="A")
    if request.form["rep_reporte_id"]:
        rep_reporte = RepReporte.query.get(request.form["rep_reporte_id"])
        if rep_reporte:
            consulta = consulta.filter(RepResultado.rep_reporte == rep_reporte)
    registros = consulta.order_by(RepResultado.creado.desc()).offset(start).limit(rows_per_page).all()
    total = consulta.count()
    # Elaborar datos para DataTable
    data = []
    for resultado in registros:
        data.append(
            {
                "creado": resultado.creado.strftime("%Y-%m-%d %H:%M:%S"),
                "detalle": {
                    "descripcion": resultado.descripcion,
                    "url": url_for("rep_resultados.detail", rep_resultado_id=resultado.id),
                },
                "modulo_nombre": resultado.modulo.nombre,
                "tipo": resultado.tipo,
                "cantidad": resultado.cantidad,
            }
        )
    # Entregar JSON
    return datatables.output(draw, total, data)


@rep_resultados.route("/rep_resultados/<int:rep_resultado_id>")
def detail(rep_resultado_id):
    """Detalle de un Resultado"""
    rep_resultado = RepResultado.query.get_or_404(rep_resultado_id)
    return render_template("rep_resultados/detail.jinja2", rep_resultado=rep_resultado)


@rep_resultados.route("/rep_resultados/eliminar/<int:rep_resultado_id>")
@permission_required(MODULO, Permiso.MODIFICAR)
def delete(rep_resultado_id):
    """Eliminar Resultado"""
    rep_resultado = RepResultado.query.get_or_404(rep_resultado_id)
    if rep_resultado.estatus == "A":
        rep_resultado.delete()
        flash(f"Resultado {rep_resultado.descripcion} eliminado.", "success")
    return redirect(url_for("rep_resultados.detail", rep_resultado_id=rep_resultado.id))


@rep_resultados.route("/rep_resultados/recuperar/<int:rep_resultado_id>")
@permission_required(MODULO, Permiso.MODIFICAR)
def recover(rep_resultado_id):
    """Recuperar Resultado"""
    rep_resultado = RepResultado.query.get_or_404(rep_resultado_id)
    if rep_resultado.estatus == "B":
        rep_resultado.recover()
        flash(f"Resultado {rep_resultado.descripcion} recuperado.", "success")
    return redirect(url_for("rep_resultados.detail", rep_resultado_id=rep_resultado.id))

"""
Rep Resultados, vistas
"""
from flask import Blueprint, flash, redirect, render_template, url_for
from flask_login import login_required
from plataforma_web.blueprints.roles.models import Permiso
from plataforma_web.blueprints.usuarios.decorators import permission_required

from plataforma_web.blueprints.rep_resultados.models import RepResultado

rep_resultados = Blueprint("rep_resultados", __name__, template_folder="templates")

MODULO = "REPORTES"


@rep_resultados.before_request
@login_required
@permission_required(Permiso.VER_CUENTAS)
def before_request():
    """Permiso por defecto"""


@rep_resultados.route("/rep_resultados")
def list_active():
    """Listado de Resultados activos"""
    rep_resultados_activos = RepResultado.query.filter_by(estatus="A").order_by(RepResultado.creado.desc()).limit(100).all()
    return render_template("rep_resultados/list.jinja2", rep_resultados=rep_resultados_activos, estatus="A")


@rep_resultados.route("/rep_resultados/inactivos")
@permission_required(Permiso.MODIFICAR_CUENTAS)
def list_inactive():
    """Listado de Resultados inactivos"""
    rep_resultados_inactivos = RepResultado.query.filter_by(estatus="B").order_by(RepResultado.creado.desc()).limit(100).all()
    return render_template("rep_resultados/list.jinja2", rep_resultados=rep_resultados_inactivos, estatus="B")


@rep_resultados.route("/rep_resultados/<int:rep_resultado_id>")
def detail(rep_resultado_id):
    """Detalle de un Resultado"""
    rep_resultado = RepResultado.query.get_or_404(rep_resultado_id)
    return render_template("rep_resultados/detail.jinja2", rep_resultado=rep_resultado)


@rep_resultados.route("/rep_resultados/eliminar/<int:rep_resultado_id>")
@permission_required(Permiso.MODIFICAR_CUENTAS)
def delete(rep_resultado_id):
    """Eliminar Resultado"""
    rep_resultado = RepResultado.query.get_or_404(rep_resultado_id)
    if rep_resultado.estatus == "A":
        rep_resultado.delete()
        flash(f"Resultado {rep_resultado.descripcion} eliminado.", "success")
    return redirect(url_for("rep_resultados.detail", rep_resultado_id=rep_resultado.id))


@rep_resultados.route("/rep_resultados/recuperar/<int:rep_resultado_id>")
@permission_required(Permiso.MODIFICAR_CUENTAS)
def recover(rep_resultado_id):
    """Recuperar Resultado"""
    rep_resultado = RepResultado.query.get_or_404(rep_resultado_id)
    if rep_resultado.estatus == "B":
        rep_resultado.recover()
        flash(f"Resultado {rep_resultado.descripcion} recuperado.", "success")
    return redirect(url_for("rep_resultados.detail", rep_resultado_id=rep_resultado.id))

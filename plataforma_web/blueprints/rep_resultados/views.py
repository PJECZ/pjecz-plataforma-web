"""
Rep Resultados, vistas
"""
from flask import Blueprint, flash, redirect, render_template, url_for
from flask_login import login_required
from plataforma_web.blueprints.roles.models import Permiso
from plataforma_web.blueprints.usuarios.decorators import permission_required

from plataforma_web.blueprints.rep_resultados.models import RepResultado

rep_resultados = Blueprint("resultados", __name__, template_folder="templates")


@rep_resultados.before_request
@login_required
@permission_required(Permiso.VER_CUENTAS)
def before_request():
    """Permiso por defecto"""


@rep_resultados.route("/rep_resultados")
def list_active():
    """Listado de Resultados activos"""
    resultados_activos = RepResultado.query.filter(RepResultado.estatus == "A").order_by(RepResultado.creado.desc()).limit(100).all()
    return render_template("rep_resultados/list.jinja2", resultados=resultados_activos, estatus="A")


@rep_resultados.route("/rep_resultados/inactivos")
@permission_required(Permiso.MODIFICAR_CUENTAS)
def list_inactive():
    """Listado de Resultados inactivos"""
    resultados_inactivos = RepResultado.query.filter(RepResultado.estatus == "B").order_by(RepResultado.creado.desc()).limit(100).all()
    return render_template("rep_resultados/list.jinja2", resultados=resultados_inactivos, estatus="B")


@rep_resultados.route("/rep_resultados/<int:resultado_id>")
def detail(resultado_id):
    """Detalle de un Resultado"""
    resultado = RepResultado.query.get_or_404(resultado_id)
    return render_template("rep_resultados/detail.jinja2", resultado=resultado)


@rep_resultados.route("/rep_resultados/eliminar/<int:resultado_id>")
@permission_required(Permiso.MODIFICAR_CUENTAS)
def delete(resultado_id):
    """Eliminar Resultado"""
    resultado = RepResultado.query.get_or_404(resultado_id)
    if resultado.estatus == "A":
        resultado.delete()
        flash(f"Resultado {resultado.descripcion} eliminado.", "success")
    return redirect(url_for("resultados.detail", resultado_id=resultado.id))


@rep_resultados.route("/rep_resultados/recuperar/<int:resultado_id>")
@permission_required(Permiso.MODIFICAR_CUENTAS)
def recover(resultado_id):
    """Recuperar Resultado"""
    resultado = RepResultado.query.get_or_404(resultado_id)
    if resultado.estatus == "B":
        resultado.recover()
        flash(f"Resultado {resultado.descripcion} recuperado.", "success")
    return redirect(url_for("resultados.detail", resultado_id=resultado.id))

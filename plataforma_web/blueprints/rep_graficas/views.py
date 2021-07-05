"""
Rep Graficas, vistas
"""
from flask import Blueprint, flash, redirect, render_template, url_for
from flask_login import login_required
from plataforma_web.blueprints.roles.models import Permiso
from plataforma_web.blueprints.usuarios.decorators import permission_required

from plataforma_web.blueprints.rep_graficas.models import RepGrafica
from plataforma_web.blueprints.rep_graficas.forms import RepGraficaForm
from plataforma_web.blueprints.rep_reportes.models import RepReporte

rep_graficas = Blueprint("rep_graficas", __name__, template_folder="templates")


@rep_graficas.before_request
@login_required
@permission_required(Permiso.VER_CUENTAS)
def before_request():
    """Permiso por defecto"""


@rep_graficas.route("/rep_graficas")
def list_active():
    """Listado de Gráficas activos"""
    rep_graficas_activos = RepGrafica.query.filter(RepGrafica.estatus == "A").order_by(RepGrafica.creado.desc()).limit(100).all()
    return render_template("rep_graficas/list.jinja2", rep_graficas=rep_graficas_activos, estatus="A")


@rep_graficas.route("/rep_graficas/inactivos")
@permission_required(Permiso.MODIFICAR_CUENTAS)
def list_inactive():
    """Listado de Gráficas inactivos"""
    rep_graficas_inactivos = RepGrafica.query.filter(RepGrafica.estatus == "B").order_by(RepGrafica.creado.desc()).limit(100).all()
    return render_template("rep_graficas/list.jinja2", rep_graficas=rep_graficas_inactivos, estatus="B")


@rep_graficas.route("/rep_graficas/<int:rep_grafica_id>")
def detail(rep_grafica_id):
    """Detalle de una Gráfica"""
    rep_grafica = RepGrafica.query.get_or_404(rep_grafica_id)
    rep_reportes = RepReporte.query.filter(RepReporte.rep_grafica == rep_grafica).filter(RepReporte.estatus == 'A').all()
    return render_template("rep_graficas/detail.jinja2", rep_grafica=rep_grafica, rep_reportes=rep_reportes)


@rep_graficas.route("/rep_graficas/nuevo", methods=["GET", "POST"])
@permission_required(Permiso.CREAR_CUENTAS)
def new():
    """Nuevo Gráfica"""
    form = RepGraficaForm()
    if form.validate_on_submit():
        rep_grafica = RepGrafica(nombre=form.nombre.data)
        rep_grafica.save()
        flash(f"Gráfica {rep_grafica.nombre} guardado.", "success")
        return redirect(url_for("rep_graficas.detail", rep_grafica_id=rep_grafica.id))
    return render_template("rep_graficas/new.jinja2", form=form)


@rep_graficas.route("/rep_graficas/edicion/<int:rep_grafica_id>", methods=["GET", "POST"])
@permission_required(Permiso.MODIFICAR_CUENTAS)
def edit(rep_grafica_id):
    """Editar Gráfica"""
    rep_grafica = RepGrafica.query.get_or_404(rep_grafica_id)
    form = RepGraficaForm()
    if form.validate_on_submit():
        rep_grafica.nombre = form.nombre.data
        rep_grafica.save()
        flash(f"Gráfica {rep_grafica.nombre} guardado.", "success")
        return redirect(url_for("rep_graficas.detail", rep_grafica_id=rep_grafica.id))
    form.nombre.data = rep_grafica.nombre
    return render_template("rep_graficas/edit.jinja2", form=form, rep_grafica=rep_grafica)


@rep_graficas.route("/rep_graficas/eliminar/<int:rep_grafica_id>")
@permission_required(Permiso.MODIFICAR_CUENTAS)
def delete(rep_grafica_id):
    """Eliminar Gráfica"""
    rep_grafica = RepGrafica.query.get_or_404(rep_grafica_id)
    if rep_grafica.estatus == "A":
        rep_grafica.delete()
        flash(f"Gráfica {rep_grafica.nombre} eliminado.", "success")
    return redirect(url_for("rep_graficas.detail", rep_grafica_id=rep_grafica.id))


@rep_graficas.route("/rep_graficas/recuperar/<int:rep_grafica_id>")
@permission_required(Permiso.MODIFICAR_CUENTAS)
def recover(rep_grafica_id):
    """Recuperar Gráfica"""
    rep_grafica = RepGrafica.query.get_or_404(rep_grafica_id)
    if rep_grafica.estatus == "B":
        rep_grafica.recover()
        flash(f"Gráfica {rep_grafica.nombre} recuperado.", "success")
    return redirect(url_for("rep_graficas.detail", rep_grafica_id=rep_grafica.id))

"""
Rep Graficas, vistas
"""
from flask import Blueprint, current_app, flash, redirect, render_template, url_for
from flask_login import current_user, login_required
from plataforma_web.blueprints.roles.models import Permiso
from plataforma_web.blueprints.usuarios.decorators import permission_required

from plataforma_web.extensions import db
from plataforma_web.blueprints.rep_graficas.models import RepGrafica
from plataforma_web.blueprints.rep_graficas.forms import RepGraficaForm
from plataforma_web.blueprints.rep_reportes.models import RepReporte
from plataforma_web.blueprints.rep_resultados.models import RepResultado

rep_graficas = Blueprint("rep_graficas", __name__, template_folder="templates")

MODULO = "REPORTES"


@rep_graficas.before_request
@login_required
@permission_required(Permiso.VER_CUENTAS)
def before_request():
    """Permiso por defecto"""


@rep_graficas.route("/rep_graficas")
def list_active():
    """Listado de Gráficas activos"""
    rep_graficas_activos = RepGrafica.query.filter_by(estatus="A").all()
    return render_template("rep_graficas/list.jinja2", rep_graficas=rep_graficas_activos, estatus="A")


@rep_graficas.route("/rep_graficas/inactivos")
@permission_required(Permiso.MODIFICAR_CUENTAS)
def list_inactive():
    """Listado de Gráficas inactivos"""
    rep_graficas_inactivos = RepGrafica.query.filter_by(estatus="B").all()
    return render_template("rep_graficas/list.jinja2", rep_graficas=rep_graficas_inactivos, estatus="B")


@rep_graficas.route("/rep_graficas/<int:rep_grafica_id>")
def detail(rep_grafica_id):
    """Detalle de una Gráfica"""
    grafica = RepGrafica.query.get_or_404(rep_grafica_id)
    reportes = RepReporte.query.filter(RepReporte.rep_grafica == grafica).filter_by(estatus="A").all()
    return render_template("rep_graficas/detail.jinja2", rep_grafica=grafica, rep_reportes=reportes)


@rep_graficas.route("/rep_graficas/datos/<int:rep_grafica_id>")
def data_json(rep_grafica_id):
    """Datos para graficar"""
    grafica = db.session.query(RepGrafica).get_or_404(rep_grafica_id)
    edictos = []
    listas_de_acuerdos = []
    sentencias = []
    for reporte, resultado in db.session.query(RepReporte, RepResultado).join(RepReporte).filter(RepReporte.rep_grafica == grafica).order_by(RepReporte.inicio).all():
        if resultado.modulo.nombre == "EDICTOS":
            edictos.append({"fecha": reporte.inicio.strftime("%Y-%m-%d"), "cantidad": resultado.cantidad})
        if resultado.modulo.nombre == "LISTAS DE ACUERDOS":
            listas_de_acuerdos.append({"fecha": reporte.inicio.strftime("%Y-%m-%d"), "cantidad": resultado.cantidad})
        if resultado.modulo.nombre == "SENTENCIAS":
            sentencias.append({"fecha": reporte.inicio.strftime("%Y-%m-%d"), "cantidad": resultado.cantidad})
    return {"edictos": edictos, "listas_de_acuerdos": listas_de_acuerdos, "sentencias": sentencias}


@rep_graficas.route("/rep_graficas/nuevo", methods=["GET", "POST"])
@permission_required(Permiso.CREAR_CUENTAS)
def new():
    """Nuevo Gráfica"""
    form = RepGraficaForm()
    if form.validate_on_submit():
        rep_grafica = RepGrafica(
            descripcion=form.descripcion.data,
            desde=form.desde.data,
            hasta=form.hasta.data,
            corte=form.corte.data,
        )
        rep_grafica.save()
        flash(f"Gráfica {rep_grafica.descripcion} guardado.", "success")
        return redirect(url_for("rep_graficas.detail", rep_grafica_id=rep_grafica.id))
    return render_template("rep_graficas/new.jinja2", form=form)


@rep_graficas.route("/rep_graficas/edicion/<int:rep_grafica_id>", methods=["GET", "POST"])
@permission_required(Permiso.MODIFICAR_CUENTAS)
def edit(rep_grafica_id):
    """Editar Gráfica"""
    rep_grafica = RepGrafica.query.get_or_404(rep_grafica_id)
    form = RepGraficaForm()
    if form.validate_on_submit():
        rep_grafica.descripcion = form.descripcion.data
        rep_grafica.desde = form.desde.data
        rep_grafica.hasta = form.hasta.data
        rep_grafica.corte = form.corte.data
        rep_grafica.save()
        flash(f"Gráfica {rep_grafica.descripcion} guardado.", "success")
        return redirect(url_for("rep_graficas.detail", rep_grafica_id=rep_grafica.id))
    form.descripcion.data = rep_grafica.descripcion
    form.desde.data = rep_grafica.desde
    form.hasta.data = rep_grafica.hasta
    form.corte.data = rep_grafica.corte
    return render_template("rep_graficas/edit.jinja2", form=form, rep_grafica=rep_grafica)


@rep_graficas.route("/rep_graficas/eliminar/<int:rep_grafica_id>")
@permission_required(Permiso.MODIFICAR_CUENTAS)
def delete(rep_grafica_id):
    """Eliminar Gráfica"""
    rep_grafica = RepGrafica.query.get_or_404(rep_grafica_id)
    if rep_grafica.estatus == "A":
        rep_grafica.delete()
        flash(f"Gráfica {rep_grafica.descripcion} eliminado.", "success")
    return redirect(url_for("rep_graficas.detail", rep_grafica_id=rep_grafica.id))


@rep_graficas.route("/rep_graficas/recuperar/<int:rep_grafica_id>")
@permission_required(Permiso.MODIFICAR_CUENTAS)
def recover(rep_grafica_id):
    """Recuperar Gráfica"""
    rep_grafica = RepGrafica.query.get_or_404(rep_grafica_id)
    if rep_grafica.estatus == "B":
        rep_grafica.recover()
        flash(f"Gráfica {rep_grafica.descripcion} recuperado.", "success")
    return redirect(url_for("rep_graficas.detail", rep_grafica_id=rep_grafica.id))


@rep_graficas.route("/rep_graficas/elaborar/<int:rep_grafica_id>")
@permission_required(Permiso.MODIFICAR_CUENTAS)
def make(rep_grafica_id):
    """Elaborar Gráfica"""
    rep_grafica = RepGrafica.query.get_or_404(rep_grafica_id)
    if current_user.get_task_in_progress("rep_graficas.tasks.elaborar"):
        flash("Debe esperar porque hay una tarea en el fondo sin terminar.", "warning")
    else:
        current_user.launch_task(
            nombre="rep_graficas.tasks.elaborar",
            descripcion=f"Elaborar gráfica {rep_grafica.descripcion}",
            rep_grafica_id=rep_grafica.id,
        )
        flash("Se está elaborando esta gráfica... <a href='" + url_for("rep_graficas.detail", rep_grafica_id=rep_grafica.id) + "'>Refresque después de unos segundos.</a>", "info")
    return redirect(url_for("rep_graficas.detail", rep_grafica_id=rep_grafica.id))

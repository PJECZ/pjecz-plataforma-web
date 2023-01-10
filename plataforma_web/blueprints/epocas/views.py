"""
Epocas, vistas
"""
import json
from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from lib.datatables import get_datatable_parameters, output_datatable_json
from lib.safe_string import safe_string, safe_message
from plataforma_web.blueprints.usuarios.decorators import permission_required

from plataforma_web.blueprints.bitacoras.models import Bitacora
from plataforma_web.blueprints.epocas.models import Epoca
from plataforma_web.blueprints.epocas.forms import EpocaForm
from plataforma_web.blueprints.modulos.models import Modulo
from plataforma_web.blueprints.permisos.models import Permiso

MODULO = "EPOCAS"

epocas = Blueprint("epocas", __name__, template_folder="templates")


@epocas.before_request
@login_required
@permission_required(MODULO, Permiso.VER)
def before_request():
    """Permiso por defecto"""


@epocas.route('/epocas/datatable_json', methods=['GET', 'POST'])
def datatable_json():
    """DataTable JSON para listado de Epocas"""
    # Tomar parámetros de Datatables
    draw, start, rows_per_page = get_datatable_parameters()
    # Consultar
    consulta = Epoca.query
    if 'estatus' in request.form:
        consulta = consulta.filter_by(estatus=request.form['estatus'])
    else:
        consulta = consulta.filter_by(estatus='A')
    registros = consulta.order_by(Epoca.id).offset(start).limit(rows_per_page).all()
    total = consulta.count()
    # Elaborar datos para DataTable
    data = []
    for resultado in registros:
        data.append(
            {
                'detalle': {
                    'nombre': resultado.nombre,
                    'url': url_for('epocas.detail', epoca_id=resultado.id),
                },
            }
        )
    # Entregar JSON
    return output_datatable_json(draw, total, data)


@epocas.route('/epocas')
def list_active():
    """Listado de Epocas activos"""
    return render_template(
        'epocas/list.jinja2',
        filtros=json.dumps({'estatus': 'A'}),
        titulo='Epocas',
        estatus='A',
    )


@epocas.route('/epocas/inactivos')
@permission_required(MODULO, Permiso.MODIFICAR)
def list_inactive():
    """Listado de Epocas inactivos"""
    return render_template(
        'epocas/list.jinja2',
        filtros=json.dumps({'estatus': 'B'}),
        titulo='Epocas inactivos',
        estatus='B',
    )


@epocas.route("/epocas/<int:epoca_id>")
def detail(epoca_id):
    """Detalle de una Epoca"""
    epoca = Epoca.query.get_or_404(epoca_id)
    return render_template("epocas/detail.jinja2", epoca=epoca)


@epocas.route("/epocas/nuevo", methods=["GET", "POST"])
@permission_required(MODULO, Permiso.CREAR)
def new():
    """Nueva Epoca"""
    form = EpocaForm()
    if form.validate_on_submit():
        epoca = Epoca(nombre=safe_string(form.nombre.data, save_enie=True))
        epoca.save()
        bitacora = Bitacora(
            modulo=Modulo.query.filter_by(nombre=MODULO).first(),
            usuario=current_user,
            descripcion=safe_message(f"Nueva Epoca {epoca.nombre}"),
            url=url_for("epocas.detail", epoca_id=epoca.id),
        )
        bitacora.save()
        flash(bitacora.descripcion, "success")
        return redirect(bitacora.url)
    return render_template("epocas/new.jinja2", form=form)


@epocas.route("/epocas/edicion/<int:epoca_id>", methods=["GET", "POST"])
@permission_required(MODULO, Permiso.MODIFICAR)
def edit(epoca_id):
    """Editar Epoca"""
    epoca = Epoca.query.get_or_404(epoca_id)
    form = EpocaForm()
    if form.validate_on_submit():
        epoca.nombre = safe_string(form.nombre.data, save_enie=True)
        epoca.save()
        bitacora = Bitacora(
            modulo=Modulo.query.filter_by(nombre=MODULO).first(),
            usuario=current_user,
            descripcion=safe_message(f"Editada la Epoca {epoca.nombre}"),
            url=url_for("epocas.detail", epoca_id=epoca.id),
        )
        bitacora.save()
        flash(bitacora.descripcion, "success")
    form.nombre.data = epoca.nombre
    return render_template("epocas/edit.jinja2", form=form, epoca=epoca)


@epocas.route("/epocas/eliminar/<int:epoca_id>")
@permission_required(MODULO, Permiso.MODIFICAR)
def delete(epoca_id):
    """Eliminar Epoca"""
    epoca = Epoca.query.get_or_404(epoca_id)
    if epoca.estatus == "A":
        epoca.delete()
        bitacora = Bitacora(
            modulo=Modulo.query.filter_by(nombre=MODULO).first(),
            usuario=current_user,
            descripcion=safe_message(f"Eliminada la Epoca {epoca.nombre}"),
            url=url_for("epocas.detail", epoca_id=epoca.id),
        )
        bitacora.save()
        flash(bitacora.descripcion, "success")
    return redirect(url_for("epocas.detail", epoca_id=epoca.id))


@epocas.route("/epocas/recuperar/<int:epoca_id>")
@permission_required(MODULO, Permiso.MODIFICAR)
def recover(epoca_id):
    """Recuperar Epoca"""
    epoca = Epoca.query.get_or_404(epoca_id)
    if epoca.estatus == "B":
        epoca.recover()
        bitacora = Bitacora(
            modulo=Modulo.query.filter_by(nombre=MODULO).first(),
            usuario=current_user,
            descripcion=safe_message(f"Recuperado Epoca {epoca.nombre}"),
            url=url_for("epocas.detail", epoca_id=epoca.id),
        )
        bitacora.save()
        flash(bitacora.descripcion, "success")
    return redirect(url_for("epocas.detail", epoca_id=epoca.id))

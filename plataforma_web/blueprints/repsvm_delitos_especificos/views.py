"""
REPSVM Delitos Especificos, vistas
"""
import json
from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from lib.datatables import get_datatable_parameters, output_datatable_json
from lib.safe_string import safe_string, safe_message
from plataforma_web.blueprints.usuarios.decorators import permission_required

from plataforma_web.blueprints.bitacoras.models import Bitacora
from plataforma_web.blueprints.modulos.models import Modulo
from plataforma_web.blueprints.permisos.models import Permiso
from plataforma_web.blueprints.repsvm_delitos_especificos.models import REPSVMDelitoEspecifico
from plataforma_web.blueprints.repsvm_delitos_especificos.forms import REPSVMDelitoEspecificoForm

MODULO = "REPSVM DELITOS ESPECIFICOS"

repsvm_delitos_especificos = Blueprint("repsvm_delitos_especificos", __name__, template_folder="templates")


@repsvm_delitos_especificos.before_request
@login_required
@permission_required(MODULO, Permiso.VER)
def before_request():
    """Permiso por defecto"""


@repsvm_delitos_especificos.route('/repsvm_delitos_especificos/datatable_json', methods=['GET', 'POST'])
def datatable_json():
    """DataTable JSON para listado de Delitos Especificos"""
    # Tomar parámetros de Datatables
    draw, start, rows_per_page = get_datatable_parameters()
    # Consultar
    consulta = REPSVMDelitoEspecifico.query
    if 'estatus' in request.form:
        consulta = consulta.filter_by(estatus=request.form['estatus'])
    else:
        consulta = consulta.filter_by(estatus='A')
    registros = consulta.order_by(REPSVMDelitoEspecifico.descripcion).offset(start).limit(rows_per_page).all()
    total = consulta.count()
    # Elaborar datos para DataTable
    data = []
    for resultado in registros:
        data.append(
            {
                'repsvm_delito_generico': {
                    'nombre': resultado.repsvm_delito_generico.nombre,
                    'url': url_for('repsvm_delitos_genericos.detail', repsvm_delito_generico_id=resultado.repsvm_delito_generico_id),
                },
                'detalle': {
                    'descripcion': resultado.descripcion,
                    'url': url_for('repsvm_delitos_especificos.detail', repsvm_delito_especifico_id=resultado.id),
                },
            }
        )
    # Entregar JSON
    return output_datatable_json(draw, total, data)


@repsvm_delitos_especificos.route('/repsvm_delitos_especificos')
def list_active():
    """Listado de Delitos Especificos activos"""
    return render_template(
        'repsvm_delitos_especificos/list.jinja2',
        filtros=json.dumps({'estatus': 'A'}),
        titulo='Delitos Especificos',
        estatus='A',
    )


@repsvm_delitos_especificos.route('/repsvm_delitos_especificos/inactivos')
@permission_required(MODULO, Permiso.MODIFICAR)
def list_inactive():
    """Listado de Delitos Especificos inactivos"""
    return render_template(
        'repsvm_delitos_especificos/list.jinja2',
        filtros=json.dumps({'estatus': 'B'}),
        titulo='Delitos Especificos inactivos',
        estatus='B',
    )


@repsvm_delitos_especificos.route("/repsvm_delitos_especificos/<int:repsvm_delito_especifico_id>")
def detail(repsvm_delito_especifico_id):
    """Detalle de un Delito Especifico"""
    repsvm_delito_especifico = REPSVMDelitoEspecifico.query.get_or_404(repsvm_delito_especifico_id)
    return render_template("repsvm_delitos_especificos/detail.jinja2", repsvm_delito_especifico=repsvm_delito_especifico)


@repsvm_delitos_especificos.route("/repsvm_delitos_especificos/nuevo", methods=["GET", "POST"])
@permission_required(MODULO, Permiso.CREAR)
def new():
    """Nuevo DelitoEspecifico"""
    form = REPSVMDelitoEspecificoForm()
    if form.validate_on_submit():
        repsvm_delito_especifico = REPSVMDelitoEspecifico(
            repsvm_delito_generico=form.repsvm_delito_generico.data,
            descripcion=safe_string(form.descripcion.data),
        )
        repsvm_delito_especifico.save()
        bitacora = Bitacora(
            modulo=Modulo.query.filter_by(nombre=MODULO).first(),
            usuario=current_user,
            descripcion=safe_message(f"Nuevo DelitoEspecifico {repsvm_delito_especifico.descripcion}"),
            url=url_for("repsvm_delitos_especificos.detail", repsvm_delito_especifico_id=repsvm_delito_especifico.id),
        )
        bitacora.save()
        flash(bitacora.descripcion, "success")
        return redirect(bitacora.url)
    return render_template("repsvm_delitos_especificos/new.jinja2", form=form)


@repsvm_delitos_especificos.route("/repsvm_delitos_especificos/edicion/<int:repsvm_delito_especifico_id>", methods=["GET", "POST"])
@permission_required(MODULO, Permiso.MODIFICAR)
def edit(repsvm_delito_especifico_id):
    """Editar Delito Especifico"""
    repsvm_delito_especifico = REPSVMDelitoEspecifico.query.get_or_404(repsvm_delito_especifico_id)
    form = REPSVMDelitoEspecificoForm()
    if form.validate_on_submit():
        repsvm_delito_especifico.repsvm_delito_generico = form.repsvm_delito_generico.data
        repsvm_delito_especifico.descripcion = safe_string(form.descripcion.data)
        repsvm_delito_especifico.save()
        bitacora = Bitacora(
            modulo=Modulo.query.filter_by(nombre=MODULO).first(),
            usuario=current_user,
            descripcion=safe_message(f"Editado Delito Especifico {repsvm_delito_especifico.descripcion}"),
            url=url_for("repsvm_delitos_especificos.detail", repsvm_delito_especifico_id=repsvm_delito_especifico.id),
        )
        bitacora.save()
        flash(bitacora.descripcion, "success")
        return redirect(bitacora.url)
    form.descripcion.data = repsvm_delito_especifico.descripcion
    return render_template("repsvm_delitos_especificos/edit.jinja2", form=form, repsvm_delito_especifico=repsvm_delito_especifico)


@repsvm_delitos_especificos.route("/repsvm_delitos_especificos/eliminar/<int:repsvm_delito_especifico_id>")
@permission_required(MODULO, Permiso.MODIFICAR)
def delete(repsvm_delito_especifico_id):
    """Eliminar Delito Especifico"""
    repsvm_delito_especifico = REPSVMDelitoEspecifico.query.get_or_404(repsvm_delito_especifico_id)
    if repsvm_delito_especifico.estatus == "A":
        repsvm_delito_especifico.delete()
        bitacora = Bitacora(
            modulo=Modulo.query.filter_by(nombre=MODULO).first(),
            usuario=current_user,
            descripcion=safe_message(f"Eliminado Delito Es {repsvm_delito_especifico.descripcion}"),
            url=url_for("repsvm_delitos_especificos.detail", repsvm_delito_especifico_id=repsvm_delito_especifico.id),
        )
        bitacora.save()
        flash(bitacora.descripcion, "success")
    return redirect(url_for("repsvm_delitos_especificos.detail", repsvm_delito_especifico_id=repsvm_delito_especifico.id))


@repsvm_delitos_especificos.route("/repsvm_delitos_especificos/recuperar/<int:repsvm_delito_especifico_id>")
@permission_required(MODULO, Permiso.MODIFICAR)
def recover(repsvm_delito_especifico_id):
    """Recuperar Delito Especifico"""
    repsvm_delito_especifico = REPSVMDelitoEspecifico.query.get_or_404(repsvm_delito_especifico_id)
    if repsvm_delito_especifico.estatus == "B":
        repsvm_delito_especifico.recover()
        bitacora = Bitacora(
            modulo=Modulo.query.filter_by(nombre=MODULO).first(),
            usuario=current_user,
            descripcion=safe_message(f"Recuperado Delito Especifico {repsvm_delito_especifico.descripcion}"),
            url=url_for("repsvm_delitos_especificos.detail", repsvm_delito_especifico_id=repsvm_delito_especifico.id),
        )
        bitacora.save()
        flash(bitacora.descripcion, "success")
    return redirect(url_for("repsvm_delitos_especificos.detail", repsvm_delito_especifico_id=repsvm_delito_especifico.id))

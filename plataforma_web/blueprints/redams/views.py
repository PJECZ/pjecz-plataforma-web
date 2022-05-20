"""
REDAM (Registro Estatal de Deudores Alimentarios), vistas
"""
import json
from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from lib.datatables import get_datatable_parameters, output_datatable_json
from lib.safe_string import safe_expediente, safe_string, safe_message

from plataforma_web.blueprints.autoridades.models import Autoridad
from plataforma_web.blueprints.bitacoras.models import Bitacora
from plataforma_web.blueprints.distritos.models import Distrito
from plataforma_web.blueprints.modulos.models import Modulo
from plataforma_web.blueprints.permisos.models import Permiso
from plataforma_web.blueprints.usuarios.decorators import permission_required
from plataforma_web.blueprints.redams.models import Redam
from plataforma_web.blueprints.redams.forms import RedamForm, RedamSearchForm

MODULO = "REDAMS"

redams = Blueprint("redams", __name__, template_folder="templates")


@redams.before_request
@login_required
@permission_required(MODULO, Permiso.VER)
def before_request():
    """Permiso por defecto"""


@redams.route("/redams/datatable_json", methods=["GET", "POST"])
def datatable_json():
    """DataTable JSON para listado de REDAM"""
    # Tomar parámetros de Datatables
    draw, start, rows_per_page = get_datatable_parameters()
    # Consultar
    consulta = Redam.query
    if "estatus" in request.form:
        consulta = consulta.filter_by(estatus=request.form["estatus"])
    else:
        consulta = consulta.filter_by(estatus="A")
    if "nombre" in request.form:
        consulta = consulta.filter(Redam.nombre.contains(request.form["nombre"]))
    if "expediente" in request.form:
        consulta = consulta.filter(Redam.expediente.contains(request.form["expediente"]))
    if "autoridad_id" in request.form:
        consulta = consulta.filter_by(autoridad_id=request.form["autoridad_id"])
    registros = consulta.order_by(Redam.id).offset(start).limit(rows_per_page).all()
    total = consulta.count()
    # Elaborar datos para DataTable
    data = []
    for resultado in registros:
        data.append(
            {
                "detalle": {
                    "id": resultado.id,
                    "url": url_for("redams.detail", redam_id=resultado.id),
                },
                "nombre": resultado.nombre,
                "expediente": resultado.expediente,
                "fecha": resultado.fecha,
                "distrito_nombre_corto": resultado.autoridad.distrito.nombre_corto,
                "autoridad_descripcion_corta": resultado.autoridad.descripcion_corta,
                "observaciones": resultado.observaciones,
            }
        )
    # Entregar JSON
    return output_datatable_json(draw, total, data)


@redams.route("/redams")
def list_active():
    """Listado de REDAM activos"""
    return render_template(
        "redams/list.jinja2",
        filtros=json.dumps({"estatus": "A"}),
        titulo="REDAM",
        estatus="A",
    )


@redams.route("/redams/inactivos")
@permission_required(MODULO, Permiso.MODIFICAR)
def list_inactive():
    """Listado de REDAM inactivos"""
    return render_template(
        "redams/list.jinja2",
        filtros=json.dumps({"estatus": "B"}),
        titulo="REDAM inactivos",
        estatus="B",
    )


@redams.route('/redams/buscar', methods=['GET', 'POST'])
def search():
    """Buscar REDAM"""
    form_search = RedamSearchForm()
    if form_search.validate_on_submit():
        busqueda = {'estatus': 'A'}
        titulos = []
        if form_search.nombre.data:
            nombre = safe_string(form_search.nombre.data)
            if nombre != '':
                busqueda['nombre'] = nombre
                titulos.append('nombre ' + nombre)
        if form_search.expediente.data:
            expediente = safe_expediente(form_search.expediente.data)
            if expediente != '':
                busqueda['expediente'] = expediente
                titulos.append('expediente ' + expediente)
        return render_template(
            'redams/list.jinja2',
            filtros=json.dumps(busqueda),
            titulo='REDAM con ' + ', '.join(titulos),
            estatus='A',
        )
    return render_template('redams/search.jinja2', form=form_search)


@redams.route("/redams/<int:redam_id>")
def detail(redam_id):
    """Detalle de un REDAM"""
    redam = Redam.query.get_or_404(redam_id)
    return render_template("redams/detail.jinja2", redam=redam)


@redams.route("/redams/nuevo", methods=["GET", "POST"])
@permission_required(MODULO, Permiso.CREAR)
def new():
    """Nuevo REDAM"""
    form = RedamForm()
    if form.validate_on_submit():
        autoridad = Autoridad.query.get_or_404(form.autoridad.data)
        redam = Redam(
            autoridad=autoridad,
            nombre=safe_string(form.nombre.data),
            expediente=safe_expediente(form.expediente.data),
            fecha=form.fecha.data,
            observaciones=safe_string(form.observaciones.data, max_len=1024),
        )
        redam.save()
        bitacora = Bitacora(
            modulo=Modulo.query.filter_by(nombre=MODULO).first(),
            usuario=current_user,
            descripcion=safe_message(f"Nuevo REDAM {redam.nombre}"),
            url=url_for("redam.detail", redam_id=redam.id),
        )
        bitacora.save()
        flash(bitacora.descripcion, "success")
        return redirect(bitacora.url)
    distritos = Distrito.query.filter_by(estatus="A").order_by(Distrito.nombre).all()  # .filter_by(es_distrito_judicial=True)
    autoridades = Autoridad.query.filter_by(estatus="A").filter_by(es_notaria=False).order_by(Autoridad.clave).all()  # .filter_by(es_jurisdiccional=True)
    return render_template(
        "redams/new.jinja2",
        form=form,
        distritos=distritos,
        autoridades=autoridades,
        distrito_no_definido=Distrito.query.filter_by(nombre="NO DEFINIDO").first(),
        autoridad_no_definido=Autoridad.query.filter_by(clave="ND").first(),
    )


@redams.route("/redams/edicion/<int:redam_id>", methods=["GET", "POST"])
@permission_required(MODULO, Permiso.MODIFICAR)
def edit(redam_id):
    """Editar REDAM"""
    redam = Redam.query.get_or_404(redam_id)
    form = RedamForm()
    if form.validate_on_submit():
        redam.autoridad = Autoridad.query.get_or_404(form.autoridad.data)
        redam.nombre = safe_string(form.nombre.data)
        redam.expediente = safe_expediente(form.expediente.data)
        redam.fecha = form.fecha.data
        redam.observaciones = safe_string(form.observaciones.data)
        redam.save()
        bitacora = Bitacora(
            modulo=Modulo.query.filter_by(nombre=MODULO).first(),
            usuario=current_user,
            descripcion=safe_message(f"Editado REDAM {redam.nombre}"),
            url=url_for("redams.detail", redam_id=redam.id),
        )
        bitacora.save()
        flash(bitacora.descripcion, "success")
        return redirect(bitacora.url)
    form.nombre.data = redam.nombre
    form.expediente.data = redam.expediente
    form.fecha.data = redam.fecha
    form.observaciones.data = redam.observaciones
    distritos = Distrito.query.filter_by(estatus="A").order_by(Distrito.nombre).all()  # .filter_by(es_distrito_judicial=True)
    autoridades = Autoridad.query.filter_by(estatus="A").filter_by(es_notaria=False).order_by(Autoridad.clave).all()  # .filter_by(es_jurisdiccional=True)
    return render_template(
        "redams/edit.jinja2",
        form=form,
        redam=redam,
        distritos=distritos,
        autoridades=autoridades,
    )


@redams.route("/redams/eliminar/<int:redam_id>")
@permission_required(MODULO, Permiso.MODIFICAR)
def delete(redam_id):
    """Eliminar REDAM"""
    redam = Redam.query.get_or_404(redam_id)
    if redam.estatus == "A":
        redam.delete()
        bitacora = Bitacora(
            modulo=Modulo.query.filter_by(nombre=MODULO).first(),
            usuario=current_user,
            descripcion=safe_message(f"Eliminado REDAM {redam.nombre}"),
            url=url_for("redams.detail", redam_id=redam.id),
        )
        bitacora.save()
        flash(bitacora.descripcion, "success")
    return redirect(url_for("redams.detail", redam_id=redam.id))


@redams.route("/redams/recuperar/<int:redam_id>")
@permission_required(MODULO, Permiso.MODIFICAR)
def recover(redam_id):
    """Recuperar REDAM"""
    redam = Redam.query.get_or_404(redam_id)
    if redam.estatus == "B":
        redam.recover()
        bitacora = Bitacora(
            modulo=Modulo.query.filter_by(nombre=MODULO).first(),
            usuario=current_user,
            descripcion=safe_message(f"Recuperado REDAM {redam.nombre}"),
            url=url_for("redams.detail", redam_id=redam.id),
        )
        bitacora.save()
        flash(bitacora.descripcion, "success")
    return redirect(url_for("redams.detail", redam_id=redam.id))

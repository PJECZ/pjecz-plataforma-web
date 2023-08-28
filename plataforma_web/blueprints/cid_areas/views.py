"""
CID Areas, vistas
"""
import json
from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from lib.datatables import get_datatable_parameters, output_datatable_json
from lib.safe_string import safe_clave, safe_string, safe_message

from plataforma_web.blueprints.bitacoras.models import Bitacora
from plataforma_web.blueprints.modulos.models import Modulo
from plataforma_web.blueprints.permisos.models import Permiso
from plataforma_web.blueprints.usuarios.decorators import permission_required
from plataforma_web.blueprints.cid_areas.models import CIDArea
from plataforma_web.blueprints.cid_areas_autoridades.models import CIDAreaAutoridad
from plataforma_web.blueprints.cid_areas.forms import CIDAreaForm

MODULO = "CID AREAS"

cid_areas = Blueprint("cid_areas", __name__, template_folder="templates")


@cid_areas.before_request
@login_required
@permission_required(MODULO, Permiso.VER)
def before_request():
    """Permiso por defecto"""


@cid_areas.route("/cid_areas/datatable_json", methods=["GET", "POST"])
def datatable_json():
    """DataTable JSON para listado de areas"""
    # Tomar parámetros de Datatables
    draw, start, rows_per_page = get_datatable_parameters()
    # Consultar
    consulta = CIDArea.query
    if "estatus" in request.form:
        consulta = consulta.filter_by(estatus=request.form["estatus"])
    else:
        consulta = consulta.filter_by(estatus="A")
    registros = consulta.order_by(CIDArea.nombre).offset(start).limit(rows_per_page).all()
    total = consulta.count()
    # Elaborar datos para DataTable
    data = []
    for resultado in registros:
        data.append(
            {
                "detalle": {
                    "clave": resultado.clave,
                    "url": url_for("cid_areas.detail", cid_area_id=resultado.id),
                },
                "nombre": resultado.nombre,
            }
        )
    # Entregar JSON
    return output_datatable_json(draw, total, data)


@cid_areas.route("/cid_areas")
def list_active():
    """Listado de Areas activas"""
    return render_template(
        "cid_areas/list.jinja2",
        filtros=json.dumps({"estatus": "A"}),
        titulo="Areas",
        estatus="A",
    )


@cid_areas.route("/cid_areas/inactivas")
@permission_required(MODULO, Permiso.MODIFICAR)
def list_inactive():
    """Listado de Areas inactivas"""
    return render_template(
        "cid_areas/list.jinja2",
        filtros=json.dumps({"estatus": "B"}),
        titulo="Areas inactivos",
        estatus="B",
    )


@cid_areas.route("/cid_areas/<int:cid_area_id>")
def detail(cid_area_id):
    """Detalle de un Area"""
    cid_area_autoridad = CIDAreaAutoridad.query.join(CIDArea).filter(CIDArea.id==cid_area_id).first()
    if not cid_area_autoridad:
        cid_area= CIDArea.query.get_or_404(cid_area_id)
        return render_template("cid_areas/detail_not_autoridad.jinja2", cid_area=cid_area)
    return render_template("cid_areas/detail.jinja2", cid_area_autoridad=cid_area_autoridad, filtros=json.dumps({"estatus":"A", "area_id":cid_area_autoridad.cid_area.id}))


@cid_areas.route("/cid_areas/nuevo", methods=["GET", "POST"])
@permission_required(MODULO, Permiso.CREAR)
def new():
    """Nueva Area"""
    form = CIDAreaForm()
    if form.validate_on_submit():
        es_valido = True
        # Validar que la clave no se repita
        clave = safe_clave(form.clave.data)
        if CIDArea.query.filter_by(clave=clave).first():
            flash("La clave ya está en uso. Debe de ser única.", "warning")
            es_valido = False
        # Validar que el nombre no se repita
        nombre = safe_string(form.nombre.data, save_enie=True)
        if CIDArea.query.filter_by(nombre=nombre).first():
            flash("EL nombre ya está en uso. Debe de ser único.", "warning")
            es_valido = False
        # Si es válido, guardar
        if es_valido is True:
            cid_area = CIDArea(
                clave=clave,
                nombre=nombre,
            )
            cid_area.save()
            bitacora = Bitacora(
                modulo=Modulo.query.filter_by(nombre=MODULO).first(),
                usuario=current_user,
                descripcion=safe_message(f"Nuevo cid_area {cid_area.clave}"),
                url=url_for("cid_areas.detail", cid_area_id=cid_area.id),
            )
            bitacora.save()
            flash(bitacora.descripcion, "success")
            return redirect(bitacora.url)
    return render_template("cid_areas/new.jinja2", form=form)


@cid_areas.route("/cid_areas/edicion/<int:cid_area_id>", methods=["GET", "POST"])
@permission_required(MODULO, Permiso.MODIFICAR)
def edit(cid_area_id):
    """Editar Area"""
    cid_area = CIDArea.query.get_or_404(cid_area_id)
    form = CIDAreaForm()
    if form.validate_on_submit():
        es_valido = True
        # Si cambia la clave verificar que no este en uso
        clave = safe_clave(form.clave.data)
        if cid_area.clave != clave:
            cid_area_existente = CIDArea.query.filter_by(clave=clave).first()
            if cid_area_existente and cid_area_existente.id != cid_area.id:
                es_valido = False
                flash("La clave ya está en uso. Debe de ser única.", "warning")
        # Si cambia el nombre verificar que no este en uso
        nombre = safe_string(form.nombre.data, save_enie=True)
        if cid_area.nombre != nombre:
            cid_area_existente = CIDArea.query.filter_by(nombre=nombre).first()
            if cid_area_existente and cid_area_existente.id != cid_area.id:
                es_valido = False
                flash("El nombre ya está en uso. Debe de ser único.", "warning")
        # Si es válido, actualizar
        if es_valido:
            cid_area.clave = clave
            cid_area.nombre = nombre
            cid_area.save()
            bitacora = Bitacora(
                modulo=Modulo.query.filter_by(nombre=MODULO).first(),
                usuario=current_user,
                descripcion=safe_message(f"Editada area {cid_area.clave}"),
                url=url_for("cid_areas.detail", cid_area_id=cid_area.id),
            )
            bitacora.save()
            flash(bitacora.descripcion, "success")
            return redirect(bitacora.url)
    form.clave.data = cid_area.clave
    form.nombre.data = cid_area.nombre
    return render_template("cid_areas/edit.jinja2", form=form, cid_area=cid_area)


@cid_areas.route("/cid_areas/eliminar/<int:cid_area_id>")
@permission_required(MODULO, Permiso.MODIFICAR)
def delete(cid_area_id):
    """Eliminar Area"""
    cid_area = CIDArea.query.get_or_404(cid_area_id)
    if cid_area.estatus == "A":
        cid_area.delete()
        bitacora = Bitacora(
            modulo=Modulo.query.filter_by(nombre=MODULO).first(),
            usuario=current_user,
            descripcion=safe_message(f"Eliminada área {cid_area.nombre}"),
            url=url_for("cid_areas.detail", cid_area_id=cid_area.id),
        )
        bitacora.save()
        flash(bitacora.descripcion, "success")
        return redirect(bitacora.url)
    return redirect(url_for("cid_areas.detail", cid_area_id=cid_area.id))


@cid_areas.route("/cid_areas/recuperar/<int:cid_area_id>")
@permission_required(MODULO, Permiso.MODIFICAR)
def recover(cid_area_id):
    """Recuperar Area"""
    cid_area = CIDArea.query.get_or_404(cid_area_id)
    if cid_area.estatus == "B":
        cid_area.recover()
        bitacora = Bitacora(
            modulo=Modulo.query.filter_by(nombre=MODULO).first(),
            usuario=current_user,
            descripcion=safe_message(f"Recuperada área {cid_area.nombre}"),
            url=url_for("cid_areas.detail", cid_area_id=cid_area.id),
        )
        bitacora.save()
        flash(bitacora.descripcion, "success")
        return redirect(bitacora.url)
    return redirect(url_for("cid_areas.detail", cid_area=cid_area.id))

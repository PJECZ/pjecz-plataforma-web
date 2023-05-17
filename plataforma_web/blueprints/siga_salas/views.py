"""
SIGA Salas, vistas
"""
import json
from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from lib.datatables import get_datatable_parameters, output_datatable_json
from lib.safe_string import safe_string, safe_message
from plataforma_web.blueprints.usuarios.decorators import permission_required

from plataforma_web.blueprints.bitacoras.models import Bitacora
# from plataforma_web.blueprints.siga_salas.forms import DomicilioForm, siga_salasearchForm
from plataforma_web.blueprints.siga_salas.models import SIGASala
from plataforma_web.blueprints.modulos.models import Modulo
from plataforma_web.blueprints.permisos.models import Permiso

MODULO = "SIGA Salas"

siga_salas = Blueprint("siga_salas", __name__, template_folder="templates")


@siga_salas.before_request
@login_required
@permission_required(MODULO, Permiso.VER)
def before_request():
    """Permiso por defecto"""


@siga_salas.route("/siga_salas/datatable_json", methods=["GET", "POST"])
def datatable_json():
    """DataTable JSON para listado de siga_salas"""
    # Tomar parámetros de Datatables
    draw, start, rows_per_page = get_datatable_parameters()
    # Consultar
    consulta = SIGASala.query
    if "estatus" in request.form:
        consulta = consulta.filter_by(estatus=request.form["estatus"])
    else:
        consulta = consulta.filter_by(estatus="A")
    registros = consulta.order_by(SIGASala.clave).offset(start).limit(rows_per_page).all()
    total = consulta.count()
    # Elaborar datos para DataTable
    data = []
    for resultado in registros:
        data.append(
            {
                "detalle": {
                    "clave": resultado.clave,
                    "url": url_for("siga_salas.detail", siga_sala_id=resultado.id),
                },
                "direccion_ip": resultado.direccion_ip,
                "direccion_nvr": resultado.direccion_nvr,
                "estado": resultado.estado,
                "descripcion": resultado.descripcion,
            }
        )
    # Entregar JSON
    return output_datatable_json(draw, total, data)


@siga_salas.route("/siga_salas")
def list_active():
    """Listado de SIGASala activas"""
    return render_template(
        "siga_salas/list.jinja2",
        filtros=json.dumps({"estatus": "A"}),
        titulo="siga_salas",
        estatus="A",
    )


@siga_salas.route("/siga_salas/inactivos")
@permission_required(MODULO, Permiso.MODIFICAR)
def list_inactive():
    """Listado de SIGASala inactivas"""
    return render_template(
        "siga_salas/list.jinja2",
        filtros=json.dumps({"estatus": "B"}),
        titulo="siga_salas inactivos",
        estatus="B",
    )


@siga_salas.route("/siga_salas/<int:siga_sala_id>")
def detail(siga_sala_id):
    """Detalle de un SIGASala"""
    siga_sala = SIGASala.query.get_or_404(siga_sala_id)
    return render_template("siga_salas/detail.jinja2", siga_sala=siga_sala)


# @siga_salas.route("/siga_salas/edicion/<int:siga_sala_id>", methods=["GET", "POST"])
# @permission_required(MODULO, Permiso.MODIFICAR)
# def edit(siga_sala_id):
#     """Editar SIGASala"""
#     siga_sala = SIGASala.query.get_or_404(siga_sala_id)
#     form = SIGASalaEditForm()
#     if form.validate_on_submit():
#         es_valido = True
#         # Si se cambia el edificio, validar que no se repita
#         edificio = safe_string(form.edificio.data, max_len=64, save_enie=True)
#         if domicilio.edificio != edificio:
#             domicilio_existente = Domicilio.query.filter_by(edificio=edificio).first()
#             if domicilio_existente and domicilio_existente.id != domicilio_id:
#                 es_valido = False
#                 flash("El edificio ya está en uso. Debe de ser único.", "warning")
#         # Si es valido, actualizar
#         if es_valido:
#             domicilio.edificio = edificio
#             domicilio.estado = safe_string(form.estado.data, max_len=64, save_enie=True)
#             domicilio.municipio = safe_string(form.municipio.data, max_len=64, save_enie=True)
#             domicilio.calle = safe_string(form.calle.data, max_len=256, save_enie=True)
#             domicilio.num_ext = safe_string(form.num_ext.data, max_len=24)
#             domicilio.num_int = safe_string(form.num_int.data, max_len=24)
#             domicilio.colonia = safe_string(form.colonia.data, max_len=256, save_enie=True)
#             domicilio.cp = form.cp.data
#             domicilio.completo = f"{domicilio.calle} #{domicilio.num_ext} {domicilio.num_int}, {domicilio.colonia}, {domicilio.municipio}, {domicilio.estado}, C.P. {domicilio.cp}"
#             domicilio.save()
#             bitacora = Bitacora(
#                 modulo=Modulo.query.filter_by(nombre=MODULO).first(),
#                 usuario=current_user,
#                 descripcion=safe_message(f"Editado el Domicilio {domicilio.edificio}"),
#                 url=url_for("siga_salas.detail", domicilio_id=domicilio.id),
#             )
#             bitacora.save()
#             flash(bitacora.descripcion, "success")
#             return redirect(bitacora.url)
#     form.edificio.data = domicilio.edificio
#     form.estado.data = domicilio.estado
#     form.municipio.data = domicilio.municipio
#     form.calle.data = domicilio.calle
#     form.num_ext.data = domicilio.num_ext
#     form.num_int.data = domicilio.num_int
#     form.colonia.data = domicilio.colonia
#     form.cp.data = domicilio.cp
#     return render_template("siga_salas/edit.jinja2", form=form, domicilio=domicilio)


@siga_salas.route("/siga_salas/eliminar/<int:siga_sala_id>")
@permission_required(MODULO, Permiso.MODIFICAR)
def delete(siga_sala_id):
    """Eliminar SIGASala"""
    siga_sala = SIGASala.query.get_or_404(siga_sala_id)
    if siga_sala.estatus == "A":
        siga_sala.delete()
        bitacora = Bitacora(
            modulo=Modulo.query.filter_by(nombre=MODULO).first(),
            usuario=current_user,
            descripcion=safe_message(f"Eliminada la SIGA_Sala {siga_sala.clave}"),
            url=url_for("siga_salas.detail", siga_sala_id=siga_sala.id),
        )
        bitacora.save()
        flash(bitacora.descripcion, "success")
    return redirect(url_for("siga_salas.detail", siga_sala_id=siga_sala_id))


@siga_salas.route("/siga_salas/recuperar/<int:siga_sala_id>")
@permission_required(MODULO, Permiso.MODIFICAR)
def recover(siga_sala_id):
    """Recuperar SIGASala"""
    siga_sala = SIGASala.query.get_or_404(siga_sala_id)
    if siga_sala.estatus == "B":
        siga_sala.recover()
        bitacora = Bitacora(
            modulo=Modulo.query.filter_by(nombre=MODULO).first(),
            usuario=current_user,
            descripcion=safe_message(f"Recuperada la SIGA_Sala {siga_sala.clave}"),
            url=url_for("siga_salas.detail", siga_sala_id=siga_sala.id),
        )
        bitacora.save()
        flash(bitacora.descripcion, "success")
    return redirect(url_for("siga_salas.detail", siga_sala_id=siga_sala_id))
"""
Requisiciones Categorias, vistas
"""

import json
from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from lib.datatables import get_datatable_parameters, output_datatable_json
from lib.safe_string import safe_string, safe_message

from plataforma_web.blueprints.bitacoras.models import Bitacora
from plataforma_web.blueprints.modulos.models import Modulo
from plataforma_web.blueprints.permisos.models import Permiso
from plataforma_web.blueprints.usuarios.decorators import permission_required
from plataforma_web.blueprints.req_categorias.models import ReqCategoria
from plataforma_web.blueprints.req_categorias.forms import ReqCategoriaNewForm

MODULO = "REQ CATEGORIAS"

# Roles que deben estar en la base de datos
ROL_ASISTENTES = "REQUISICIONES ASISTENTES"
ROL_SOLICITANTES = "REQUISICIONES SOLICITANTES"
ROL_AUTORIZANTES = "REQUISICIONES AUTORIZANTES"
ROL_REVISANTES = "REQUISICIONES REVISANTES"

ROLES_PUEDEN_VER = (ROL_SOLICITANTES, ROL_AUTORIZANTES, ROL_REVISANTES, ROL_ASISTENTES)
ROLES_PUEDEN_IMPRIMIR = (ROL_SOLICITANTES, ROL_AUTORIZANTES, ROL_REVISANTES, ROL_ASISTENTES)

req_categorias = Blueprint("req_categorias", __name__, template_folder="templates")


@req_categorias.before_request
@login_required
@permission_required(MODULO, Permiso.VER)
def before_request():
    """Permiso por defecto"""


@req_categorias.route("/req_categorias/datatable_json", methods=["GET", "POST"])
def datatable_json():
    """DataTable JSON para listado de Categorias"""
    # Tomar parámetros de Datatables
    draw, start, rows_per_page = get_datatable_parameters()
    # Consultar
    consulta = ReqCategoria.query
    if "estatus" in request.form:
        consulta = consulta.filter_by(estatus=request.form["estatus"])
    else:
        consulta = consulta.filter_by(estatus="A")
    if "descripcion" in request.form:
        consulta = consulta.filter(ReqCategoria.descripcion.contains(safe_string(request.form["descripcion"], to_uppercase=True)))
    registros = consulta.order_by(ReqCategoria.id).offset(start).limit(rows_per_page).all()

    total = consulta.count()
    # Elaborar datos para DataTable
    data = []
    for resultado in registros:
        data.append(
            {
                "detalle": {
                    "id": resultado.id,
                    "url": url_for("req_categorias.detail", req_categoria_id=resultado.id),
                },
                "id": resultado.id,
                "descripcion": resultado.descripcion,
            }
        )
    # Entregar JSON
    return output_datatable_json(draw, total, data)


@req_categorias.route("/req_categorias/nuevo", methods=["GET", "POST"])
@permission_required(MODULO, Permiso.CREAR)
def new():
    """Categorias nuevo registro"""
    form = ReqCategoriaNewForm()

    if form.validate_on_submit():
        # Guardar articulo
        req_categoria = ReqCategoria(
            descripcion=safe_string(form.descripcion.data, max_len=256, to_uppercase=True, save_enie=True),
        )
        req_categoria.save()

        # Guardar en la bitacora
        bitacora = Bitacora(
            modulo=Modulo.query.filter_by(nombre=MODULO).first(),
            usuario=current_user,
            descripcion=safe_message(f"Categoria creada {req_categoria.descripcion}"),
            url=url_for("req_categorias.detail", req_categoria_id=req_categoria.id),
        )
        bitacora.save()
        flash(bitacora.descripcion, "success")
        return redirect(bitacora.url)
    return render_template("req_categorias/new.jinja2", titulo="Registro nuevo de categoria", form=form)


@req_categorias.route("/req_categorias/<int:req_categoria_id>")
def detail(req_categoria_id):
    """Detalle de un registro de Categorias"""
    req_categoria = ReqCategoria.query.get_or_404(req_categoria_id)
    return render_template("req_categorias/detail.jinja2", req_categoria=req_categoria)


@req_categorias.route("/req_categorias")
def list_active():
    """Listado de Categorias activas"""
    return render_template(
        "req_categorias/list.jinja2",
        filtros=json.dumps({"estatus": "A"}),
        titulo="Categorias",
        estatus="A",
    )


@req_categorias.route("/req_categorias/inactivos")
@permission_required(MODULO, Permiso.MODIFICAR)
def list_inactive():
    """Listado de registro de Categorias inactivas"""
    return render_template(
        "req_categorias/list.jinja2",
        filtros=json.dumps({"estatus": "B"}),
        titulo="Listado de registros de Categorias inactivas",
        estatus="B",
    )

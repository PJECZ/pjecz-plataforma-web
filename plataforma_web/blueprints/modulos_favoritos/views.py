"""
Modulos Favoritos, vistas
"""
import json

from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from lib.datatables import get_datatable_parameters, output_datatable_json
from plataforma_web.blueprints.usuarios.decorators import permission_required

from plataforma_web.blueprints.modulos_favoritos.models import ModuloFavorito
from plataforma_web.blueprints.modulos.models import Modulo
from plataforma_web.blueprints.usuarios.models import Usuario
from plataforma_web.blueprints.permisos.models import Permiso

MODULO = "MODULOS"

modulos_favoritos = Blueprint("modulos_favoritos", __name__, template_folder="templates")


@modulos_favoritos.before_request
@login_required
@permission_required(MODULO, Permiso.VER)
def before_request():
    """Permiso por defecto"""


@modulos_favoritos.route("/modulos_favoritos/datatable_json", methods=["GET", "POST"])
def datatable_json():
    """DataTable JSON para listado de Módulos Favoritos"""
    # Tomar parámetros de DataTables
    draw, start, rows_per_page = get_datatable_parameters()
    # Consultar
    consulta = ModuloFavorito.query.join(Modulo)
    if "estatus" in request.form:
        consulta = consulta.filter(ModuloFavorito.estatus == request.form["estatus"])
    else:
        consulta = consulta.filter(ModuloFavorito.estatus == "A")
    if "usuario_id" in request.form:
        consulta = consulta.filter(ModuloFavorito.usuario_id == request.form["usuario_id"])
    registros = consulta.order_by(ModuloFavorito.modulo.nombre).offset(start).limit(rows_per_page).all()
    total = consulta.count()
    # Elaborar datos para DataTable
    data = []
    for resultado in registros:
        data.append(
            {
                "detalle": {
                    "nombre": resultado.Modulo.nombre,
                    "url": url_for("modulos.detail", modulo_id=resultado.Modulo.id),
                },
                "icono": resultado.Modulo.icono,
                "acciones": {
                    "remover": url_for("modulos_favoritos.remove", modulo_favorito_id=resultado.ModuloFavorito.id),
                },
            }
        )
    # Entregar JSON
    return output_datatable_json(draw, total, data)


@modulos_favoritos.route("/modulos_favoritos")
def list_active():
    """Listado de Módulos Favoritos activos"""
    return render_template(
        "modulos_favoritos/list.jinja2",
        filtros=json.dumps({"estatus": "A", "usuario_id": current_user.id}),
        titulo="Módulos Favoritos",
        estatus="A",
    )


@modulos_favoritos.route("/modulos_favoritos/agregar/<int:modulo_id>", methods=["GET", "POST"])
def add(modulo_id):
    """Agregar un nuevo Modulo al listado de Favoritos"""
    # Validar el Modulo ID
    modulo = Modulo.query.get_or_404(modulo_id)
    if modulo.estatus != "A":
        flash(f"El Módulo {modulo.nombre} se encuentra eliminado.", "warning")
        return redirect(url_for("modulos_favoritos.list_active"))
    # TODO: Validar si tiene acceso a este Módulo
    # TODO: Validar si el módulo no se encuentra ya agregado
    # Añadir el módulo al listado de Favoritos
    ModuloFavorito(
        modulo=modulo,
        usuario=current_user,
    ).save()
    flash(f"El Módulo {modulo.nombre} se añadió a la lista de favoritos.", "success")
    return redirect(url_for("modulos_favoritos.list_active"))


@modulos_favoritos.route("/modulos_favoritos/remover/<int:modulo_favorito_id>", methods=["GET", "POST"])
def remove(modulo_favorito_id):
    """Quitar un Modulo del listado de Favoritos"""
    # Validar el Modulo ID
    modulo_favorito = ModuloFavorito.query.get_or_404(modulo_favorito_id)
    # TODO: Remover vía SQL RAW el registro
    flash(f"El Módulo {modulo_favorito.modulo.nombre} se removió de su lista de favoritos.", "success")
    return redirect(url_for("modulos_favoritos.list_active"))

"""
not_escrituras, vistas
"""
import json
from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from lib.datatables import get_datatable_parameters, output_datatable_json
from lib.safe_string import safe_string, safe_message
from sqlalchemy.sql import or_

from plataforma_web.blueprints.bitacoras.models import Bitacora
from plataforma_web.blueprints.modulos.models import Modulo
from plataforma_web.blueprints.permisos.models import Permiso
from plataforma_web.blueprints.not_escrituras.forms import NotEscrituraForm
from plataforma_web.blueprints.usuarios.decorators import permission_required
from plataforma_web.blueprints.autoridades.models import Autoridad
from plataforma_web.blueprints.not_escrituras.models import NotEscritura

MODULO = "NOT ESCRITURAS"

not_escrituras = Blueprint("not_escrituras", __name__, template_folder="templates")


@not_escrituras.before_request
@login_required
@permission_required(MODULO, Permiso.VER)
def before_request():
    """Permiso por defecto"""


@not_escrituras.route("/not_escrituras/datatable_json", methods=["GET", "POST"])
def datatable_json():
    """DataTable JSON para listado de NOT ESCRITURAS"""
    # Tomar parámetros de Datatables
    draw, start, rows_per_page = get_datatable_parameters()
    # Consultar
    consulta = NotEscritura.query
    if "estatus" in request.form:
        consulta = consulta.filter_by(estatus=request.form["estatus"])
    else:
        consulta = consulta.filter_by(estatus="A")
    if "estado" in request.form:
        consulta = consulta.filter(NotEscritura.estado == request.form["estado"])
    # asegurarse que quien haga la petición sea Administrador, notaría o juzgado
    if current_user.can_admin(MODULO) is False:
        consulta = consulta.filter(or_(NotEscritura.notaria == current_user.autoridad, NotEscritura.juzgado == current_user.autoridad))
    registros = consulta.order_by(NotEscritura.id).offset(start).limit(rows_per_page).all()
    total = consulta.count()
    # Elaborar datos para DataTable
    data = []
    for resultado in registros:
        data.append(
            {
                "detalle": {
                    "id": resultado.id,
                    "url": url_for("not_escrituras.detail", not_escritura_id=resultado.id),
                },
                "notaria": resultado.notaria,
                "juzgado": resultado.juzgado,
            }
        )
    # Entregar JSON
    return output_datatable_json(draw, total, data)


@not_escrituras.route("/not_escrituras/activos")
def list_active():
    """Listado de Escrituras activos"""
    return render_template(
        "not_escrituras/list.jinja2",
        filtros=json.dumps({"estatus": "A"}),
        titulo="Escrituras",
        estatus="A",
    )


@not_escrituras.route("/not_escrituras")
def list_send():
    """Listado de Escrituras trabajando y enviadas"""
    return render_template(
        "not_escrituras/list_get_send.jinja2",
        titulo="Escrituras trabajdndo y eEnviadas",
    )


@not_escrituras.route("/not_escrituras/inactivos")
@permission_required(MODULO, Permiso.MODIFICAR)
def list_inactive():
    """Listado de Escrituras inactivos"""
    return render_template(
        "not_escrituras/list.jinja2",
        filtros=json.dumps({"estatus": "B"}),
        titulo="Escrituras inactivos",
        estatus="B",
    )


@not_escrituras.route("/not_escrituras/nuevo", methods=["GET", "POST"])
@permission_required(MODULO, Permiso.CREAR)
def new():
    """Nueva Escritura"""
    autoridad = current_user.autoridad
    if autoridad is None or autoridad.estatus != "A":
        flash("El juzgado/autoridad no existe o no es activa.", "warning")
        return redirect(url_for("not_escrituras.list_active"))
    if not autoridad.distrito.es_distrito_judicial:
        flash("El juzgado/autoridad no está en un distrito jurisdiccional.", "warning")
        return redirect(url_for("not_escrituras.list_active"))
    if not autoridad.es_notaria:
        flash("La autoridad no es una notaria.", "warning")
        return redirect(url_for("not_escrituras.list_active"))
    form = NotEscrituraForm()
    if form.validate_on_submit():
        juzgado = Autoridad.query.get_or_404(form.juzgado.data)
        not_escritura = NotEscritura(
            notaria=current_user.autoridad,
            juzgado=juzgado,
            estado=form.estado.data,
            contenido=form.contenido.data,
        )
        not_escritura.save()
        bitacora = Bitacora(
            modulo=Modulo.query.filter_by(nombre=MODULO).first(),
            usuario=current_user,
            descripcion=safe_message(f"Nueva Escritura {not_escritura.id}"),
            url=url_for("not_escrituras.detail", not_escritura_id=not_escritura.id),
        )
        bitacora.save()
        flash(bitacora.descripcion, "success")
        return redirect(bitacora.url)
    form.distrito.data = autoridad.distrito.nombre
    form.notaria.data = autoridad.descripcion
    buscar = None
    if current_user.autoridad.es_notaria:
        buscar = "JUZGADO"
    elif current_user.autoridad.es_jurisdiccional:
        buscar = "NOTARIA"
    return render_template("not_escrituras/new.jinja2", buscar=buscar, form=form)

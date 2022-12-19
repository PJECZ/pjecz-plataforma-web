"""
Archivo - Remesas, vistas
"""
import json
from datetime import date, datetime
from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required
from sqlalchemy import or_

from lib.datatables import get_datatable_parameters, output_datatable_json
from lib.safe_string import safe_message, safe_string
from plataforma_web.blueprints.usuarios.decorators import permission_required

from plataforma_web.blueprints.arc_remesas.models import ArcRemesa
from plataforma_web.blueprints.bitacoras.models import Bitacora
from plataforma_web.blueprints.modulos.models import Modulo
from plataforma_web.blueprints.permisos.models import Permiso

from plataforma_web.blueprints.usuarios.models import Usuario
from plataforma_web.blueprints.roles.models import Rol
from plataforma_web.blueprints.usuarios_roles.models import UsuarioRol

from plataforma_web.blueprints.arc_remesas.forms import ArcRemesaNewForm

from plataforma_web.blueprints.arc_archivos.views import ROL_JEFE_REMESA, ROL_ARCHIVISTA, ROL_SOLICITANTE


MODULO = "ARC REMESAS"


arc_remesas = Blueprint("arc_remesas", __name__, template_folder="templates")


@arc_remesas.before_request
@login_required
@permission_required(MODULO, Permiso.VER)
def before_request():
    """Permiso por defecto"""


@arc_remesas.route("/arc_remesas/datatable_json", methods=["GET", "POST"])
def datatable_json():
    """DataTable JSON para listado de Solicitudes"""
    # Tomar parámetros de Datatables
    draw, start, rows_per_page = get_datatable_parameters()
    # Consultar
    consulta = ArcRemesa.query
    if "estatus" in request.form:
        consulta = consulta.filter_by(estatus=request.form["estatus"])
    else:
        consulta = consulta.filter_by(estatus="A")
    if "juzgado_id" in request.form:
        consulta = consulta.filter_by(autoridad_id=int(request.form["juzgado_id"]))
    if "asignado_id" in request.form:
        consulta = consulta.filter_by(usuario_asignado_id=int(request.form["asignado_id"]))
    if "esta_archivado" in request.form:
        consulta = consulta.filter_by(esta_archivado=bool(request.form["esta_archivado"]))
    if "omitir_cancelados" in request.form:
        consulta = consulta.filter(ArcRemesa.estado != "CANCELADO")
    if "omitir_archivados" in request.form:
        consulta = consulta.filter(ArcRemesa.esta_archivado != True)
    if "mostrar_archivados" in request.form:
        consulta = consulta.filter_by(esta_archivado=True)
    # Ordena los registros resultantes por id descendientes para ver los más recientemente capturados
    if "orden_acendente" in request.form:
        registros = consulta.order_by(ArcRemesa.id.desc()).offset(start).limit(rows_per_page).all()
    else:
        registros = consulta.order_by(ArcRemesa.id).offset(start).limit(rows_per_page).all()
    total = consulta.count()
    # Elaborar datos para DataTable
    data = []
    for resultado in registros:
        data.append(
            {
                "remesa": {
                    "id": resultado.id,
                    "url": url_for("arc_remesas.detail", remesa_id=resultado.id),
                },
                "juzgado": {
                    "clave": resultado.autoridad.clave,
                    "nombre": resultado.autoridad.descripcion_corta,
                    "url": url_for("autoridades.detail", autoridad_id=resultado.autoridad.id),
                },
                "tiempo": resultado.creado.strftime("%Y-%m-%d %H:%M:%S"),
                "anio": resultado.anio,
                "num_oficio": resultado.num_oficio,
                "num_docs": 2,
                "estado": resultado.estado,
                "asignado": {
                    "nombre": "SIN ASIGNAR" if resultado.usuario_asignado is None else resultado.usuario_asignado.nombre,
                    "url": "" if resultado.usuario_asignado is None else url_for("usuarios.detail", usuario_id=resultado.usuario_asignado.id),
                },
            }
        )
    # Entregar JSON
    return output_datatable_json(draw, total, data)


@arc_remesas.route("/arc_remesas/<int:remesa_id>")
def detail(remesa_id):
    """Detalle de una Remesa"""


@arc_remesas.route("/arc_remesas/nueva", methods=["GET", "POST"])
@permission_required(MODULO, Permiso.CREAR)
def new():
    """Nueva Remesa"""

    form = ArcRemesaNewForm()
    if form.validate_on_submit():
        if form.anio.data < 1950 or form.anio.data > date.today().year:
            flash(f"El año se encuntra fuera de un rango permitido 1950-{date.today().year}.", "warning")
        elif not current_user.can_admin(MODULO) and ROL_SOLICITANTE not in current_user.get_roles():
            flash(f"Solo se pueden crear nuevas remesas por el Administrador o {ROL_SOLICITANTE}.", "warning")
        else:
            remesa = ArcRemesa(
                autoridad=current_user.autoridad,
                esta_archivado=False,
                anio=int(form.anio.data),
                num_oficio=safe_string(form.num_oficio.data),
                estado="PENDIENTE",
            )
            remesa.save()
            bitacora = Bitacora(
                modulo=Modulo.query.filter_by(nombre=MODULO).first(),
                usuario=current_user,
                descripcion=safe_message(f"Nueva Remesa creada {remesa.id}"),
                url=url_for("arc_archivos.list_active"),
            )
            bitacora.save()
            flash(bitacora.descripcion, "success")
            return redirect(bitacora.url)
    return render_template("arc_remesas/new.jinja2", form=form)

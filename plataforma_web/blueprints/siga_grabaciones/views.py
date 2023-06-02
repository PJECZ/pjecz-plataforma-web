"""
SIGA Grabaciones, vistas
"""
import json
from flask import Blueprint, flash, redirect, request, render_template, url_for
from flask_login import current_user, login_required

from lib.datatables import get_datatable_parameters, output_datatable_json
from lib.safe_string import safe_string, safe_text, safe_message
from plataforma_web.blueprints.usuarios.decorators import permission_required

from plataforma_web.blueprints.bitacoras.models import Bitacora
from plataforma_web.blueprints.modulos.models import Modulo
from plataforma_web.blueprints.siga_grabaciones.models import SIGAGrabacion
from plataforma_web.blueprints.materias.models import Materia
from plataforma_web.blueprints.permisos.models import Permiso

from plataforma_web.blueprints.siga_grabaciones.forms import SIGAGrabacionEditForm

MODULO = "SIGA GRABACIONES"

siga_grabaciones = Blueprint("siga_grabaciones", __name__, template_folder="templates")


@siga_grabaciones.before_request
@login_required
@permission_required(MODULO, Permiso.VER)
def before_request():
    """Permiso por defecto"""


@siga_grabaciones.route("/siga_grabaciones/datatable_json", methods=["GET", "POST"])
def datatable_json():
    """DataTable JSON para listado de siga_grabaciones"""
    # Tomar parámetros de Datatables
    draw, start, rows_per_page = get_datatable_parameters()
    # Consultar
    consulta = SIGAGrabacion.query
    if "estatus" in request.form:
        consulta = consulta.filter_by(estatus=request.form["estatus"])
    else:
        consulta = consulta.filter_by(estatus="A")
    if "id" in request.form:
        consulta = consulta.filter(SIGAGrabacion.id == request.form["id"])
    if "expediente" in request.form:
        consulta = consulta.filter(SIGAGrabacion.expediente.contains(request.form["expediente"]))
    if "desde" in request.form:
        consulta = consulta.filter(SIGAGrabacion.inicio >= request.form["desde"])
    if "hasta" in request.form:
        consulta = consulta.filter(SIGAGrabacion.inicio <= request.form["hasta"] + " 23:59:59")
    if "sala_id" in request.form:
        consulta = consulta.filter(SIGAGrabacion.siga_sala_id == request.form["sala_id"])
    if "autoridad_id" in request.form:
        consulta = consulta.filter(SIGAGrabacion.autoridad_id == request.form["autoridad_id"])
    if "materia_id" in request.form:
        consulta = consulta.filter(SIGAGrabacion.materia_id == request.form["materia_id"])
    if "estado" in request.form:
        consulta = consulta.filter_by(estado=request.form["estado"])
    registros = consulta.order_by(SIGAGrabacion.id.desc()).offset(start).limit(rows_per_page).all()
    total = consulta.count()
    # Elaborar datos para DataTable
    data = []
    for resultado in registros:
        data.append(
            {
                "id": {
                    "id": resultado.id,
                    "url": url_for("siga_grabaciones.detail", siga_grabacion_id=resultado.id),
                },
                "tiempo": {
                    "inicio": resultado.inicio.strftime("%Y/%m/%d - %H:%M:%S"),
                    "termino": resultado.termino.strftime("%Y/%m/%d - %H:%M:%S"),
                },
                "sala": {
                    "nombre": resultado.siga_sala.clave,
                    "url": url_for("siga_salas.detail", siga_sala_id=resultado.siga_sala.id) if current_user.can_view("SIGA SALAS") else "",
                    "tooltip": resultado.siga_sala.domicilio.edificio,
                },
                "inicio": resultado.inicio.strftime("%Y/%m/%d - %H:%M:%S"),
                "termino": resultado.termino.strftime("%Y/%m/%d - %H:%M:%S"),
                "autoridad_materia": {
                    "autoridad": {
                        "nombre": resultado.autoridad.clave,
                        "url": url_for("autoridades.detail", autoridad_id=resultado.autoridad.id) if current_user.can_view("AUTORIDADES") else "",
                    },
                    "materia": {
                        "nombre": resultado.materia.nombre,
                        "url": url_for("materias.detail", materia_id=resultado.materia.id) if current_user.can_view("MATERIAS") else "",
                    },
                },
                "autoridad": {
                    "nombre": resultado.autoridad.clave,
                    "url": url_for("autoridades.detail", autoridad_id=resultado.autoridad.id) if current_user.can_view("AUTORIDADES") else "",
                },
                "materia": {
                    "nombre": resultado.materia.nombre,
                    "url": url_for("materias.detail", materia_id=resultado.materia.id) if current_user.can_view("MATERIAS") else "",
                },
                "expediente": resultado.expediente,
                "duracion": str(resultado.duracion),
                "duracion_tamanio": {
                    "duracion": str(resultado.duracion),
                    "tamanio": f"{resultado.tamanio / (1024 * 1024):0.2f}",
                },
                "estado": resultado.estado,
                "nota": resultado.nota,
            }
        )
    # Entregar JSON
    return output_datatable_json(draw, total, data)


@siga_grabaciones.route("/siga_grabaciones")
def list_active():
    """Listado de Grabaciones activas"""
    return render_template(
        "siga_grabaciones/list.jinja2",
        filtros=json.dumps({"estatus": "A"}),
        titulo="SIGA Grabaciones",
        estatus="A",
        materias=Materia.query.filter_by(estatus="A").order_by(Materia.nombre).all(),
        estados_grabaciones=SIGAGrabacion.ESTADOS,
    )


@siga_grabaciones.route("/siga_grabaciones/inactivos")
@permission_required(MODULO, Permiso.MODIFICAR)
def list_inactive():
    """Listado de Grabaciones inactivas"""
    return render_template(
        "siga_grabaciones/list.jinja2",
        filtros=json.dumps({"estatus": "B"}),
        titulo="SIGA Grabaciones Inactivas",
        estatus="B",
        materias=Materia.query.filter_by(estatus="A").order_by(Materia.nombre).all(),
        estados_grabaciones=SIGAGrabacion.ESTADOS,
    )


@siga_grabaciones.route("/siga_grabaciones/<int:siga_grabacion_id>")
def detail(siga_grabacion_id):
    """Detalle de un SIGAGrabacion"""
    siga_grabacion = SIGAGrabacion.query.get_or_404(siga_grabacion_id)
    return render_template(
        "siga_grabaciones/detail.jinja2",
        siga_grabacion=siga_grabacion,
    )


@siga_grabaciones.route("/siga_grabaciones/editar_nota/<int:siga_grabacion_id>", methods=["GET", "POST"])
def edit_note(siga_grabacion_id):
    """Detalle de un SIGAGrabacion"""
    siga_grabacion = SIGAGrabacion.query.get_or_404(siga_grabacion_id)

    form = SIGAGrabacionEditForm()
    if form.validate_on_submit():
        siga_grabacion.nota = safe_text(form.nota.data)
        siga_grabacion.save()
        bitacora = Bitacora(
            modulo=Modulo.query.filter_by(nombre=MODULO).first(),
            usuario=current_user,
            descripcion=safe_message(f"Editada la Nota de la SIGA Grabación {siga_grabacion.id}"),
            url=url_for("siga_grabaciones.detail", siga_grabacion_id=siga_grabacion.id),
        )
        bitacora.save()
        flash(bitacora.descripcion, "success")
        return redirect(bitacora.url)

    # Pasar los datos de solo lectura
    form.sala.data = siga_grabacion.siga_sala.clave
    form.expediente.data = siga_grabacion.expediente
    form.inicio.data = siga_grabacion.inicio.strftime("%Y/%m/%d - %H:%M:%S")
    form.nota.data = siga_grabacion.nota

    return render_template(
        "siga_grabaciones/edit.jinja2",
        siga_grabacion=siga_grabacion,
        form=form,
    )

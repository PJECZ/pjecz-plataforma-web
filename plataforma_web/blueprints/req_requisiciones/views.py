"""
Requisiciones Requisiciones, vistas
"""
from datetime import datetime
import json
from flask import Blueprint, flash, jsonify, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from lib.datatables import get_datatable_parameters, output_datatable_json
from lib.safe_string import safe_string, safe_message

from plataforma_web.blueprints.bitacoras.models import Bitacora
from plataforma_web.blueprints.modulos.models import Modulo
from plataforma_web.blueprints.permisos.models import Permiso
from plataforma_web.blueprints.usuarios.decorators import permission_required
from plataforma_web.blueprints.req_requisiciones.models import ReqRequisicion
from plataforma_web.blueprints.req_requisiciones.forms import ReqRequisicionNewForm
from plataforma_web.blueprints.req_requisiciones.forms import ArticulosForm
from plataforma_web.blueprints.autoridades.models import Autoridad
from plataforma_web.blueprints.req_catalogos.models import ReqCatalogo
from plataforma_web.blueprints.req_requisiciones_registros.models import ReqRequisicionRegistro
from plataforma_web.extensions import db

MODULO = "REQ REQUISICIONES"

req_requisiciones = Blueprint("req_requisiciones", __name__, template_folder="templates")


@req_requisiciones.before_request
@login_required
@permission_required(MODULO, Permiso.VER)
def before_request():
    """Permiso por defecto"""


@req_requisiciones.route("/req_requisiciones/datatable_json", methods=["GET", "POST"])
def datatable_json():
    """DataTable JSON para listado de Requisiciones"""
    # Tomar parámetros de Datatables
    draw, start, rows_per_page = get_datatable_parameters()
    # Consultar
    consulta = ReqRequisicion.query
    if "estatus" in request.form:
        consulta = consulta.filter_by(estatus=request.form["estatus"])
    else:
        consulta = consulta.filter_by(estatus="A")
    registros = consulta.order_by(ReqRequisicion.id).offset(start).limit(rows_per_page).all()
    total = consulta.count()
    # Elaborar datos para DataTable
    data = []
    for resultado in registros:
        data.append(
            {
                "fecha": resultado.fecha,
                "detalle": {
                    "consecutivo": resultado.consecutivo,
                    "url": url_for("req_requisiciones.detail", req_requisicion_id=resultado.id),
                },
                "observaciones": resultado.observaciones,
            }
        )
    # Entregar JSON
    return output_datatable_json(draw, total, data)


@req_requisiciones.route("/req_requisiciones")
def list_active():
    """Listado de Requisiciones activos"""
    return render_template(
        "req_requisiciones/list.jinja2",
        filtros=json.dumps({"estatus": "A"}),
        titulo="Requisiciones",
        estatus="A",
    )


@req_requisiciones.route("/req_requisiciones/inactivos")
@permission_required(MODULO, Permiso.MODIFICAR)
def list_inactive():
    """Listado de Requisiciones inactivas"""
    return render_template(
        "req_requisiciones/list.jinja2",
        filtros=json.dumps({"estatus": "B"}),
        titulo="Listado de requisiciones inactivas",
        estatus="B",
    )


@req_requisiciones.route("/req_requisiciones/nuevo", methods=["GET", "POST"])
@permission_required(MODULO, Permiso.CREAR)
def new():
    """Requisiciones nueva"""
    form = ReqRequisicionNewForm()
    form.area.choices = [("", "")] + [(a.id, a.descripcion) for a in Autoridad.query.order_by("descripcion")]
    form.codigoTmp.choices = [("", "")] + [(c.id, c.codigo + " - " + c.descripcion) for c in ReqCatalogo.query.order_by("descripcion")]
    form.claveTmp.choices = [("", "")] + [("INS", "INSUFICIENCIA")] + [("REP", "REPOSICION DE BIENES")] + [("OBS", "OBSOLESENCIA")] + [("AMP", "AMPLIACION COBERTURA DEL SERVICIO")] + [("NUE", "NUEVO PROYECTO")]
    if form.validate_on_submit():
        # Guardar requisicion
        req_requisicion = ReqRequisicion(
            usuario=current_user,
            autoridad_id=form.area.data,
            estado="CREADO",
            observaciones=safe_string(form.observaciones.data, max_len=256, to_uppercase=False, save_enie=True),
            fecha=datetime.now(),
            consecutivo=form.gasto.data,
            glosa=form.glosa.data,
            programa=form.programa.data,
            fuente=form.fuente.data,
            area="area final",
            fecha_requerida=form.fechaRequerida.data,
        )
        req_requisicion.save()
        # Guardar los registros de la requisición
        for registros in form.articulos:
            if registros.codigo.data != None:
                req_requisicion_registro = ReqRequisicionRegistro(
                    req_requisicion_id=req_requisicion.id,
                    req_catalogo_id=registros.codigo.data,
                    clave=registros.clave.data,
                    cantidad=registros.cantidad.data,
                    detalle=registros.detalle.data,
                )
                req_requisicion_registro.save()

        # Guardar en la bitacora
        bitacora = Bitacora(
            modulo=Modulo.query.filter_by(nombre=MODULO).first(),
            usuario=current_user,
            descripcion=safe_message(f"Requisicion creada {req_requisicion.observaciones}"),
            url=url_for("req_requisiciones.detail", req_requisicion_id=req_requisicion.id),
        )
        bitacora.save()
        flash(bitacora.descripcion, "success")
        return redirect(bitacora.url)
    return render_template("req_requisiciones/new.jinja2", titulo="Requisicion nueva", form=form)


@req_requisiciones.route("/req_requisiciones/<int:req_requisicion_id>")
def detail(req_requisicion_id):
    """Detalle de una Requisicion"""
    req_requisicion = ReqRequisicion.query.get_or_404(req_requisicion_id)
    articulos = db.session.query(ReqRequisicionRegistro, ReqCatalogo).filter_by(req_requisicion_id=req_requisicion_id).join(ReqCatalogo).all()
    return render_template("req_requisiciones/detail.jinja2", req_requisicion=req_requisicion, req_requisicion_registro=articulos)


@req_requisiciones.route("/req_requisiciones/buscarRegistros/", methods=["GET"])
def buscarRegistros():
    args = request.args
    registro = ReqCatalogo.query.get_or_404(args.get("req_catalogo_id"))
    return ReqCatalogo.object_as_dict(registro)

"""
Domicilios, vistas
"""
import json
from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from lib import datatables
from lib.safe_string import safe_string, safe_message

from plataforma_web.blueprints.permisos.models import Permiso
from plataforma_web.blueprints.usuarios.decorators import permission_required

from plataforma_web.blueprints.bitacoras.models import Bitacora
from plataforma_web.blueprints.modulos.models import Modulo
from plataforma_web.blueprints.domicilios.models import Domicilio

from plataforma_web.blueprints.domicilios.forms import DomicilioForm, DomicilioSearchForm

MODULO = "DOMICILIOS"

domicilios = Blueprint("domicilios", __name__, template_folder="templates")


@domicilios.route("/domicilios")
@login_required
@permission_required(MODULO, Permiso.VER)
def list_active():
    """Listado de Domicilios activos"""
    activos = Domicilio.query.filter(Domicilio.estatus == "A").all()
    return render_template(
        "domicilios/list.jinja2",
        clientes=activos,
        titulo="Domicilios",
        estatus="A",
        filtros=json.dumps({"estatus": "A"}),
    )


@domicilios.route("/domicilios/inactivos")
@login_required
@permission_required(MODULO, Permiso.MODIFICAR)
def list_inactive():
    """Listado de Domicilios inactivos"""
    inactivos = Domicilio.query.filter(Domicilio.estatus == "B").all()
    return render_template(
        "domicilios/list.jinja2",
        clientes=inactivos,
        titulo="Domicilios inactivos",
        estatus="B",
        filtros=json.dumps({"estatus": "B"}),
    )


@domicilios.route("/domicilios/<int:domicilio_id>")
@login_required
@permission_required(MODULO, Permiso.VER)
def detail(domicilio_id):
    """Detalle de un Domicilio"""
    domicilio = Domicilio.query.get_or_404(domicilio_id)
    return render_template("domicilios/detail.jinja2", domicilio=domicilio)


@domicilios.route("/domicilios/buscar", methods=["GET", "POST"])
def search():
    """Buscar un Domicilio"""
    form_search = DomicilioSearchForm()
    if form_search.validate_on_submit():
        busqueda = {"estatus": "A"}
        titulos = []
        # Búsqueda por campos
        if form_search.calle.data:
            busqueda["calle"] = form_search.calle.data
            titulos.append("calle " + busqueda["calle"])
        if form_search.colonia.data:
            busqueda["colonia"] = form_search.colonia.data
            titulos.append("colonia " + busqueda["colonia"])
        if form_search.cp.data:
            busqueda["cp"] = form_search.cp.data
            titulos.append("cp " + str(busqueda["cp"]))
        # Mostrar resultados
        return render_template(
            "domicilios/list.jinja2",
            filtros=json.dumps(busqueda),
            titulo="Domicilios con " + ", ".join(titulos),
        )
    return render_template("domicilios/search.jinja2", form=form_search)


@domicilios.route("/domicilios/nuevo", methods=["GET", "POST"])
@login_required
@permission_required(MODULO, Permiso.CREAR)
def new():
    """Nuevo Domicilio"""
    form = DomicilioForm()
    if form.validate_on_submit():
        estado = safe_string(form.estado.data, max_len=64)
        municipio = safe_string(form.municipio.data, max_len=64)
        calle = safe_string(form.calle.data, max_len=256)
        num_ext = safe_string(form.num_ext.data, max_len=24)
        num_int = safe_string(form.num_int.data, max_len=24)
        colonia = safe_string(form.colonia.data, max_len=256)
        cp = form.cp.data
        completo = f"{calle} #{num_ext} {num_int}, {colonia}, {municipio}, {estado}, C.P. {cp}"
        domicilio = Domicilio(
            estado=estado,
            municipio=municipio,
            calle=calle,
            num_ext=num_ext,
            num_int=num_int,
            colonia=colonia,
            cp=cp,
            completo=completo,
        ).save()
        bitacora = Bitacora(
            modulo=Modulo.query.filter_by(nombre=MODULO).first(),
            usuario=current_user,
            descripcion=safe_message(f"Nuevo Domicilio {completo}"),
            url=url_for("domicilios.detail", domicilio_id=domicilio.id),
        )
        bitacora.save()
        flash(bitacora.descripcion, "success")
        return redirect(bitacora.url)
    return render_template("domicilios/new.jinja2", form=form)


@domicilios.route("/domicilios/edicion/<int:domicilio_id>", methods=["GET", "POST"])
@login_required
@permission_required(MODULO, Permiso.MODIFICAR)
def edit(domicilio_id):
    """Editar Domicilio"""
    domicilio = Domicilio.query.get_or_404(domicilio_id)
    form = DomicilioForm()
    if form.validate_on_submit():
        domicilio.estado = safe_string(form.estado.data, max_len=64)
        domicilio.municipio = safe_string(form.municipio.data, max_len=64)
        domicilio.calle = safe_string(form.calle.data, max_len=256)
        domicilio.num_ext = safe_string(form.num_ext.data, max_len=24)
        domicilio.num_int = safe_string(form.num_int.data, max_len=24)
        domicilio.colonia = safe_string(form.colonia.data, max_len=256)
        domicilio.cp = form.cp.data
        domicilio.completo = f"{domicilio.calle} #{domicilio.num_ext} {domicilio.num_int}, {domicilio.colonia}, {domicilio.municipio}, {domicilio.estado}, C.P. {domicilio.cp}"
        domicilio.save()
        bitacora = Bitacora(
            modulo=Modulo.query.filter_by(nombre=MODULO).first(),
            usuario=current_user,
            descripcion=safe_message(f"Editado el Domicilio {domicilio.completo}"),
            url=url_for("domicilios.detail", domicilio_id=domicilio.id),
        )
        bitacora.save()
        flash(bitacora.descripcion, "success")
        return redirect(bitacora.url)
    form.estado.data = domicilio.estado
    form.municipio.data = domicilio.municipio
    form.calle.data = domicilio.calle
    form.num_ext.data = domicilio.num_ext
    form.num_int.data = domicilio.num_int
    form.colonia.data = domicilio.colonia
    form.cp.data = domicilio.cp
    return render_template("domicilios/edit.jinja2", form=form, domicilio=domicilio)


@domicilios.route("/domicilios/eliminar/<int:domicilio_id>")
@login_required
@permission_required(MODULO, Permiso.MODIFICAR)
def delete(domicilio_id):
    """Eliminar Domicilio"""
    domicilio = Domicilio.query.get_or_404(domicilio_id)
    if domicilio.estatus == "A":
        domicilio.delete()
        bitacora = Bitacora(
            modulo=Modulo.query.filter_by(nombre=MODULO).first(),
            usuario=current_user,
            descripcion=safe_message(f"Eliminado el Domicilio {domicilio.calle}"),
            url=url_for("domicilios.detail", domicilio_id=domicilio.id),
        )
        bitacora.save()
        flash(bitacora.descripcion, "success")
    return redirect(url_for("domicilios.detail", domicilio_id=domicilio_id))


@domicilios.route("/domicilios/recuperar/<int:domicilio_id>")
@login_required
@permission_required(MODULO, Permiso.MODIFICAR)
def recover(domicilio_id):
    """Recuperar Domicilio"""
    domicilio = Domicilio.query.get_or_404(domicilio_id)
    if domicilio.estatus == "B":
        domicilio.recover()
        bitacora = Bitacora(
            modulo=Modulo.query.filter_by(nombre=MODULO).first(),
            usuario=current_user,
            descripcion=safe_message(f"Recuperado el Servicio {domicilio.calle}"),
            url=url_for("domicilios.detail", domicilio_id=domicilio.id),
        )
        bitacora.save()
        flash(bitacora.descripcion, "success")
    return redirect(url_for("domicilios.detail", domicilio_id=domicilio_id))


@domicilios.route("/domicilios/datatable_json", methods=["GET", "POST"])
def datatable_json():
    """DataTable JSON para listado de clientes"""
    # Tomar parámetros de Datatables
    draw, start, rows_per_page = datatables.get_parameters()
    # Consultar
    consulta = Domicilio.query
    if "estatus" in request.form:
        consulta = consulta.filter_by(estatus=request.form["estatus"])
    else:
        consulta = consulta.filter_by(estatus="A")
    if "calle" in request.form:
        consulta = consulta.filter(Domicilio.calle.like("%" + safe_string(request.form["calle"]) + "%"))
    if "colonia" in request.form:
        consulta = consulta.filter(Domicilio.colonia.like("%" + safe_string(request.form["colonia"]) + "%"))
    if "cp" in request.form:
        consulta = consulta.filter(Domicilio.cp.like("%" + safe_string(request.form["cp"]) + "%"))
    registros = consulta.order_by(Domicilio.calle.desc()).offset(start).limit(rows_per_page).all()
    total = consulta.count()
    # Elaborar datos para DataTable
    data = []
    for domicilio in registros:
        data.append(
            {
                "estado": domicilio.estado,
                "municipio": domicilio.municipio,
                "calle": {
                    "id": domicilio.id,
                    "url": url_for("domicilios.detail", domicilio_id=domicilio.id),
                    "descripcion": domicilio.calle,
                },
                "num_ext": domicilio.num_ext,
                "num_int": domicilio.num_int,
                "colonia": domicilio.colonia,
                "cp": domicilio.cp,
            }
        )
    # Entregar JSON
    return datatables.output(draw, total, data)

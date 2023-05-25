"""
Domicilios, vistas
"""
import json
from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required
from sqlalchemy import or_

from lib.datatables import get_datatable_parameters, output_datatable_json
from lib.safe_string import safe_string, safe_message
from plataforma_web.blueprints.usuarios.decorators import permission_required

from plataforma_web.blueprints.bitacoras.models import Bitacora
from plataforma_web.blueprints.domicilios.forms import DomicilioForm, DomicilioSearchForm
from plataforma_web.blueprints.domicilios.models import Domicilio
from plataforma_web.blueprints.distritos.models import Distrito
from plataforma_web.blueprints.modulos.models import Modulo
from plataforma_web.blueprints.permisos.models import Permiso

MODULO = "DOMICILIOS"

domicilios = Blueprint("domicilios", __name__, template_folder="templates")


@domicilios.before_request
@login_required
@permission_required(MODULO, Permiso.VER)
def before_request():
    """Permiso por defecto"""


@domicilios.route("/domicilios/datatable_json", methods=["GET", "POST"])
def datatable_json():
    """DataTable JSON para listado de Domicilios"""
    # Tomar parámetros de Datatables
    draw, start, rows_per_page = get_datatable_parameters()
    # Consultar
    consulta = Domicilio.query
    if "estatus" in request.form:
        consulta = consulta.filter_by(estatus=request.form["estatus"])
    else:
        consulta = consulta.filter_by(estatus="A")
    if "edificio" in request.form:
        consulta = consulta.filter(Domicilio.edificio.contains(safe_string(request.form["edificio"])))
    if "estado" in request.form:
        consulta = consulta.filter(Domicilio.estado.contains(safe_string(request.form["estado"])))
    if "municipio" in request.form:
        consulta = consulta.filter(Domicilio.municipio.contains(safe_string(request.form["municipio"])))
    if "calle" in request.form:
        consulta = consulta.filter(Domicilio.calle.contains(safe_string(request.form["calle"])))
    if "colonia" in request.form:
        consulta = consulta.filter(Domicilio.colonia.contains(safe_string(request.form["colonia"])))
    if "cp" in request.form:
        consulta = consulta.filter_by(colonia=int(request.form["cp"]))
    registros = consulta.order_by(Domicilio.edificio).offset(start).limit(rows_per_page).all()
    total = consulta.count()
    # Elaborar datos para DataTable
    data = []
    for resultado in registros:
        data.append(
            {
                "detalle": {
                    "edificio": resultado.edificio,
                    "url": url_for("domicilios.detail", domicilio_id=resultado.id),
                },
                "estado": resultado.estado,
                "municipio": resultado.municipio,
                "calle": resultado.calle,
                "num_ext": resultado.num_ext,
                "num_int": resultado.num_int,
                "colonia": resultado.colonia,
                "cp": resultado.cp,
            }
        )
    # Entregar JSON
    return output_datatable_json(draw, total, data)


@domicilios.route("/domicilios")
def list_active():
    """Listado de Modulo activos"""
    return render_template(
        "domicilios/list.jinja2",
        filtros=json.dumps({"estatus": "A"}),
        titulo="Domicilios",
        estatus="A",
    )


@domicilios.route("/domicilios/inactivos")
@permission_required(MODULO, Permiso.MODIFICAR)
def list_inactive():
    """Listado de Domicilios inactivos"""
    return render_template(
        "domicilios/list.jinja2",
        filtros=json.dumps({"estatus": "B"}),
        titulo="Domicilios inactivos",
        estatus="B",
    )


@domicilios.route("/domicilios/buscar", methods=["GET", "POST"])
def search():
    """Buscar Domicilios"""
    form_search = DomicilioSearchForm()
    if form_search.validate_on_submit():
        busqueda = {"estatus": "A"}
        titulos = []
        if form_search.edificio.data:
            edificio = safe_string(form_search.edificio.data)
            if edificio != "":
                busqueda["edificio"] = edificio
                titulos.append("edificio " + edificio)
        if form_search.estado.data:
            estado = safe_string(form_search.estado.data)
            if estado != "":
                busqueda["estado"] = estado
                titulos.append("estado " + estado)
        if form_search.municipio.data:
            municipio = safe_string(form_search.municipio.data)
            if municipio != "":
                busqueda["municipio"] = municipio
                titulos.append("municipio " + municipio)
        if form_search.calle.data:
            calle = safe_string(form_search.calle.data)
            if calle != "":
                busqueda["calle"] = calle
                titulos.append("calle " + calle)
        if form_search.colonia.data:
            colonia = safe_string(form_search.colonia.data)
            if colonia != "":
                busqueda["colonia"] = colonia
                titulos.append("colonia " + colonia)
        if form_search.cp.data:
            cp = int(form_search.cp.data)
            if cp:
                busqueda["cp"] = cp
                titulos.append("C.P. " + cp)
        return render_template(
            "domicilios/list.jinja2",
            filtros=json.dumps(busqueda),
            titulo="Domicilios con " + ", ".join(titulos),
            estatus="A",
        )
    return render_template("domicilios/search.jinja2", form=form_search)


@domicilios.route("/domicilios/<int:domicilio_id>")
def detail(domicilio_id):
    """Detalle de un Domicilio"""
    domicilio = Domicilio.query.get_or_404(domicilio_id)
    return render_template("domicilios/detail.jinja2", domicilio=domicilio)


@domicilios.route("/domicilios/nuevo", methods=["GET", "POST"])
@permission_required(MODULO, Permiso.CREAR)
def new():
    """Nuevo Domicilio"""
    form = DomicilioForm()
    if form.validate_on_submit():
        es_valido = True
        # Validar que el edificio no se repita
        edificio = safe_string(form.edificio.data, max_len=64, save_enie=True)
        if Domicilio.query.filter_by(edificio=edificio).first():
            es_valido = False
            flash("El edificio ya está en uso. Debe de ser único.", "warning")
        # Si es valido, insertar
        if es_valido:
            estado = safe_string(form.estado.data, max_len=64, save_enie=True)
            municipio = safe_string(form.municipio.data, max_len=64, save_enie=True)
            calle = safe_string(form.calle.data, max_len=256, save_enie=True)
            num_ext = safe_string(form.num_ext.data, max_len=24)
            num_int = safe_string(form.num_int.data, max_len=24)
            colonia = safe_string(form.colonia.data, max_len=256, save_enie=True)
            cp = form.cp.data
            completo = f"{calle} #{num_ext} {num_int}, {colonia}, {municipio}, {estado}, C.P. {cp}"
            domicilio = Domicilio(
                edificio=edificio,
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
                descripcion=safe_message(f"Nuevo Domicilio {edificio}"),
                url=url_for("domicilios.detail", domicilio_id=domicilio.id),
            )
            bitacora.save()
            flash(bitacora.descripcion, "success")
            return redirect(bitacora.url)
    return render_template("domicilios/new.jinja2", form=form)


@domicilios.route("/domicilios/edicion/<int:domicilio_id>", methods=["GET", "POST"])
@permission_required(MODULO, Permiso.MODIFICAR)
def edit(domicilio_id):
    """Editar Domicilio"""
    domicilio = Domicilio.query.get_or_404(domicilio_id)
    form = DomicilioForm()
    if form.validate_on_submit():
        es_valido = True
        # Si se cambia el edificio, validar que no se repita
        edificio = safe_string(form.edificio.data, max_len=64, save_enie=True)
        if domicilio.edificio != edificio:
            domicilio_existente = Domicilio.query.filter_by(edificio=edificio).first()
            if domicilio_existente and domicilio_existente.id != domicilio_id:
                es_valido = False
                flash("El edificio ya está en uso. Debe de ser único.", "warning")
        # Si es valido, actualizar
        if es_valido:
            domicilio.edificio = edificio
            domicilio.estado = safe_string(form.estado.data, max_len=64, save_enie=True)
            domicilio.municipio = safe_string(form.municipio.data, max_len=64, save_enie=True)
            domicilio.calle = safe_string(form.calle.data, max_len=256, save_enie=True)
            domicilio.num_ext = safe_string(form.num_ext.data, max_len=24)
            domicilio.num_int = safe_string(form.num_int.data, max_len=24)
            domicilio.colonia = safe_string(form.colonia.data, max_len=256, save_enie=True)
            domicilio.cp = form.cp.data
            domicilio.completo = f"{domicilio.calle} #{domicilio.num_ext} {domicilio.num_int}, {domicilio.colonia}, {domicilio.municipio}, {domicilio.estado}, C.P. {domicilio.cp}"
            domicilio.save()
            bitacora = Bitacora(
                modulo=Modulo.query.filter_by(nombre=MODULO).first(),
                usuario=current_user,
                descripcion=safe_message(f"Editado el Domicilio {domicilio.edificio}"),
                url=url_for("domicilios.detail", domicilio_id=domicilio.id),
            )
            bitacora.save()
            flash(bitacora.descripcion, "success")
            return redirect(bitacora.url)
    form.edificio.data = domicilio.edificio
    form.estado.data = domicilio.estado
    form.municipio.data = domicilio.municipio
    form.calle.data = domicilio.calle
    form.num_ext.data = domicilio.num_ext
    form.num_int.data = domicilio.num_int
    form.colonia.data = domicilio.colonia
    form.cp.data = domicilio.cp
    return render_template("domicilios/edit.jinja2", form=form, domicilio=domicilio)


@domicilios.route("/domicilios/eliminar/<int:domicilio_id>")
@permission_required(MODULO, Permiso.MODIFICAR)
def delete(domicilio_id):
    """Eliminar Domicilio"""
    domicilio = Domicilio.query.get_or_404(domicilio_id)
    if domicilio.estatus == "A":
        domicilio.delete()
        bitacora = Bitacora(
            modulo=Modulo.query.filter_by(nombre=MODULO).first(),
            usuario=current_user,
            descripcion=safe_message(f"Eliminado el Domicilio {domicilio.edificio}"),
            url=url_for("domicilios.detail", domicilio_id=domicilio.id),
        )
        bitacora.save()
        flash(bitacora.descripcion, "success")
    return redirect(url_for("domicilios.detail", domicilio_id=domicilio_id))


@domicilios.route("/domicilios/recuperar/<int:domicilio_id>")
@permission_required(MODULO, Permiso.MODIFICAR)
def recover(domicilio_id):
    """Recuperar Domicilio"""
    domicilio = Domicilio.query.get_or_404(domicilio_id)
    if domicilio.estatus == "B":
        domicilio.recover()
        bitacora = Bitacora(
            modulo=Modulo.query.filter_by(nombre=MODULO).first(),
            usuario=current_user,
            descripcion=safe_message(f"Recuperado el Servicio {domicilio.edificio}"),
            url=url_for("domicilios.detail", domicilio_id=domicilio.id),
        )
        bitacora.save()
        flash(bitacora.descripcion, "success")
    return redirect(url_for("domicilios.detail", domicilio_id=domicilio_id))


@domicilios.route("/domicilios/edificios_json", methods=["POST"])
def query_edificios_json():
    """Proporcionar el JSON de edificios para elegir un Edificio con un Select2"""
    consulta = Domicilio.query.filter(Domicilio.estatus == "A")
    if "edificio" in request.form:
        edificio_nombre = safe_string(request.form["edificio"])
        consulta = consulta.filter(Domicilio.edificio.contains(edificio_nombre))
    if "edificio_or_distrito_clave" in request.form:
        edificio_or_distrito_clave = safe_string(request.form["edificio_or_distrito_clave"])
        consulta = consulta.join(Distrito)
        consulta = consulta.filter(or_(Domicilio.edificio.contains(edificio_or_distrito_clave), Distrito.clave.contains(edificio_or_distrito_clave)))
    results = []
    for edificio in consulta.order_by(Domicilio.edificio).limit(20).all():
        results.append({"id": edificio.id, "text": edificio.distrito.clave + " : " + edificio.edificio})
    return {"results": results, "pagination": {"more": False}}

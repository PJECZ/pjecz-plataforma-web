"""
Inventarios Custodias, vistas
"""
import json
from datetime import date

from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from lib.datatables import get_datatable_parameters, output_datatable_json
from lib.safe_string import safe_message, safe_string

from plataforma_web.blueprints.bitacoras.models import Bitacora
from plataforma_web.blueprints.inv_custodias.models import InvCustodia
from plataforma_web.blueprints.inv_equipos.models import InvEquipo
from plataforma_web.blueprints.modulos.models import Modulo
from plataforma_web.blueprints.permisos.models import Permiso
from plataforma_web.blueprints.usuarios.decorators import permission_required
from plataforma_web.blueprints.usuarios.models import Usuario

from plataforma_web.blueprints.inv_custodias.forms import InvCustodiaForm, InvCustodiaSearchForm

MODULO = "INV CUSTODIAS"
MESES_FUTUROS = 6  # Un año a futuro, para las fechas

inv_custodias = Blueprint("inv_custodias", __name__, template_folder="templates")


@inv_custodias.before_request
@login_required
@permission_required(MODULO, Permiso.VER)
def before_request():
    """Permiso por defecto"""


@inv_custodias.route("/inv_custodias/datatable_json", methods=["GET", "POST"])
def datatable_json():
    """DataTable JSON para listado de INV CUSTODIAS"""
    # Tomar parámetros de Datatables
    draw, start, rows_per_page = get_datatable_parameters()
    # Consultar
    consulta = InvCustodia.query
    if "estatus" in request.form:
        consulta = consulta.filter_by(estatus=request.form["estatus"])
    else:
        consulta = consulta.filter_by(estatus="A")
    if "usuario_id" in request.form:
        usuario = Usuario.query.get(request.form["usuario_id"])
        if usuario:
            consulta = consulta.filter(InvCustodia.usuario == usuario)
    if "fecha" in request.form:
        consulta = consulta.filter(InvCustodia.fecha >= request.form["fecha"])
    if "nombre_completo" in request.form:
        consulta = consulta.filter(InvCustodia.nombre_completo.contains(safe_string(request.form["nombre_completo"])))
    if "fecha_desde" in request.form:
        consulta = consulta.filter(InvCustodia.fecha >= request.form["fecha_desde"])
    if "fecha_hasta" in request.form:
        consulta = consulta.filter(InvCustodia.fecha <= request.form["fecha_hasta"])
    registros = consulta.order_by(InvCustodia.id.desc()).offset(start).limit(rows_per_page).all()
    total = consulta.count()
    # Elaborar datos para DataTable
    data = []
    for resultado in registros:
        data.append(
            {
                "detalle": {
                    "id": resultado.id,
                    "url": url_for("inv_custodias.detail", inv_custodia_id=resultado.id),
                },
                "usuario": {
                    "nombre": resultado.nombre_completo,
                    "url": url_for("usuarios.detail", usuario_id=resultado.usuario_id) if current_user.can_view("USUARIOS") else "",
                },
                "fecha": resultado.fecha.strftime("%Y-%m-%d"),
                "equipos_cantidad": resultado.equipos_cantidad if resultado.equipos_cantidad != 0 else "-",
                "equipos_fotos_cantidad": resultado.equipos_fotos_cantidad if resultado.equipos_fotos_cantidad != 0 else "-",
                "oficina": {
                    "clave": resultado.usuario.oficina.clave,
                    "url": url_for("oficinas.detail", oficina_id=resultado.usuario.oficina_id) if current_user.can_view("OFICINAS") else "",
                },
            }
        )
    # Entregar JSON
    return output_datatable_json(draw, total, data)


@inv_custodias.route("/inv_custodias/")
def list_active():
    """Listado de Custodias activos"""
    return render_template(
        "inv_custodias/list.jinja2",
        filtros=json.dumps({"estatus": "A"}),
        titulo="Custodias",
        estatus="A",
    )


@inv_custodias.route("/inv_custodias/inactivos")
@permission_required(MODULO, Permiso.MODIFICAR)
def list_inactive():
    """Listado de Custodias inactivos"""
    return render_template(
        "inv_custodias/list.jinja2",
        filtros=json.dumps({"estatus": "B"}),
        titulo="Custodias inactivos",
        estatus="B",
    )


@inv_custodias.route("/inv_custodias/<int:inv_custodia_id>")
def detail(inv_custodia_id):
    """Detalle de un Custodias"""
    inv_custodia = InvCustodia.query.get_or_404(inv_custodia_id)
    return render_template("inv_custodias/detail.jinja2", inv_custodia=inv_custodia)


@inv_custodias.route("/inv_custodias/nuevo/<int:usuario_id>", methods=["GET", "POST"])
@permission_required(MODULO, Permiso.CREAR)
def new(usuario_id):
    """Nuevo Custodias"""
    usuario = Usuario.query.get_or_404(usuario_id)
    form = InvCustodiaForm()
    if form.validate_on_submit():
        es_valido = True
        # Validar la fecha de custodia nueva, no se permiten fechas futuras
        fecha = form.fecha.data
        if fecha is not None and fecha > date.today():
            es_valido = False
            flash("La fecha de custodia no puede ser futura.", "warning")
        # Si es valido insertar
        if es_valido:
            inv_custodia = InvCustodia(
                fecha=form.fecha.data,
                usuario=usuario,
                nombre_completo=usuario.nombre,
                curp=usuario.curp,
            )
            inv_custodia.save()
            flash(f"Custodias {inv_custodia.nombre_completo} guardado.", "success")
            return redirect(url_for("inv_custodias.detail", inv_custodia_id=inv_custodia.id))
    form.usuario.data = str(f"{usuario.nombre}")
    form.oficina.data = str(f"{usuario.oficina.clave} - {usuario.oficina.descripcion_corta}")
    return render_template("inv_custodias/new.jinja2", form=form, usuario=usuario)


@inv_custodias.route("/inv_custodias/edicion/<int:inv_custodia_id>", methods=["GET", "POST"])
@permission_required(MODULO, Permiso.MODIFICAR)
def edit(inv_custodia_id):
    """Editar Custodias"""
    inv_custodia = InvCustodia.query.get_or_404(inv_custodia_id)
    form = InvCustodiaForm()
    if form.validate_on_submit():
        es_valido = True
        # validar que la actualización de la fecha de custodia, no se permiten fechas futuras
        fecha = form.fecha.data
        if fecha is not None and fecha > date.today():
            es_valido = False
            flash("La fecha de custodia no puede ser futura.", "warning")
        # Si es valido insertar
        if es_valido:
            inv_custodia.fecha = form.fecha.data
            inv_custodia.save()
            flash(f"Custodias {inv_custodia.nombre_completo} guardado.", "success")
            return redirect(url_for("inv_custodias.detail", inv_custodia_id=inv_custodia.id))
    form.fecha.data = inv_custodia.fecha
    form.usuario.data = inv_custodia.usuario.nombre
    form.oficina.data = str(f"{inv_custodia.usuario.oficina.clave} - {inv_custodia.usuario.oficina.descripcion_corta}")
    return render_template("inv_custodias/edit.jinja2", form=form, inv_custodia=inv_custodia)


@inv_custodias.route("/inv_custodias/buscar", methods=["GET", "POST"])
def search():
    """Buscar Custodias"""
    form_search = InvCustodiaSearchForm()
    if form_search.validate_on_submit():
        busqueda = {"estatus": "A"}
        titulos = []
        # Si se busca por el ID y se encuentra, se redirecciona al detalle
        if form_search.id.data:
            inv_custodia_id = int(form_search.id.data)
            if inv_custodia_id != 0:
                inv_custodia = InvCustodia.query.get(inv_custodia_id)
                if inv_custodia is not None:
                    return redirect(url_for("inv_custodias.detail", inv_custodia_id=inv_custodia.id))
        # Si se busca con los demas parametros
        if form_search.nombre_completo.data:
            nombre_completo = safe_string(form_search.nombre_completo.data)
            if nombre_completo != "":
                busqueda["nombre_completo"] = nombre_completo
                titulos.append("nombre_completo " + nombre_completo)
        if form_search.fecha_desde.data:
            busqueda["fecha_desde"] = form_search.fecha_desde.data.strftime("%Y-%m-%d")
            titulos.append("fecha desde " + busqueda["fecha_desde"])
        if form_search.fecha_hasta.data:
            busqueda["fecha_hasta"] = form_search.fecha_hasta.data.strftime("%Y-%m-%d")
            titulos.append("fecha hasta " + busqueda["fecha_hasta"])
        return render_template(
            "inv_custodias/list.jinja2",
            filtros=json.dumps(busqueda),
            titulo="Custodias con " + ", ".join(titulos),
            estatus="A",
        )
    return render_template("inv_custodias/search.jinja2", form=form_search)


@inv_custodias.route("/inv_custodias/eliminar/<int:inv_custodia_id>")
@permission_required(MODULO, Permiso.MODIFICAR)
def delete(inv_custodia_id):
    """Eliminar Custodias"""
    inv_custodia = InvCustodia.query.get_or_404(inv_custodia_id)
    if inv_custodia.estatus == "A":
        inv_custodia.delete()
        flash(f"Custodias {inv_custodia.nombre_completo} eliminado.", "success")
    return redirect(url_for("inv_custodias.detail", inv_custodia_id=inv_custodia.id))


@inv_custodias.route("/inv_custodias/recuperar/<int:inv_custodia_id>")
@permission_required(MODULO, Permiso.MODIFICAR)
def recover(inv_custodia_id):
    """Recuperar Custodias"""
    inv_custodia = InvCustodia.query.get_or_404(inv_custodia_id)
    if inv_custodia.estatus == "B":
        inv_custodia.recover()
        flash(f"Custodias {inv_custodia.nombre_completo} recuperado.", "success")
    return redirect(url_for("inv_custodias.detail", inv_custodia_id=inv_custodia.id))

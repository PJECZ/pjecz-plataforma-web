"""
Inventarios Equipos, vistas
"""
import json
from datetime import date
from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from lib.datatables import get_datatable_parameters, output_datatable_json
from lib.safe_string import safe_string, safe_message

from plataforma_web.blueprints.bitacoras.models import Bitacora
from plataforma_web.blueprints.modulos.models import Modulo
from plataforma_web.blueprints.permisos.models import Permiso
from plataforma_web.blueprints.inv_custodias.models import InvCustodia
from plataforma_web.blueprints.inv_equipos.forms import InvEquipoForm, InvEquipoSearchForm
from plataforma_web.blueprints.inv_equipos.models import InvEquipo
from plataforma_web.blueprints.usuarios.decorators import permission_required

MODULO = "INV EQUIPOS"

inv_equipos = Blueprint("inv_equipos", __name__, template_folder="templates")


@inv_equipos.before_request
@login_required
@permission_required(MODULO, Permiso.VER)
def before_request():
    """Permiso por defecto"""


@inv_equipos.route("/inv_equipos/datatable_json", methods=["GET", "POST"])
def datatable_json():
    """DataTable JSON para listado de INV EQUIPOS"""
    # Tomar parámetros de Datatables
    draw, start, rows_per_page = get_datatable_parameters()
    # Consultar
    consulta = InvEquipo.query
    if "estatus" in request.form:
        consulta = consulta.filter_by(estatus=request.form["estatus"])
    else:
        consulta = consulta.filter_by(estatus="A")
    if "inv_custodia_id" in request.form:
        consulta = consulta.filter_by(inv_custodia_id=request.form["inv_custodia_id"])
    if "inv_modelo_id" in request.form:
        consulta = consulta.filter_by(inv_modelo=request.form["inv_modelo_id"])
    if "inv_red_id" in request.form:
        consulta = consulta.filter_by(inv_red=request.form["inv_red_id"])
    if "descripcion" in request.form:
        consulta = consulta.filter(InvEquipo.descripcion.contains(safe_string(request.form["descripcion"])))
    if "numero_serie" in request.form:
        consulta = consulta.filter(InvEquipo.numero_serie.contains(request.form["numero_serie"]))
    if "adquisicion_fecha" in request.form:
        consulta = consulta.filter(InvEquipo.adquisicion_fecha >= request.form["adquisicion_fecha"])
    registros = consulta.order_by(InvEquipo.id).offset(start).limit(rows_per_page).all()
    total = consulta.count()
    # Elaborar datos para DataTable
    data = []
    for resultado in registros:
        data.append(
            {
                "id": {
                    "equipo_id": resultado.id,
                    "url": url_for("inv_equipos.detail", equipo_id=resultado.id),
                },
                "descripcion": resultado.descripcion,
                "adquisicion_fecha": resultado.adquisicion_fecha.strftime("%Y-%m-%d") if resultado.adquisicion_fecha is not None else "-",
                "usuario": {
                    "nombre_completo": resultado.inv_custodia.usuario.nombre,
                    "url": url_for("usuarios.detail", usuario_id=resultado.inv_custodia.usuario_id) if current_user.can_view("USUARIOS") else "",
                },
                "inv_custodia_id": {
                    "id": resultado.inv_custodia.id,
                    "url": url_for("inv_custodias.detail", inv_custodia_id=resultado.inv_custodia.id) if current_user.can_view("INV CUSTODIAS") else "",
                },
                "inv_marca": {
                    "nombre": resultado.inv_modelo.inv_marca.nombre,
                    "url": url_for("inv_marcas.detail", inv_marca_id=resultado.inv_modelo.inv_marca.id) if current_user.can_view("INV MARCAS") else "",
                },
                "inv_modelo": {
                    "nombre": resultado.inv_modelo.descripcion,
                    "url": url_for("inv_modelos.detail", inv_modelo_id=resultado.inv_modelo.id) if current_user.can_view("INV MODELOS") else "",
                },
                "inv_red": {
                    "nombre": resultado.inv_red.nombre,
                    "url": url_for("inv_redes.detail", inv_red_id=resultado.inv_red.id) if current_user.can_view("INV REDES") else "",
                },
            }
        )
    # Entregar JSON
    return output_datatable_json(draw, total, data)


@inv_equipos.route("/inv_equipos")
def list_active():
    """Listado de Equipos activos"""
    return render_template(
        "inv_equipos/list.jinja2",
        filtros=json.dumps({"estatus": "A"}),
        titulo="Equipos",
        estatus="A",
    )


@inv_equipos.route("/inv_equipos/inactivos")
@permission_required(MODULO, Permiso.MODIFICAR)
def list_inactive():
    """Listado de Equipos inactivos"""
    return render_template(
        "inv_equipos/list.jinja2",
        filtros=json.dumps({"estatus": "B"}),
        titulo="Equipos inactivos",
        estatus="B",
    )


@inv_equipos.route("/inv_equipos/<int:inv_equipo_id>")
@login_required
@permission_required(MODULO, Permiso.VER)
def detail(inv_equipo_id):
    """Detalle de un Equipos"""
    inv_equipo = InvEquipo.query.get_or_404(inv_equipo_id)
    return render_template("inv_equipos/detail.jinja2", inv_equipo=inv_equipo)


@inv_equipos.route("/inv_equipos/nuevo/<int:inv_custodia_id>", methods=["GET", "POST"])
@permission_required(MODULO, Permiso.CREAR)
def new(inv_custodia_id):
    """Nuevo Equipos"""
    inv_custodia = InvCustodia.query.get_or_404(inv_custodia_id)
    if inv_custodia.estatus != "A":
        flash("La custodia no es activa.", "error")
        return redirect(url_for("inv_custodia.list_active"))
    form = InvEquipoForm()
    if form.validate_on_submit():
        es_valido = True
        # Validar la fecha de adquisicion, no se permiten fechas futuras
        adquisicion_fecha = form.adquisicion_fecha.data
        if adquisicion_fecha is not None and adquisicion_fecha > date.today():
            es_valido = False
            flash("La fecha de adquisición no puede ser futura.", "warning")
        # Si es valido insertar
        if es_valido:
            inv_equipo = InvEquipo(
                inv_custodia=inv_custodia,
                inv_modelo=form.inv_modelo.data,
                inv_red=form.inv_red.data,
                adquisicion_fecha=form.adquisicion_fecha.data,
                numero_serie=form.numero_serie.data,
                numero_inventario=form.numero_inventario.data,
                descripcion=safe_string(form.descripcion.data),
                direccion_ip=form.direccion_ip.data,
                direccion_mac=form.direccion_mac.data,
                numero_nodo=form.numero_nodo.data,
                numero_switch=form.numero_switch.data,
                numero_puerto=form.numero_puerto.data,
            )
            inv_equipo.save()
            bitacora = Bitacora(
                modulo=Modulo.query.filter_by(nombre=MODULO).first(),
                usuario=current_user,
                descripcion=safe_message(f"Nuevo equipo {inv_equipo.descripcion}"),
                url=url_for("inv_equipos.detail", inv_equipo_id=inv_equipo.id),
            )
            bitacora.save()
            flash(bitacora.descripcion, "success")
            return redirect(url_for("inv_equipos.detail", inv_equipo_id=inv_equipo.id))
    form.custodia.data = inv_custodia.nombre_completo
    form.email.data = inv_custodia.usuario.email
    form.puesto.data = inv_custodia.usuario.puesto
    form.oficina.data = str(f"{inv_custodia.usuario.oficina.clave} - {inv_custodia.usuario.oficina.descripcion_corta}")
    return render_template("inv_equipos/new.jinja2", form=form, custodia=inv_custodia)


@inv_equipos.route("/inv_equipos/edicion/<int:equipo_id>", methods=["GET", "POST"])
@permission_required(MODULO, Permiso.MODIFICAR)
def edit(equipo_id):
    """Editar Equipos"""
    equipo = InvEquipo.query.get_or_404(equipo_id)
    form = InvEquipoForm()
    validacion = False
    if form.validate_on_submit():
        try:
            validar_fecha(form.adquisicion_fecha.data)
            validacion = True
        except Exception as err:
            flash(f"La fecha es incorrecta: {str(err)}", "warning")
            validacion = False
        if validacion:
            equipo.inv_modelo = form.modelo.data
            equipo.inv_red = form.red.data
            equipo.adquisicion_fecha = form.adquisicion_fecha.data
            equipo.numero_serie = form.numero_serie.data
            equipo.numero_inventario = form.numero_inventario.data
            equipo.descripcion = safe_string(form.descripcion.data)
            equipo.direccion_ip = form.direccion_ip.data
            equipo.direccion_mac = form.direccion_mac.data
            equipo.numero_nodo = form.numero_nodo.data
            equipo.numero_switch = form.numero_switch.data
            equipo.numero_puerto = form.numero_puerto.data
            equipo.save()
            bitacora = Bitacora(
                modulo=Modulo.query.filter_by(nombre=MODULO).first(),
                usuario=current_user,
                descripcion=safe_message(f"Nuevo equipo {equipo.descripcion}"),
                url=url_for("inv_equipos.detail", equipo_id=equipo.id),
            )
            bitacora.save()
            flash(bitacora.descripcion, "success")
            # flash(f"Equipos {equipo.descripcion} guardado.", "success")
            return redirect(url_for("inv_equipos.detail", equipo_id=equipo.id))
    form.modelo.data = equipo.inv_modelo
    form.red.data = equipo.inv_red
    form.adquisicion_fecha.data = equipo.adquisicion_fecha
    form.numero_serie.data = equipo.numero_serie
    form.numero_inventario.data = equipo.numero_inventario
    form.descripcion.data = safe_string(equipo.descripcion)
    form.direccion_ip.data = equipo.direccion_ip
    form.direccion_mac.data = equipo.direccion_mac
    form.numero_nodo.data = equipo.numero_nodo
    form.numero_switch.data = equipo.numero_switch
    form.numero_puerto.data = equipo.numero_puerto
    form.custodia.data = equipo.inv_custodia.nombre_completo
    form.email.data = equipo.inv_custodia.usuario.email
    form.puesto.data = equipo.inv_custodia.usuario.puesto
    form.oficina.data = str(f"{equipo.inv_custodia.usuario.oficina.clave} - {equipo.inv_custodia.usuario.oficina.descripcion_corta}")
    return render_template("inv_equipos/edit.jinja2", form=form, equipo=equipo)


@inv_equipos.route("/inv_equipos/buscar", methods=["GET", "POST"])
def search():
    """Buscar Equipos"""
    form_search = InvEquipoSearchForm()
    if form_search.validate_on_submit():
        busqueda = {"estatus": "A"}
        titulos = []
        if form_search.descripcion.data:
            descripcion = safe_string(form_search.descripcion.data)
            if descripcion != "":
                busqueda["descripcion"] = descripcion
                titulos.append("descripcion " + descripcion)
        if form_search.numero_serie.data:
            numero_serie = form_search.numero_serie.data
            if numero_serie != "":
                busqueda["numero_serie"] = numero_serie
                titulos.append("numero serie" + numero_serie)
        if form_search.adquisicion_fecha.data:
            busqueda["adquisicion_fecha"] = form_search.adquisicion_fecha.data.strftime("%Y-%m-%d")
            titulos.append("fecha de asignacion de equipo" + form_search.adquisicion_fecha.data.strftime("%Y-%m-%d"))
        return render_template(
            "inv_equipos/list.jinja2",
            filtros=json.dumps(busqueda),
            titulo="Equipos con " + ", ".join(titulos),
            estatus="A",
        )
    return render_template("inv_equipos/search.jinja2", form=form_search)


@inv_equipos.route("/inv_equipos/eliminar/<int:equipo_id>")
@permission_required(MODULO, Permiso.MODIFICAR)
def delete(equipo_id):
    """Eliminar Equipos"""
    equipo = InvEquipo.query.get_or_404(equipo_id)
    if equipo.estatus == "A":
        equipo.delete()
        bitacora = Bitacora(
            modulo=Modulo.query.filter_by(nombre=MODULO).first(),
            usuario=current_user,
            descripcion=safe_message(f"Eliminado equipo {equipo.descripcion}"),
            url=url_for("inv_equipos.detail", equipo_id=equipo.id),
        )
        bitacora.save()
        flash(bitacora.descripcion, "success")
    return redirect(url_for("inv_equipos.detail", equipo_id=equipo.id))


@inv_equipos.route("/inv_equipos/recuperar/<int:equipo_id>")
@permission_required(MODULO, Permiso.MODIFICAR)
def recover(equipo_id):
    """Recuperar Equipos"""
    equipo = InvEquipo.query.get_or_404(equipo_id)
    if equipo.estatus == "B":
        equipo.recover()
        bitacora = Bitacora(
            modulo=Modulo.query.filter_by(nombre=MODULO).first(),
            usuario=current_user,
            descripcion=safe_message(f"Recuperar equipo {equipo.descripcion}"),
            url=url_for("inv_equipos.detail", equipo_id=equipo.id),
        )
        bitacora.save()
        flash(bitacora.descripcion, "success")
    return redirect(url_for("inv_equipos.detail", equipo_id=equipo.id))

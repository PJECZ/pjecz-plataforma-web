"""
Inventarios Equipos, vistas
"""
import json
from datetime import date
from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from lib.datatables import get_datatable_parameters, output_datatable_json
from lib.safe_string import safe_mac_address, safe_message, safe_string

from plataforma_web.blueprints.bitacoras.models import Bitacora
from plataforma_web.blueprints.inv_custodias.models import InvCustodia
from plataforma_web.blueprints.inv_equipos.forms import InvEquipoForm, InvEquipoSearchForm, InvEquipoChangeCustodia
from plataforma_web.blueprints.inv_equipos.models import InvEquipo
from plataforma_web.blueprints.modulos.models import Modulo
from plataforma_web.blueprints.permisos.models import Permiso
from plataforma_web.blueprints.usuarios.decorators import permission_required
from plataforma_web.blueprints.usuarios.models import Usuario

MODULO = "INV EQUIPOS"
FECHA_ANTIGUA = date(year=1990, month=1, day=1)

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
    if "usuario_id" in request.form:
        inv_custodia = InvCustodia.query.filter(InvCustodia.usuario_id == request.form["usuario_id"]).order_by(InvCustodia.id.desc()).first()
        if inv_custodia:
            consulta = consulta.filter(InvEquipo.inv_custodia_id == inv_custodia.id)
        else:
            consulta = consulta.filter(InvEquipo.inv_custodia_id == 0)
    if "inv_modelo_id" in request.form:
        consulta = consulta.filter_by(inv_modelo_id=request.form["inv_modelo_id"])
    if "inv_red_id" in request.form:
        consulta = consulta.filter_by(inv_red_id=request.form["inv_red_id"])
    if "descripcion" in request.form:
        consulta = consulta.filter(InvEquipo.descripcion.contains(safe_string(request.form["descripcion"])))
    if "numero_serie" in request.form:
        consulta = consulta.filter(InvEquipo.numero_serie.contains(request.form["numero_serie"]))
    if "numero_inventario" in request.form:
        consulta = consulta.filter(InvEquipo.numero_inventario.contains(request.form["numero_inventario"]))
    if "tipo" in request.form:
        consulta = consulta.filter(InvEquipo.tipo.contains(request.form["tipo"]))
    if "direccion_mac" in request.form:
        consulta = consulta.filter(InvEquipo.direccion_mac.contains(request.form["direccion_mac"]))
    if "direccion_ip" in request.form:
        consulta = consulta.filter(InvEquipo.direccion_ip.contains(request.form["direccion_ip"]))
    if "fecha_desde" in request.form:
        consulta = consulta.filter(InvEquipo.fecha_fabricacion >= request.form["fecha_desde"])
    if "fecha_hasta" in request.form:
        consulta = consulta.filter(InvEquipo.fecha_fabricacion <= request.form["fecha_hasta"])
    if "oficina_id" in request.form:
        consulta = consulta.join(InvCustodia, Usuario)
        consulta = consulta.filter(InvEquipo.inv_custodia_id == InvCustodia.id)
        consulta = consulta.filter(InvCustodia.usuario_id == Usuario.id)
        consulta = consulta.filter(Usuario.oficina_id == request.form["oficina_id"])
    registros = consulta.order_by(InvEquipo.id.desc()).offset(start).limit(rows_per_page).all()
    total = consulta.count()
    # Elaborar datos para DataTable
    data = []
    for resultado in registros:
        data.append(
            {
                "detalle": {
                    "id": resultado.id,
                    "url": url_for("inv_equipos.detail", inv_equipo_id=resultado.id),
                },
                "descripcion": resultado.descripcion,
                "fecha_fabricacion": resultado.fecha_fabricacion.strftime("%Y-%m-%d") if resultado.fecha_fabricacion is not None else "-",
                "tipo": resultado.tipo,
                "nombre_completo": resultado.inv_custodia.nombre_completo,
                "direccion_ip": resultado.direccion_ip,
                "direccion_mac": resultado.direccion_mac,
                "numero_serie": resultado.numero_serie,
                "numero_inventario": resultado.numero_inventario,
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
        # Validar la fecha de fabricación
        fecha_fabricacion = form.fecha_fabricacion.data
        if fecha_fabricacion is not None and not FECHA_ANTIGUA < fecha_fabricacion < date.today():
            es_valido = False
            flash("La fecha de fabricación esta fuera del rango permitido.", "warning")
        # Si es valido insertar
        if es_valido:
            inv_equipo = InvEquipo(
                inv_custodia=inv_custodia,
                inv_modelo=form.inv_modelo.data,
                inv_red=form.inv_red.data,
                fecha_fabricacion=form.fecha_fabricacion.data,
                numero_serie=form.numero_serie.data,
                numero_inventario=form.numero_inventario.data,
                descripcion=safe_string(form.descripcion.data),
                tipo=form.tipo.data,
                direccion_ip=form.direccion_ip.data,
                direccion_mac=safe_mac_address(form.direccion_mac.data),
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
    return render_template("inv_equipos/new.jinja2", form=form, inv_custodia=inv_custodia)


@inv_equipos.route("/inv_equipos/edicion/<int:inv_equipo_id>", methods=["GET", "POST"])
@permission_required(MODULO, Permiso.MODIFICAR)
def edit(inv_equipo_id):
    """Editar Equipos"""
    inv_equipo = InvEquipo.query.get_or_404(inv_equipo_id)
    form = InvEquipoForm()
    if form.validate_on_submit():
        es_valido = True
        # Validar la fecha de fabricación
        fecha_fabricacion = form.fecha_fabricacion.data
        if fecha_fabricacion is not None and not FECHA_ANTIGUA < fecha_fabricacion < date.today():
            es_valido = False
            flash("La fecha de fabricación esta fuera del rango permitido.", "warning")
        # Si es valido insertar
        if es_valido:
            inv_equipo.inv_modelo = form.inv_modelo.data
            inv_equipo.inv_red = form.inv_red.data
            inv_equipo.fecha_fabricacion = form.fecha_fabricacion.data
            inv_equipo.numero_serie = form.numero_serie.data
            inv_equipo.numero_inventario = form.numero_inventario.data
            inv_equipo.descripcion = safe_string(form.descripcion.data)
            inv_equipo.tipo = form.tipo.data
            inv_equipo.direccion_ip = form.direccion_ip.data
            inv_equipo.direccion_mac = safe_mac_address(form.direccion_mac.data)
            inv_equipo.numero_nodo = form.numero_nodo.data
            inv_equipo.numero_switch = form.numero_switch.data
            inv_equipo.numero_puerto = form.numero_puerto.data
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
    form.inv_modelo.data = inv_equipo.inv_modelo
    form.inv_red.data = inv_equipo.inv_red
    form.fecha_fabricacion.data = inv_equipo.fecha_fabricacion
    form.numero_serie.data = inv_equipo.numero_serie
    form.numero_inventario.data = inv_equipo.numero_inventario
    form.descripcion.data = safe_string(inv_equipo.descripcion)
    form.tipo.data = inv_equipo.tipo
    form.direccion_ip.data = inv_equipo.direccion_ip
    form.direccion_mac.data = inv_equipo.direccion_mac
    form.numero_nodo.data = inv_equipo.numero_nodo
    form.numero_switch.data = inv_equipo.numero_switch
    form.numero_puerto.data = inv_equipo.numero_puerto
    form.custodia.data = inv_equipo.inv_custodia.nombre_completo
    form.email.data = inv_equipo.inv_custodia.usuario.email
    form.puesto.data = inv_equipo.inv_custodia.usuario.puesto
    form.oficina.data = str(f"{inv_equipo.inv_custodia.usuario.oficina.clave} - {inv_equipo.inv_custodia.usuario.oficina.descripcion_corta}")
    return render_template("inv_equipos/edit.jinja2", form=form, inv_equipo=inv_equipo)


@inv_equipos.route("/inv_equipos/buscar", methods=["GET", "POST"])
def search():
    """Buscar Equipos"""
    form_search = InvEquipoSearchForm()
    if form_search.validate_on_submit():
        busqueda = {"estatus": "A"}
        titulos = []
        # Si se busca por el ID y se encuentra, se redirecciona al detalle
        if form_search.id.data:
            return redirect(url_for("inv_equipos.detail", inv_equipo_id=form_search.id.data))
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
        if form_search.numero_inventario.data:
            numero_inventario = int(form_search.numero_inventario.data)
            if numero_inventario != 0:
                numero_inventario = InvEquipo.query.get(numero_inventario)
                if numero_inventario is not None:
                    return redirect(url_for("inv_equipos.detail", numero_inventario=numero_inventario))
        if form_search.tipo.data:
            tipo_equipo = safe_string(form_search.tipo.data)
            if tipo_equipo != "":
                busqueda["tipo"] = tipo_equipo
                titulos.append("tipo" + tipo_equipo)
        if form_search.direccion_mac.data:
            direccion_mac = form_search.direccion_mac.data
            if direccion_mac != "":
                busqueda["direccion_mac"] = direccion_mac
                titulos.append("direccion_mac" + direccion_mac)
        if form_search.direccion_ip.data:
            direccion_ip = form_search.direccion_ip.data
            if direccion_ip != "":
                busqueda["direccion_ip"] = direccion_ip
                titulos.append("direccion_ip" + direccion_ip)
        if form_search.fecha_desde.data:
            busqueda["fecha_desde"] = form_search.fecha_desde.data.strftime("%Y-%m-%d")
            titulos.append("fecha desde " + busqueda["fecha_desde"])
        if form_search.fecha_hasta.data:
            busqueda["fecha_hasta"] = form_search.fecha_hasta.data.strftime("%Y-%m-%d")
            titulos.append("fecha hasta " + busqueda["fecha_hasta"])
        return render_template(
            "inv_equipos/list.jinja2",
            filtros=json.dumps(busqueda),
            titulo="Equipos con  " + ", ".join(titulos),
            estatus="A",
        )
    return render_template("inv_equipos/search.jinja2", form=form_search)


@inv_equipos.route("/inv_equipos/eliminar/<int:inv_equipo_id>")
@permission_required(MODULO, Permiso.MODIFICAR)
def delete(inv_equipo_id):
    """Eliminar Equipo"""
    inv_equipo = InvEquipo.query.get_or_404(inv_equipo_id)
    if inv_equipo.estatus == "A":
        inv_equipo.delete()
        bitacora = Bitacora(
            modulo=Modulo.query.filter_by(nombre=MODULO).first(),
            usuario=current_user,
            descripcion=safe_message(f"Eliminado equipo {inv_equipo.descripcion}"),
            url=url_for("inv_equipos.detail", inv_equipo_id=inv_equipo.id),
        )
        bitacora.save()
        flash(bitacora.descripcion, "success")
    return redirect(url_for("inv_equipos.detail", inv_equipo_id=inv_equipo.id))


@inv_equipos.route("/inv_equipos/recuperar/<int:inv_equipo_id>")
@permission_required(MODULO, Permiso.MODIFICAR)
def recover(inv_equipo_id):
    """Recuperar Equipo"""
    inv_equipo = InvEquipo.query.get_or_404(inv_equipo_id)
    if inv_equipo.estatus == "B":
        inv_equipo.recover()
        bitacora = Bitacora(
            modulo=Modulo.query.filter_by(nombre=MODULO).first(),
            usuario=current_user,
            descripcion=safe_message(f"Recuperar equipo {inv_equipo.descripcion}"),
            url=url_for("inv_equipos.detail", inv_equipo_id=inv_equipo.id),
        )
        bitacora.save()
        flash(bitacora.descripcion, "success")
    return redirect(url_for("inv_equipos.detail", inv_equipo_id=inv_equipo.id))


@inv_equipos.route("/inv_equipos/transferir/<int:inv_equipo_id>", methods=["GET", "POST"])
@permission_required(MODULO, Permiso.MODIFICAR)
def transferir(inv_equipo_id):
    """Transferir"""
    inv_equipo = InvEquipo.query.get_or_404(inv_equipo_id)
    form = InvEquipoChangeCustodia()
    if form.validate_on_submit():
        # Actualizar
        inv_equipo.inv_custodia_id = form.inv_custodia.data
        inv_equipo.save()
        bitacora = Bitacora(
            modulo=Modulo.query.filter_by(nombre=MODULO).first(),
            usuario=current_user,
            descripcion=safe_message(f"Se transfirió el equipo con id {inv_equipo.id}."),
            url=url_for("inv_custodias.detail", inv_custodia_id=inv_equipo.inv_custodia_id),
        )
        bitacora.save()
        flash(bitacora.descripcion, "success")
        return redirect(bitacora.url)
    return render_template("inv_equipos/transferir.jinja2", form=form, inv_equipo=inv_equipo)


@inv_equipos.route("/inv_equipos/custodias_json", methods=["POST"])
def query_custodias_json():
    """Proporcionar el JSON de usuarios para elegir con un Slecet2"""
    inv_custodias = InvCustodia.query.filter(InvCustodia.estatus == "A")
    if "searchString" in request.form:
        current_custodia = request.form["current_custodia"]
        inv_custodias = inv_custodias.filter(InvCustodia.nombre_completo.contains(safe_string(request.form["searchString"])))
    resultados = []
    for inv_custodia in inv_custodias.order_by(InvCustodia.nombre_completo).limit(10).all():
        if inv_custodia.id != int(current_custodia):
            resultados.append({"id": inv_custodia.id, "text": inv_custodia.usuario.email, "value": inv_custodia.id})
    return {"results": resultados, "pagination": {"more": False}}


@inv_equipos.route("/inv_equipos/custodias_json/<int:custodia_id>", methods=["GET", "POST"])
@permission_required(MODULO, Permiso.MODIFICAR)
def custodiajson(custodia_id):
    """JSON trar custodia"""
    custodia = InvCustodia.query.get_or_404(custodia_id)
    equipos = InvEquipo.query.filter(InvEquipo.estatus == "A")
    equipos = equipos.filter(InvEquipo.inv_custodia_id == custodia_id).all()
    resultados = []
    for equipo in equipos:
        resultados.append({"id": equipo.id, "tipo": equipo.tipo, "descripcion": equipo.descripcion})
    return {"id": custodia_id, "nombre": custodia.nombre_completo, "email": custodia.usuario.email, "oficina": custodia.usuario.oficina.descripcion_corta, "equipos": resultados}

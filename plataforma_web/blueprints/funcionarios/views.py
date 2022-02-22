"""
Funcionarios, vistas
"""
import json
from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from lib import datatables
from lib.safe_string import safe_message, safe_string

from plataforma_web.blueprints.bitacoras.models import Bitacora
from plataforma_web.blueprints.usuarios.decorators import permission_required
from plataforma_web.blueprints.funcionarios.models import Funcionario
from plataforma_web.blueprints.funcionarios.forms import FuncionarioForm, FuncionarioSearchForm
from plataforma_web.blueprints.modulos.models import Modulo
from plataforma_web.blueprints.permisos.models import Permiso

MODULO = "FUNCIONARIOS"

funcionarios = Blueprint("funcionarios", __name__, template_folder="templates")


@funcionarios.before_request
@login_required
@permission_required(MODULO, Permiso.VER)
def before_request():
    """Permiso por defecto"""


@funcionarios.route("/funcionarios")
def list_active():
    """Listado de Funcionarios activos y en funciones"""
    return render_template(
        "funcionarios/list.jinja2",
        filtros=json.dumps({"estatus": "A", "en_funciones": True}),
        titulo="Funcionarios en funciones",
        estatus="A",
    )


@funcionarios.route("/funcionarios/en_sentencias")
def list_active_en_sentencias():
    """Listado de Funcionarios activos y en sentencias"""
    return render_template(
        "funcionarios/list.jinja2",
        filtros=json.dumps({"estatus": "A", "en_sentencias": True}),
        titulo="Funcionarios en sentencias",
        estatus="A",
    )


@funcionarios.route("/funcionarios/en_soportes")
def list_active_en_soportes():
    """Listado de Funcionarios activos y en soportes"""
    return render_template(
        "funcionarios/list.jinja2",
        filtros=json.dumps({"estatus": "A", "en_soportes": True}),
        titulo="Funcionarios en soportes",
        estatus="A",
    )


@funcionarios.route("/funcionarios/en_tesis_jurisprudencias")
def list_active_en_tesis_jurisprudencias():
    """Listado de Funcionarios activos y en tesis y jurisprudencias"""
    return render_template(
        "funcionarios/list.jinja2",
        filtros=json.dumps({"estatus": "A", "en_tesis_jurisprudencias": True}),
        titulo="Funcionarios en tesis y jurisprudencias",
        estatus="A",
    )


@funcionarios.route("/funcionarios/inactivos")
@permission_required(MODULO, Permiso.MODIFICAR)
def list_inactive():
    """Listado de Funcionarios inactivos"""
    return render_template(
        "funcionarios/list.jinja2",
        filtros=json.dumps({"estatus": "B"}),
        titulo="Funcionarios inactivos",
        estatus="B",
    )


@funcionarios.route("/funcionarios/buscar", methods=["GET", "POST"])
def search():
    """Buscar Funcionarios"""
    form_search = FuncionarioSearchForm()
    if form_search.validate_on_submit():
        busqueda = {"estatus": "A"}
        titulos = []
        if form_search.nombres.data:
            nombres = safe_string(form_search.nombres.data)
            if nombres != "":
                busqueda["nombres"] = nombres
                titulos.append("nombres " + nombres)
        if form_search.apellido_paterno.data:
            apellido_paterno = safe_string(form_search.apellido_paterno.data)
            if apellido_paterno != "":
                busqueda["apellido_paterno"] = apellido_paterno
                titulos.append("apellido paterno " + apellido_paterno)
        if form_search.apellido_materno.data:
            apellido_materno = safe_string(form_search.apellido_materno.data)
            if apellido_materno != "":
                busqueda["apellido_materno"] = apellido_materno
                titulos.append("apellido materno " + apellido_materno)
        if form_search.curp.data:
            curp = safe_string(form_search.curp.data)
            if curp != "":
                busqueda["curp"] = curp
                titulos.append("CURP " + curp)
        if form_search.puesto.data:
            puesto = safe_string(form_search.puesto.data)
            if puesto != "":
                busqueda["puesto"] = puesto
                titulos.append("puesto " + puesto)
        if form_search.email.data:
            email = safe_string(form_search.email.data, to_uppercase=False)
            if email != "":
                busqueda["email"] = email
                titulos.append("e-mail " + email)
        return render_template(
            "funcionarios/list.jinja2",
            filtros=json.dumps(busqueda),
            titulo="Funcionarios con " + ", ".join(titulos),
            estatus="A",
        )
    return render_template("funcionarios/search.jinja2", form=form_search)


@funcionarios.route("/funcionarios/datatable_json", methods=["GET", "POST"])
def datatable_json():
    """DataTable JSON para listado de Funcionarios"""
    # Tomar parámetros de Datatables
    draw, start, rows_per_page = datatables.get_parameters()
    # Consultar
    consulta = Funcionario.query
    if "estatus" in request.form:
        consulta = consulta.filter_by(estatus=request.form["estatus"])
    else:
        consulta = consulta.filter_by(estatus="A")
    if "nombres" in request.form:
        consulta = consulta.filter(Funcionario.nombres.contains(safe_string(request.form["nombres"])))
    if "apellido_paterno" in request.form:
        consulta = consulta.filter(Funcionario.apellido_paterno.contains(safe_string(request.form["apellido_paterno"])))
    if "apellido_materno" in request.form:
        consulta = consulta.filter(Funcionario.apellido_materno.contains(safe_string(request.form["apellido_materno"])))
    if "curp" in request.form:
        consulta = consulta.filter(Funcionario.curp.contains(safe_string(request.form["curp"])))
    if "puesto" in request.form:
        consulta = consulta.filter(Funcionario.puesto.contains(safe_string(request.form["puesto"])))
    if "email" in request.form:
        consulta = consulta.filter(Funcionario.email.contains(safe_string(request.form["email"], to_uppercase=False)))
    if "en_funciones" in request.form and request.form["en_funciones"] == "true":
        consulta = consulta.filter(Funcionario.en_funciones == True)
    if "en_sentencias" in request.form and request.form["en_sentencias"] == "true":
        consulta = consulta.filter(Funcionario.en_sentencias == True)
    if "en_soportes" in request.form and request.form["en_soportes"] == "true":
        consulta = consulta.filter(Funcionario.en_soportes == True)
    if "en_tesis_jurisprudencias" in request.form and request.form["en_tesis_jurisprudencias"] == "true":
        consulta = consulta.filter(Funcionario.en_tesis_jurisprudencias == True)
    registros = consulta.order_by(Funcionario.curp.asc()).offset(start).limit(rows_per_page).all()
    total = consulta.count()
    # Elaborar datos para DataTable
    data = []
    for resultado in registros:
        data.append(
            {
                "detalle": {
                    "curp": resultado.curp,
                    "url": url_for("funcionarios.detail", funcionario_id=resultado.id),
                },
                "nombre": resultado.nombre,
                "email": resultado.email,
                "puesto": resultado.puesto,
                "en_funciones": resultado.en_funciones,
            }
        )
    # Entregar JSON
    return datatables.output(draw, total, data)


@funcionarios.route("/funcionarios/<int:funcionario_id>")
def detail(funcionario_id):
    """Detalle de un Funcionario"""
    funcionario = Funcionario.query.get_or_404(funcionario_id)
    return render_template("funcionarios/detail.jinja2", funcionario=funcionario)


@funcionarios.route("/funcionarios/nuevo", methods=["GET", "POST"])
@permission_required(MODULO, Permiso.CREAR)
def new():
    """Nuevo Funcionario"""
    form = FuncionarioForm()
    if form.validate_on_submit():
        es_valido = True
        curp = safe_string(form.curp.data)
        if Funcionario.query.filter_by(curp=curp).first():
            flash(f"Ya existe un funcionario con la CURP {curp}", "warning")
            es_valido = False
        email = form.email.data
        if Funcionario.query.filter_by(email=email).first():
            flash(f"Ya existe un funcionario con el email {email}", "warning")
            es_valido = False
        if es_valido:
            funcionario = Funcionario(
                nombres=safe_string(form.nombres.data),
                apellido_paterno=safe_string(form.apellido_paterno.data),
                apellido_materno=safe_string(form.apellido_materno.data),
                curp=curp,
                email=email,
                puesto=safe_string(form.puesto.data),
                en_funciones=form.en_funciones.data,
                en_sentencias=form.en_sentencias.data,
                en_soportes=form.en_soportes.data,
                en_tesis_jurisprudencias=form.en_tesis_jurisprudencias.data,
            )
            funcionario.save()
            bitacora = Bitacora(
                modulo=Modulo.query.filter_by(nombre=MODULO).first(),
                usuario=current_user,
                descripcion=safe_message(f"Nuevo funcionario {funcionario.nombre}"),
                url=url_for("funcionarios.detail", funcionario_id=funcionario.id),
            )
            bitacora.save()
            flash(bitacora.descripcion, "success")
            return redirect(bitacora.url)
    return render_template("funcionarios/new.jinja2", form=form)


@funcionarios.route("/funcionarios/edicion/<int:funcionario_id>", methods=["GET", "POST"])
@permission_required(MODULO, Permiso.MODIFICAR)
def edit(funcionario_id):
    """Editar Funcionario"""
    funcionario = Funcionario.query.get_or_404(funcionario_id)
    form = FuncionarioForm()
    if form.validate_on_submit():
        es_valido = True
        curp = safe_string(form.curp.data)
        if Funcionario.query.filter_by(curp=curp).filter(Funcionario.id != funcionario_id).first():
            flash(f"Ya existe un funcionario con la CURP {curp}", "warning")
            es_valido = False
        email = form.email.data
        if Funcionario.query.filter_by(email=email).filter(Funcionario.id != funcionario_id).first():
            flash(f"Ya existe un funcionario con el email {email}", "warning")
            es_valido = False
        if es_valido:
            funcionario.nombres = safe_string(form.nombres.data)
            funcionario.apellido_paterno = safe_string(form.apellido_paterno.data)
            funcionario.apellido_materno = safe_string(form.apellido_materno.data)
            funcionario.curp = curp
            funcionario.email = email
            funcionario.puesto = safe_string(form.puesto.data)
            funcionario.en_funciones = form.en_funciones.data
            funcionario.en_sentencias = form.en_sentencias.data
            funcionario.en_soportes = form.en_soportes.data
            funcionario.en_tesis_jurisprudencias = form.en_tesis_jurisprudencias.data
            funcionario.save()
            bitacora = Bitacora(
                modulo=Modulo.query.filter_by(nombre=MODULO).first(),
                usuario=current_user,
                descripcion=safe_message(f"Editado funcionario {funcionario.nombre}"),
                url=url_for("funcionarios.detail", funcionario_id=funcionario.id),
            )
            bitacora.save()
            flash(bitacora.descripcion, "success")
            return redirect(bitacora.url)
    form.nombres.data = funcionario.nombres
    form.apellido_paterno.data = funcionario.apellido_paterno
    form.apellido_materno.data = funcionario.apellido_materno
    form.curp.data = funcionario.curp
    form.email.data = funcionario.email
    form.puesto.data = funcionario.puesto
    form.en_funciones.data = funcionario.en_funciones
    form.en_sentencias.data = funcionario.en_sentencias
    form.en_soportes.data = funcionario.en_soportes
    form.en_tesis_jurisprudencias.data = funcionario.en_tesis_jurisprudencias
    return render_template("funcionarios/edit.jinja2", form=form, funcionario=funcionario)


@funcionarios.route("/funcionarios/eliminar/<int:funcionario_id>")
@permission_required(MODULO, Permiso.MODIFICAR)
def delete(funcionario_id):
    """Eliminar Funcionario"""
    funcionario = Funcionario.query.get_or_404(funcionario_id)
    if funcionario.estatus == "A":
        funcionario.delete()
        bitacora = Bitacora(
            modulo=Modulo.query.filter_by(nombre=MODULO).first(),
            usuario=current_user,
            descripcion=safe_message(f"Eliminado funcionario {funcionario.nombre}"),
            url=url_for("funcionarios.detail", funcionario_id=funcionario.id),
        )
        bitacora.save()
        flash(bitacora.descripcion, "success")
    return redirect(url_for("funcionarios.detail", funcionario_id=funcionario.id))


@funcionarios.route("/funcionarios/recuperar/<int:funcionario_id>")
@permission_required(MODULO, Permiso.MODIFICAR)
def recover(funcionario_id):
    """Recuperar Funcionario"""
    funcionario = Funcionario.query.get_or_404(funcionario_id)
    if funcionario.estatus == "B":
        funcionario.recover()
        bitacora = Bitacora(
            modulo=Modulo.query.filter_by(nombre=MODULO).first(),
            usuario=current_user,
            descripcion=safe_message(f"Recuperado {funcionario.nombre}"),
            url=url_for("funcionarios.detail", funcionario_id=funcionario.id),
        )
        bitacora.save()
        flash(bitacora.descripcion, "success")
    return redirect(url_for("funcionarios.detail", funcionario_id=funcionario.id))

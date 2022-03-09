"""
Soporte Categorias, vistas
"""
import json
from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from lib.datatables import get_datatable_parameters, output_datatable_json
from lib.safe_string import safe_string, safe_message, safe_text

from plataforma_web.blueprints.bitacoras.models import Bitacora
from plataforma_web.blueprints.modulos.models import Modulo
from plataforma_web.blueprints.permisos.models import Permiso
from plataforma_web.blueprints.usuarios.decorators import permission_required
from plataforma_web.blueprints.soportes_categorias.models import SoporteCategoria
from plataforma_web.blueprints.soportes_categorias.forms import SoporteCategoriaForm

from plataforma_web.blueprints.roles.models import Rol

MODULO = "SOPORTES CATEGORIAS"

soportes_categorias = Blueprint("soportes_categorias", __name__, template_folder="templates")


@soportes_categorias.before_request
@login_required
@permission_required(MODULO, Permiso.VER)
def before_request():
    """Permiso por defecto"""


@soportes_categorias.route("/soportes_categorias")
def list_active():
    """Listado de Soportes Categorias activos"""
    return render_template(
        "soportes_categorias/list.jinja2",
        filtros=json.dumps({"estatus": "A"}),
        titulo="Soportes Categorias",
        estatus="A",
    )


@soportes_categorias.route("/soportes_categorias/inactivos")
@permission_required(MODULO, Permiso.MODIFICAR)
def list_inactive():
    """Listado de Soportes Categorias inactivos"""
    return render_template(
        "soportes_categorias/list.jinja2",
        filtros=json.dumps({"estatus": "B"}),
        titulo="Soportes Categorias inactivos",
        estatus="B",
    )


@soportes_categorias.route("/soportes_categorias/datatable_json", methods=["GET", "POST"])
def datatable_json():
    """DataTable JSON para listado de Categorías"""
    # Tomar parámetros de Datatables
    draw, start, rows_per_page = get_datatable_parameters()
    # Consultar
    consulta = SoporteCategoria.query
    if "estatus" in request.form:
        consulta = consulta.filter_by(estatus=request.form["estatus"])
    else:
        consulta = consulta.filter_by(estatus="A")
    if "nombre" in request.form and request.form["nombre"] != "OTRO":
        consulta = consulta.filter(SoporteCategoria.nombre.contains(safe_string(request.form["nombre"])))
    registros = consulta.order_by(SoporteCategoria.nombre).offset(start).limit(rows_per_page).all()
    total = consulta.count()
    # Elaborar datos para DataTable
    data = []
    for resultado in registros:
        data.append(
            {
                "detalle": {
                    "nombre": resultado.nombre,
                    "url": url_for("soportes_categorias.detail", soporte_categoria_id=resultado.id),
                },
                "atendido": resultado.rol.nombre,
                "instrucciones": resultado.instrucciones,
            }
        )
    # Entregar JSON
    return output_datatable_json(draw, total, data)


@soportes_categorias.route("/soportes_categorias/<int:soporte_categoria_id>")
def detail(soporte_categoria_id):
    """Detalle de un Soporte Categoria"""
    soporte_categoria = SoporteCategoria.query.get_or_404(soporte_categoria_id)
    return render_template("soportes_categorias/detail.jinja2", soporte_categoria=soporte_categoria)


@soportes_categorias.route("/soportes_categorias/nuevo", methods=["GET", "POST"])
@permission_required(MODULO, Permiso.CREAR)
def new():
    """Nuevo Soporte Categoria"""
    form = SoporteCategoriaForm()
    if form.validate_on_submit():
        # Validar que el nombre no se repita
        nombre = safe_string(form.nombre.data)
        if SoporteCategoria.query.filter_by(nombre=nombre).first() is not None:
            flash("El nombre ya está en uso. Debe de ser único.", "warning")
        else:
            soporte_categoria = SoporteCategoria(
                nombre=nombre,
                rol=form.rol.data,
                instrucciones=safe_text(form.instrucciones.data),
            )
            soporte_categoria.save()
            bitacora = Bitacora(
                modulo=Modulo.query.filter_by(nombre=MODULO).first(),
                usuario=current_user,
                descripcion=safe_message(f"Nuevo soporte categoria {soporte_categoria.nombre}"),
                url=url_for("soportes_categorias.detail", soporte_categoria_id=soporte_categoria.id),
            )
            bitacora.save()
            flash(bitacora.descripcion, "success")
            return redirect(bitacora.url)
    return render_template("soportes_categorias/new.jinja2", form=form)


@soportes_categorias.route("/soportes_categorias/edicion/<int:soporte_categoria_id>", methods=["GET", "POST"])
@permission_required(MODULO, Permiso.MODIFICAR)
def edit(soporte_categoria_id):
    """Editar Soporte Categoria"""
    soporte_categoria = SoporteCategoria.query.get_or_404(soporte_categoria_id)
    form = SoporteCategoriaForm()
    if form.validate_on_submit():
        es_valido = True
        # Si cambia el nombre verificar que no este en uso
        nombre = safe_string(form.nombre.data)
        if soporte_categoria.nombre != nombre:
            soporte_categoria_existente = SoporteCategoria.query.filter_by(nombre=nombre).first()
            if soporte_categoria_existente and soporte_categoria_existente.id != soporte_categoria.id:
                es_valido = False
                flash("El nombre ya está en uso. Debe de ser único.", "warning")
        # Si es valido actualizar
        if es_valido:
            soporte_categoria.nombre = nombre
            soporte_categoria.rol = form.rol.data
            soporte_categoria.instrucciones = safe_text(form.instrucciones.data)
            soporte_categoria.save()
            bitacora = Bitacora(
                modulo=Modulo.query.filter_by(nombre=MODULO).first(),
                usuario=current_user,
                descripcion=safe_message(f"Editado soporte categoria {soporte_categoria.nombre}"),
                url=url_for("soportes_categorias.detail", soporte_categoria_id=soporte_categoria.id),
            )
            bitacora.save()
            flash(bitacora.descripcion, "success")
            return redirect(bitacora.url)
    form.nombre.data = soporte_categoria.nombre
    form.rol.data = soporte_categoria.rol
    form.instrucciones.data = soporte_categoria.instrucciones
    return render_template("soportes_categorias/edit.jinja2", form=form, soporte_categoria=soporte_categoria)


@soportes_categorias.route("/soportes_categorias/eliminar/<int:soporte_categoria_id>")
@permission_required(MODULO, Permiso.MODIFICAR)
def delete(soporte_categoria_id):
    """Eliminar Soporte Categoria"""
    soporte_categoria = SoporteCategoria.query.get_or_404(soporte_categoria_id)
    if soporte_categoria.estatus == "A":
        soporte_categoria.delete()
        bitacora = Bitacora(
            modulo=Modulo.query.filter_by(nombre=MODULO).first(),
            usuario=current_user,
            descripcion=safe_message(f"Recuperado soporte_categoria_id {soporte_categoria.nombre}"),
            url=url_for("soportes_categorias.detail", soporte_categoria_id=soporte_categoria.id),
        )
        bitacora.save()
        flash(bitacora.descripcion, "success")
    return redirect(url_for("soportes_categorias.detail", soporte_categoria_id=soporte_categoria.id))


@soportes_categorias.route("/soportes_categorias/recuperar/<int:soporte_categoria_id>")
@permission_required(MODULO, Permiso.MODIFICAR)
def recover(soporte_categoria_id):
    """Recuperar Soporte Categoria"""
    soporte_categoria = SoporteCategoria.query.get_or_404(soporte_categoria_id)
    if soporte_categoria.estatus == "B":
        soporte_categoria.recover()
        bitacora = Bitacora(
            modulo=Modulo.query.filter_by(nombre=MODULO).first(),
            usuario=current_user,
            descripcion=safe_message(f"Recuperado soporte_categoria_id {soporte_categoria.nombre}"),
            url=url_for("soportes_categorias.detail", soporte_categoria_id=soporte_categoria.id),
        )
        bitacora.save()
        flash(bitacora.descripcion, "success")
    return redirect(url_for("soportes_categorias.detail", soporte_categoria_id=soporte_categoria.id))

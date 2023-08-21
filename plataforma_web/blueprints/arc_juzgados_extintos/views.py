"""
Archivo Juzgados Extintos, vistas
"""
import json
from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from lib.datatables import get_datatable_parameters, output_datatable_json
from lib.safe_string import safe_message, safe_string, safe_clave

from plataforma_web.blueprints.bitacoras.models import Bitacora
from plataforma_web.blueprints.modulos.models import Modulo
from plataforma_web.blueprints.permisos.models import Permiso
from plataforma_web.blueprints.usuarios.decorators import permission_required

from plataforma_web.blueprints.arc_juzgados_extintos.models import ArcJuzgadoExtinto
from plataforma_web.blueprints.arc_juzgados_extintos.forms import ArcJuzgadoExtintoForm

MODULO = "ARC JUZGADOS EXTINTOS"

arc_juzgados_extintos = Blueprint("arc_juzgados_extintos", __name__, template_folder="templates")


@arc_juzgados_extintos.before_request
@login_required
@permission_required(MODULO, Permiso.VER)
def before_request():
    """Permiso por defecto"""


@arc_juzgados_extintos.route("/arc_juzgados_extintos/datatable_json", methods=["GET", "POST"])
def datatable_json():
    """DataTable JSON para listado de Juzgados Extintos"""
    # Tomar parámetros de Datatables
    draw, start, rows_per_page = get_datatable_parameters()
    # Consultar
    consulta = ArcJuzgadoExtinto.query
    if "estatus" in request.form:
        consulta = consulta.filter_by(estatus=request.form["estatus"])
    else:
        consulta = consulta.filter_by(estatus="A")
    registros = consulta.order_by(ArcJuzgadoExtinto.clave).offset(start).limit(rows_per_page).all()
    total = consulta.count()
    # Elaborar datos para DataTable
    data = []
    for resultado in registros:
        data.append(
            {
                "detalle": {
                    "clave": resultado.clave,
                    "url": url_for("arc_juzgados_extintos.detail", arc_juzgado_extinto_id=resultado.id),
                },
                "descripcion_corta": resultado.descripcion_corta,
                "descripcion": resultado.descripcion,
                "distrito": {
                    "nombre": resultado.distrito.nombre_corto,
                    "url": url_for("distritos.detail", distrito_id=resultado.distrito_id) if current_user.can_view("DISTRITOS") else "",
                },
            }
        )
    # Entregar JSON
    return output_datatable_json(draw, total, data)


@arc_juzgados_extintos.route("/arc_juzgados_extintos")
def list_active():
    """Listado de Juzgados Extintos activos"""
    return render_template(
        "arc_juzgados_extintos/list.jinja2",
        filtros=json.dumps({"estatus": "A"}),
        titulo="Juzgados Extintos",
        estatus="A",
    )


@arc_juzgados_extintos.route("/arc_juzgados_extintos/inactivos")
@permission_required(MODULO, Permiso.MODIFICAR)
def list_inactive():
    """Listado de Juzgados Extintos inactivos"""
    return render_template(
        "arc_juzgados_extintos/list.jinja2",
        filtros=json.dumps({"estatus": "B"}),
        titulo="Juzgados Extintos inactivos",
        estatus="B",
    )


@arc_juzgados_extintos.route("/arc_juzgados_extintos/<int:arc_juzgado_extinto_id>")
def detail(arc_juzgado_extinto_id):
    """Detalle de un Juzgado Extinto"""
    arc_juzgado_extinto = ArcJuzgadoExtinto.query.get_or_404(arc_juzgado_extinto_id)
    return render_template("arc_juzgados_extintos/detail.jinja2", arc_juzgado_extinto=arc_juzgado_extinto)


@arc_juzgados_extintos.route("/arc_juzgados_extintos/nuevo", methods=["GET", "POST"])
@permission_required(MODULO, Permiso.CREAR)
def new():
    """Nuevo Juzgado Extinto"""
    form = ArcJuzgadoExtintoForm()
    if form.validate_on_submit():
        # Validar que la clave sea única
        clave = safe_clave(form.clave.data)
        if ArcJuzgadoExtinto.query.filter_by(clave=clave).first():
            flash(f"La clave '{clave}' ya se encuentra en uso. Utilice una diferente.", "warning")
        else:
            arc_juzgado_extinto = ArcJuzgadoExtinto(
                clave=clave,
                distrito=form.distrito.data,
                descripcion_corta=safe_string(form.descripcion_corta.data),
                descripcion=safe_string(form.descripcion.data),
            )
            arc_juzgado_extinto.save()
            bitacora = Bitacora(
                modulo=Modulo.query.filter_by(nombre=MODULO).first(),
                usuario=current_user,
                descripcion=safe_message(f"Nuevo Juzgado Extinto {arc_juzgado_extinto.clave}"),
                url=url_for("arc_juzgados_extintos.detail", arc_juzgado_extinto_id=arc_juzgado_extinto.id),
            )
            bitacora.save()
            flash(bitacora.descripcion, "success")
            return redirect(bitacora.url)
    return render_template("arc_juzgados_extintos/new.jinja2", form=form)


@arc_juzgados_extintos.route("/arc_juzgados_extintos/edicion/<int:arc_juzgado_extinto_id>", methods=["GET", "POST"])
@permission_required(MODULO, Permiso.MODIFICAR)
def edit(arc_juzgado_extinto_id):
    """Editar Juzgado Extinto"""
    arc_juzgado_extinto = ArcJuzgadoExtinto.query.get_or_404(arc_juzgado_extinto_id)
    form = ArcJuzgadoExtintoForm()
    if form.validate_on_submit():
        # Validar que la clave sea única
        clave = safe_clave(form.clave.data)
        if ArcJuzgadoExtinto.query.filter_by(clave=clave).filter(ArcJuzgadoExtinto.id != arc_juzgado_extinto_id).first():
            flash(f"La clave '{clave}' ya se encuentra en uso. Utilice una diferente.", "warning")
        else:
            arc_juzgado_extinto.clave = clave
            arc_juzgado_extinto.distrito = form.distrito.data
            arc_juzgado_extinto.descripcion_corta = safe_string(form.descripcion_corta.data)
            arc_juzgado_extinto.descripcion = safe_string(form.descripcion.data)
            arc_juzgado_extinto.save()
            bitacora = Bitacora(
                modulo=Modulo.query.filter_by(nombre=MODULO).first(),
                usuario=current_user,
                descripcion=safe_message(f"Editado Juzgado Extinto {arc_juzgado_extinto.clave}"),
                url=url_for("arc_juzgados_extintos.detail", arc_juzgado_extinto_id=arc_juzgado_extinto.id),
            )
            bitacora.save()
            flash(bitacora.descripcion, "success")
            return redirect(bitacora.url)
    # Cargar valores guardados
    form.clave.data = arc_juzgado_extinto.clave
    form.distrito.data = arc_juzgado_extinto.distrito
    form.descripcion_corta.data = arc_juzgado_extinto.descripcion_corta
    form.descripcion.data = arc_juzgado_extinto.descripcion
    return render_template("arc_juzgados_extintos/edit.jinja2", form=form, arc_juzgado_extinto=arc_juzgado_extinto)


@arc_juzgados_extintos.route("/arc_juzgados_extintos/eliminar/<int:arc_juzgado_extinto_id>")
@permission_required(MODULO, Permiso.MODIFICAR)
def delete(arc_juzgado_extinto_id):
    """Eliminar Juzgado Extinto"""
    arc_juzgado_extinto = ArcJuzgadoExtinto.query.get_or_404(arc_juzgado_extinto_id)
    if arc_juzgado_extinto.estatus == "A":
        arc_juzgado_extinto.delete()
        bitacora = Bitacora(
            modulo=Modulo.query.filter_by(nombre=MODULO).first(),
            usuario=current_user,
            descripcion=safe_message(f"Eliminado Juzgado Extinto {arc_juzgado_extinto.clave}"),
            url=url_for("arc_juzgados_extintos.detail", arc_juzgado_extinto_id=arc_juzgado_extinto.id),
        )
        bitacora.save()
        flash(bitacora.descripcion, "success")
    return redirect(url_for("arc_juzgados_extintos.detail", arc_juzgado_extinto_id=arc_juzgado_extinto.id))


@arc_juzgados_extintos.route("/arc_juzgados_extintos/recuperar/<int:arc_juzgado_extinto_id>")
@permission_required(MODULO, Permiso.MODIFICAR)
def recover(arc_juzgado_extinto_id):
    """Recuperar Juzgado Extinto"""
    arc_juzgado_extinto = ArcJuzgadoExtinto.query.get_or_404(arc_juzgado_extinto_id)
    if arc_juzgado_extinto.estatus == "B":
        arc_juzgado_extinto.recover()
        bitacora = Bitacora(
            modulo=Modulo.query.filter_by(nombre=MODULO).first(),
            usuario=current_user,
            descripcion=safe_message(f"Recuperado Juzgado Extinto {arc_juzgado_extinto.clave}"),
            url=url_for("arc_juzgados_extintos.detail", arc_juzgado_extinto_id=arc_juzgado_extinto.id),
        )
        bitacora.save()
        flash(bitacora.descripcion, "success")
    return redirect(url_for("arc_juzgados_extintos.detail", arc_juzgado_extinto_id=arc_juzgado_extinto.id))

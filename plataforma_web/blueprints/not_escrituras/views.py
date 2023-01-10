"""
Notarías Escrituras, vistas
"""
import json
from datetime import date

from delta import html
from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required
from sqlalchemy.sql import or_

from lib.datatables import get_datatable_parameters, output_datatable_json
from lib.safe_string import safe_message
from lib.time_working import next_labor_day

from plataforma_web.blueprints.autoridades.models import Autoridad
from plataforma_web.blueprints.bitacoras.models import Bitacora
from plataforma_web.blueprints.modulos.models import Modulo
from plataforma_web.blueprints.not_escrituras.models import NotEscritura
from plataforma_web.blueprints.not_escrituras.forms import NotEscriturasForm, NotEscriturasEditForm, NotEscriturasEditJuzgadoForm
from plataforma_web.blueprints.permisos.models import Permiso
from plataforma_web.blueprints.usuarios.decorators import permission_required

MODULO = "NOT ESCRITURAS"

not_escrituras = Blueprint("not_escrituras", __name__, template_folder="templates")

# Roles que deben estar en la base de datos
ROL_NOTARIA = "NOTARIA"
ROL_JUZGADO = "JUZGADO PRIMERA INSTANCIA"


@not_escrituras.before_request
@login_required
@permission_required(MODULO, Permiso.VER)
def before_request():
    """Permiso por defecto"""


@not_escrituras.route("/not_escrituras/datatable_json", methods=["GET", "POST"])
def datatable_json():
    """DataTable JSON para listado de Not Escrituras New"""
    # Tomar parámetros de Datatables
    draw, start, rows_per_page = get_datatable_parameters()
    # Consultar
    consulta = NotEscritura.query
    if "estatus" in request.form:
        consulta = consulta.filter_by(estatus=request.form["estatus"])
    else:
        consulta = consulta.filter_by(estatus="A")
    if "notaria" in request.form:
        consulta = consulta.filter(NotEscritura.notaria == request.form["notaria"])
    if "autoridad_id" in request.form:
        consulta = consulta.filter(NotEscritura.autoridad_id == request.form["autoridad_id"])
    if "estado" in request.form:
        consulta = consulta.filter(NotEscritura.estado == request.form["estado"])
    registros = consulta.order_by(NotEscritura.id).offset(start).limit(rows_per_page).all()
    total = consulta.count()
    # Elaborar datos para DataTable
    data = []
    for resultado in registros:
        nombre_notaria = Autoridad.query.filter(Autoridad.id == resultado.notaria).first()
        data.append(
            {
                "detalle": {
                    "id": resultado.id,
                    "url": url_for("not_escrituras.detail", not_escritura_id=resultado.id),
                },
                "distrito": {
                    "nombre_corto": resultado.autoridad.distrito.nombre_corto,
                    "url": url_for("distritos.detail", distrito_id=resultado.autoridad.distrito_id) if current_user.can_view("DISTRITOS") else "",
                },
                "notaria": {
                    "descripcion_corta": nombre_notaria.descripcion,
                    "url": url_for("autoridades.detail", autoridad_id=resultado.notaria) if current_user.can_view("AURORIDADES") else "",
                },
                "autoridad": {
                    "descripcion": resultado.autoridad.descripcion_corta,
                    "url": url_for("autoridades.detail", autoridad_id=resultado.autoridad_id) if current_user.can_view("AUTRIDADES") else "",
                },
                "estado": resultado.estado,
            }
        )
    # Entregar JSON
    return output_datatable_json(draw, total, data)


@not_escrituras.route("/not_escrituras")
def list_active():
    """Listado de Escrituras activos"""
    # Consultar los roles del usuario
    current_user_roles = current_user.get_roles()
    # Mostrar solo las Escrituras finalizadas
    return render_template(
        "not_escrituras/list.jinja2",
        titulo="Escrituras Finalizadas",
        filtros=json.dumps({"estatus": "A", "estado": "FINALIZADO"}),
        estatus="A",
        show_button_list_working=current_user.can_admin(MODULO) or ROL_NOTARIA in current_user_roles,
        show_button_list_send=True,
        show_button_list_update=True,
        show_button_list_approved=True,
    )


@not_escrituras.route("/not_escrituras/finalizadas")
def list_approved():
    """Listado de Escrituras finalizadas"""
    # Consultar los roles del usuario
    current_user_roles = current_user.get_roles()
    # vista para mostrar listado a Administrador y Juzgado
    if current_user.can_admin(MODULO) or ROL_JUZGADO in current_user_roles:
        return render_template(
            "not_escrituras/list.jinja2",
            filtros=json.dumps({"estatus": "A", "estado": "FINALIZADO", "autoridad_id": current_user.autoridad_id}),
            titulo="Escrituras finalizado",
            estatus="A",
            show_button_list_working=current_user.can_admin(MODULO) or ROL_NOTARIA in current_user_roles,
            show_button_list_send=True,
            show_button_list_update=True,
            show_button_list_approved=True,
        )
    # vista para mostrar listado a Administrador y Notaría
    elif current_user.can_admin(MODULO) or ROL_NOTARIA in current_user_roles:
        return render_template(
            "not_escrituras/list.jinja2",
            filtros=json.dumps({"estatus": "A", "estado": "FINALIZADO", "notaria": current_user.autoridad_id}),
            titulo="Escrituras finalizado",
            estatus="A",
            show_button_list_working=current_user.can_admin(MODULO) or ROL_NOTARIA in current_user_roles,
            show_button_list_send=True,
            show_button_list_update=True,
            show_button_list_approved=True,
        )
    # si no, redirigir a la lista general
    return redirect(url_for("not_escrituras.list_active"))


@not_escrituras.route("/not_escrituras/revisadas")
def list_update():
    """Listado de Escrituras revisadas"""
    # Consultar los roles del usuario
    current_user_roles = current_user.get_roles()
    # vista para mostrar listado a Administrador y Juzgado
    if current_user.can_admin(MODULO) or ROL_JUZGADO in current_user_roles:
        return render_template(
            "not_escrituras/list.jinja2",
            titulo="Escrituras revisadas",
            filtros=json.dumps({"estatus": "A", "estado": "REVISADO", "autoridad_id": current_user.autoridad_id}),
            estatus="A",
            show_button_list_working=current_user.can_admin(MODULO) or ROL_NOTARIA in current_user_roles,
            show_button_list_send=True,
            show_button_list_update=True,
            show_button_list_approved=True,
        )
    # vista para mostrar listado a Administrador y Notaría
    elif current_user.can_admin(MODULO) or ROL_NOTARIA in current_user_roles:
        return render_template(
            "not_escrituras/list.jinja2",
            titulo="Escrituras revisadas",
            filtros=json.dumps({"estatus": "A", "estado": "REVISADO", "notaria": current_user.autoridad_id}),
            estatus="A",
            show_button_list_working=current_user.can_admin(MODULO) or ROL_NOTARIA in current_user_roles,
            show_button_list_send=True,
            show_button_list_update=True,
            show_button_list_approved=True,
        )
    # si no, redirigir a la lista general
    return redirect(url_for("not_escrituras.list_active"))


@not_escrituras.route("/not_escrituras/trabajadas")
def list_working():
    """Listado de Escrituras trabajadas"""
    # Consultar los roles del usuario
    current_user_roles = current_user.get_roles()
    # vista para mostrar listado a Administrador y Notaría
    if current_user.can_admin(MODULO) or ROL_NOTARIA in current_user_roles:
        return render_template(
            "not_escrituras/list.jinja2",
            filtros=json.dumps({"estatus": "A", "estado": "TRABAJADO", "notaria": current_user.autoridad_id}),
            titulo="Escrituras trabajado",
            estatus="A",
            show_button_list_working=current_user.can_admin(MODULO) or ROL_NOTARIA in current_user_roles,
            show_button_list_send=True,
            show_button_list_update=True,
            show_button_list_approved=True,
        )
    # si no, redirigir a la lista general
    return redirect(url_for("not_escrituras.list_active"))


@not_escrituras.route("/not_escrituras/enviadas")
def list_send():
    """Listado de Escrituras enviadas"""
    # Consultar los roles del usuario
    current_user_roles = current_user.get_roles()
    # vista para mostrar listado a Administrador y Juzgado
    if current_user.can_admin(MODULO) or ROL_JUZGADO in current_user_roles:
        return render_template(
            "not_escrituras/list.jinja2",
            filtros=json.dumps({"estatus": "A", "estado": "ENVIADO", "autoridad_id": current_user.autoridad_id}),
            titulo="Escrituras envíadas",
            estatus="A",
            show_button_list_working=current_user.can_admin(MODULO) or ROL_NOTARIA in current_user_roles,
            show_button_list_send=True,
            show_button_list_update=True,
            show_button_list_approved=True,
        )
    # vista para mostrar listado a Administrador y Notaría
    elif current_user.can_admin(MODULO) or ROL_NOTARIA in current_user_roles:
        return render_template(
            "not_escrituras/list.jinja2",
            filtros=json.dumps({"estatus": "A", "estado": "ENVIADO", "notaria": current_user.autoridad_id}),
            titulo="Escrituras envíadas",
            estatus="A",
            show_button_list_working=current_user.can_admin(MODULO) or ROL_NOTARIA in current_user_roles,
            show_button_list_send=True,
            show_button_list_update=True,
            show_button_list_approved=True,
        )
    # si no, redirigir a la lista general
    return redirect(url_for("not_escrituras.list_active"))


@not_escrituras.route("/not_escrituras/inactivos")
@permission_required(MODULO, Permiso.MODIFICAR)
def list_inactive():
    """Listado de Escrituras inactivos"""
    return render_template(
        "not_escrituras/list.jinja2",
        filtros=json.dumps({"estatus": "B"}),
        titulo="Escrituras inactivos",
        estatus="B",
    )


@not_escrituras.route("/not_escrituras/<int:not_escritura_id>")
def detail(not_escritura_id):
    """Detalle de un Escrituras"""
    not_escritura = NotEscritura.query.get_or_404(not_escritura_id)
    return render_template(
        "not_escrituras/detail.jinja2",
        not_escritura=not_escritura,
        contenido=str(html.render(not_escritura.contenido["ops"])),
        # Mostrar botones de editar
        show_button_edit_juzgado=ROL_JUZGADO in current_user.get_roles(),
        show_button_edit_notaria=current_user.can_admin(MODULO) or ROL_NOTARIA in current_user.get_roles(),
    )


@not_escrituras.route("/not_escrituras/nuevo", methods=["GET", "POST"])
@permission_required(MODULO, Permiso.CREAR)
def new():
    """Nuevo Escrituras"""
    form = NotEscriturasForm()
    if form.validate_on_submit():
        autoridad = Autoridad.query.get_or_404(form.autoridad.data)
        not_escritura = NotEscritura(
            notaria=current_user.autoridad.id,
            autoridad=autoridad,
            expediente=form.expediente.data,
            contenido=form.contenido.data,
            fecha=date.today(),
            fecha_limite=next_labor_day(date.today(), 10),
            estado=form.estado.data,
        )
        not_escritura.save()

        # Agregar evento a la bitácora e ir al detalle
        bitacora = Bitacora(
            modulo=Modulo.query.filter_by(nombre=MODULO).first(),
            usuario=current_user,
            descripcion=safe_message(f"Nuevo Escrituras {not_escritura.expediente}"),
            url=url_for("not_escrituras.detail", not_escritura_id=not_escritura.id),
        )
        bitacora.save()
        flash(bitacora.descripcion, "success")
        return redirect(bitacora.url)
    form.distrito.data = current_user.autoridad.distrito.nombre
    form.notaria.data = current_user.autoridad.descripcion
    buscar = "Busca un juzgado o notaria"
    if current_user.autoridad.es_notaria:
        buscar = "JUZGADO"
    elif current_user.autoridad.es_jurisdiccional:
        buscar = "NOTARIA"
    return render_template("not_escrituras/new.jinja2", form=form, buscar=buscar)


@not_escrituras.route("/not_escrituras/edicion/<int:not_escritura_id>", methods=["GET", "POST"])
@permission_required(MODULO, Permiso.MODIFICAR)
def edit(not_escritura_id):
    """Editar Escrituras"""
    not_escritura = NotEscritura.query.get_or_404(not_escritura_id)
    if not_escritura.estado not in ["TRABAJADO", "REVISADO"]:
        flash(f"No puede editar la escritura porque ya fue {not_escritura.estado}.", "warning")
        return redirect(url_for("not_escrituras.detail", not_escritura_id=not_escritura_id))
    form = NotEscriturasEditForm()
    if form.validate_on_submit():

        juzgado = Autoridad.query.get_or_404(form.autoridad.data)
        not_escritura.contenido = form.contenido.data
        not_escritura.autoridad = juzgado
        not_escritura.estado = form.estado.data
        not_escritura.expediente = form.expediente.data
        not_escritura.fecha_limite = next_labor_day(date.today(), 10)
        not_escritura.save()
        bitacora = Bitacora(
            modulo=Modulo.query.filter_by(nombre=MODULO).first(),
            usuario=current_user,
            descripcion=safe_message(f"Editado Escrituras {not_escritura.expediente}"),
            url=url_for("not_escrituras.detail", not_escritura_id=not_escritura.id),
        )
        bitacora.save()
        flash(bitacora.descripcion, "success")
        return redirect(bitacora.url)
    form.distrito.data = current_user.autoridad.distrito.nombre
    form.notaria.data = current_user.autoridad.descripcion
    form.autoridad.data = not_escritura.autoridad
    form.expediente.data = not_escritura.expediente
    form.contenido.data = not_escritura.contenido
    buscar = "Busca un juzgado o notaria"
    if current_user.autoridad.es_notaria:
        buscar = "JUZGADO"
    elif current_user.autoridad.es_jurisdiccional:
        buscar = "NOTARIA"
    return render_template(
        "not_escrituras/edit_borrador.jinja2",
        form=form,
        not_escritura=not_escritura,
        buscar=buscar,
        contenido=json.dumps(not_escritura.contenido),
    )


@not_escrituras.route("/not_escrituras/edicion_juzgado/<int:not_escritura_id>", methods=["GET", "POST"])
@permission_required(MODULO, Permiso.MODIFICAR)
def edit_juzgado(not_escritura_id):
    """Editar Escritura juzgado"""
    not_escritura = NotEscritura.query.get_or_404(not_escritura_id)
    if not_escritura.estado not in ["ENVIADO", "REVISADO"]:
        flash(f"No puede editar la escritura porque ya fue {not_escritura.estado}.", "warning")
        return redirect(url_for("not_escrituras.detail", not_escritura_id=not_escritura_id))
    form = NotEscriturasEditJuzgadoForm()
    if form.validate_on_submit():
        not_escritura.contenido = form.contenido.data
        not_escritura.estado = form.estado.data
        not_escritura.expediente = form.expediente.data
        not_escritura.fecha_limite = next_labor_day(date.today(), 10)
        not_escritura.save()
        bitacora = Bitacora(
            modulo=Modulo.query.filter_by(nombre=MODULO).first(),
            usuario=current_user,
            descripcion=safe_message(f"Editado Escritura {not_escritura.id}"),
            url=url_for("not_escrituras.detail", not_escritura_id=not_escritura.id),
        )
        bitacora.save()
        flash(bitacora.descripcion, "success")
        return redirect(bitacora.url)
    form.distrito.data = current_user.autoridad.distrito.nombre
    form.notaria.data = current_user.autoridad.descripcion
    form.autoridad.data = not_escritura.autoridad_id
    form.expediente.data = not_escritura.expediente
    form.contenido.data = not_escritura.contenido
    buscar = "Busca un juzgado o notaria"
    if current_user.autoridad.es_notaria:
        buscar = "JUZGADO"
    elif current_user.autoridad.es_jurisdiccional:
        buscar = "NOTARIA"
    return render_template(
        "not_escrituras/edit_revision.jinja2",
        form=form,
        not_escritura=not_escritura,
        buscar=buscar,
        contenido=json.dumps(not_escritura.contenido),
    )


@not_escrituras.route("/not_escrituras/eliminar/<int:not_escritura_id>")
@permission_required(MODULO, Permiso.MODIFICAR)
def delete(not_escritura_id):
    """Eliminar Escrituras"""
    not_escritura = NotEscritura.query.get_or_404(not_escritura_id)
    if not_escritura.estatus == "A":
        not_escritura.delete()
        bitacora = Bitacora(
            modulo=Modulo.query.filter_by(nombre=MODULO).first(),
            usuario=current_user,
            descripcion=safe_message(f"Eliminado Escrituras {not_escritura.id}"),
            url=url_for("not_escrituras.detail", not_escritura_id=not_escritura.id),
        )
        bitacora.save()
        flash(bitacora.descripcion, "success")
    return redirect(url_for("not_escrituras.detail", not_escritura_id=not_escritura.id))


@not_escrituras.route("/not_escrituras/recuperar/<int:not_escritura_id>")
@permission_required(MODULO, Permiso.MODIFICAR)
def recover(not_escritura_id):
    """Recuperar Escritura"""
    not_escritura = NotEscritura.query.get_or_404(not_escritura_id)
    if not_escritura.estatus == "B":
        not_escritura.recover()
        bitacora = Bitacora(
            modulo=Modulo.query.filter_by(nombre=MODULO).first(),
            usuario=current_user,
            descripcion=safe_message(f"Recuperado Escritura {not_escritura.id}"),
            url=url_for("not_escrituras.detail", not_escritura_id=not_escritura.id),
        )
        bitacora.save()
        flash(bitacora.descripcion, "success")
    return redirect(url_for("not_escrituras.detail", not_escritura_id=not_escritura.id))


@not_escrituras.route("/not_escrituras/query_autoridades_json", methods=["POST"])
def query_autoridades_json(tipo):
    """Listado de Autoridades filtrar por juzgado"""
    # Consultar las autoridades
    consulta = Autoridad.query
    if tipo == "juzgado":
        consulta = consulta.filter_by(estatus="A").filter_by(es_revision_escritura=True)
    if "searchString" in request.form:
        busqueda = request.form["searchString"]
        consulta = consulta.filter(or_(Autoridad.clave.contains(busqueda), Autoridad.descripcion.contains(busqueda)))
        consulta = consulta.order_by(Autoridad.id).limit(15).all()

    # Elaborar datos para el Select2
    results = []
    for autoridad in consulta:
        results.append({"id": autoridad.id, "text": autoridad.clave + " : " + autoridad.descripcion})

    return {"results": results, "pagination": {"more": False}}

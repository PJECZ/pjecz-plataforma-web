"""
Not Escrituras, vistas
"""
import json
from delta import html
from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required
from sqlalchemy.sql import or_

from lib.datatables import get_datatable_parameters, output_datatable_json
from lib.safe_string import safe_string, safe_message

from plataforma_web.blueprints.autoridades.models import Autoridad
from plataforma_web.blueprints.bitacoras.models import Bitacora
from plataforma_web.blueprints.modulos.models import Modulo
from plataforma_web.blueprints.not_escrituras.forms import NotEscriturasForm, NotEscriturasEditForm, NotEscriturasEditJuzgadoForm
from plataforma_web.blueprints.not_escrituras.models import NotEscritura
from plataforma_web.blueprints.permisos.models import Permiso
from plataforma_web.blueprints.usuarios.decorators import permission_required

MODULO = "NOT ESCRITURAS"

not_escrituras = Blueprint("not_escrituras", __name__, template_folder="templates")

# ROLES
ROL_NOTARIA = "NOTARIA"
ROL_JUZGADO = "JUZGADO PRIMERA INSTANCIA"


@not_escrituras.before_request
@login_required
@permission_required(MODULO, Permiso.VER)
def before_request():
    """Permiso por defecto"""


@not_escrituras.route("/not_escrituras/datatable_json", methods=["GET", "POST"])
def datatable_json():
    """DataTable JSON para listado de Escrituras"""
    # Tomar parámetros de Datatables
    draw, start, rows_per_page = get_datatable_parameters()
    # Consultar
    consulta = NotEscritura.query
    if "estatus" in request.form:
        consulta = consulta.filter_by(estatus=request.form["estatus"])
    else:
        consulta = consulta.filter_by(estatus="A")
    if "notaria_id" in request.form:
        consulta = consulta.filter(NotEscritura.notaria_id == request.form["notaria_id"])
    if "juzgado_id" in request.form:
        consulta = consulta.filter(NotEscritura.juzgado_id == request.form["juzgado_id"])
    if "estado" in request.form:
        consulta = consulta.filter(NotEscritura.estado == request.form["estado"])
    current_user_roles = current_user.get_roles()
    if ROL_JUZGADO in current_user_roles:
        consulta = consulta.filter(NotEscritura.estado != "TRABAJANDO")
    if ROL_NOTARIA in current_user_roles:
        consulta = consulta.filter(NotEscritura.notaria == current_user.autoridad)
    if ROL_JUZGADO in current_user_roles:
        consulta = consulta.filter(NotEscritura.juzgado == current_user.autoridad)
    registros = consulta.order_by(NotEscritura.id).offset(start).limit(rows_per_page).all()
    total = consulta.count()
    # Elaborar datos para DataTable
    data = []
    for resultado in registros:
        data.append(
            {
                "detalle": {
                    "id": resultado.id,
                    "url": url_for("not_escrituras.detail", not_escritura_id=resultado.id),
                },
                "distrito": {
                    "nombre_corto": resultado.notaria.distrito.nombre_corto,
                    "url": url_for("distritos.detail", distrito_id=resultado.notaria.distrito_id) if current_user.can_view("DISTRITOS") else "",
                },
                "notaria": {
                    "descripcion": resultado.notaria.descripcion_corta,
                    "url": url_for("autoridades.detail", autoridad_id=resultado.notaria_id) if current_user.can_view("AUTORIDADES") else "",
                },
                "estado": resultado.estado,
            }
        )
    # Entregar JSON
    return output_datatable_json(draw, total, data)


@not_escrituras.route("/not_escrituras")
def list_active():
    """Listado de Escrituras activos"""
    if current_user.can_admin(MODULO):
        return render_template(
            "not_escrituras/list.jinja2",
            filtros=json.dumps({"estatus": "A"}),
            titulo="Todas las Escrituras",
            estatus="A",
            show_button_list_working=current_user.can_admin(MODULO) or ROL_NOTARIA in current_user.get_roles(),
            show_button_list_send=True,
            show_button_list_update=True,
            show_button_list_all=True,
        )
    # Consultar los roles del usuario
    current_user_roles = current_user.get_roles()
    # Mostrar solo las Escrituras aprobadas
    return render_template(
        "not_escrituras/list.jinja2",
        titulo="Escrituras aprobadas",
        filtros=json.dumps({"estatus": "A", "estado": "APROBADO"}),
        estatus="A",
        show_button_list_working=current_user.can_admin(MODULO) or ROL_NOTARIA in current_user_roles,
        show_button_list_send=current_user.can_admin(MODULO) or ROL_NOTARIA in current_user_roles or ROL_JUZGADO in current_user_roles,
        show_button_list_update=current_user.can_admin(MODULO) or ROL_NOTARIA in current_user_roles or ROL_JUZGADO in current_user_roles,
        show_button_list_all=current_user.can_admin(MODULO) or ROL_NOTARIA in current_user_roles or ROL_JUZGADO in current_user_roles,
    )


@not_escrituras.route("/not_escrituras/aprobadas")
def list_approved():
    """Listado de Escrituras aprobadas"""
    # Consultar los roles del usuario
    current_user_roles = current_user.get_roles()
    # Si es administrador, juzgado ó notaría, mostrar las Escrituras que se estan aprobadas
    return render_template(
        "not_escrituras/list.jinja2",
        filtros=json.dumps({"estatus": "A", "estado": "APROBADO"}),
        titulo="Escrituras aprobadas",
        estatus="A",
        show_button_list_working=current_user.can_admin(MODULO) or ROL_NOTARIA in current_user_roles,
        show_button_list_send=current_user.can_admin(MODULO) or ROL_NOTARIA in current_user_roles or ROL_JUZGADO in current_user_roles,
        show_button_list_update=current_user.can_admin(MODULO) or ROL_NOTARIA in current_user_roles or ROL_JUZGADO in current_user_roles,
        show_button_list_all=current_user.can_admin(MODULO) or ROL_NOTARIA in current_user_roles or ROL_JUZGADO in current_user_roles,
    )


@not_escrituras.route("/not_escrituras/corregidas")
def list_update():
    """Listado de Escrituras corregidas"""
    # Consultar los roles del usuario
    current_user_roles = current_user.get_roles()
    # Si es administrador, juzgado ó notaría, mostrar las Escrituras que se estan corrigiendo
    # if not (current_user.can_admin(MODULO) or ROL_JUZGADO == current_user.autoridad_id or ROL_NOTARIA == current_user.autoridad_id):
    if current_user.can_admin(MODULO) or ROL_JUZGADO in current_user_roles or ROL_NOTARIA in current_user_roles:
        return render_template(
            "not_escrituras/list.jinja2",
            filtros=json.dumps({"estatus": "A", "estado": "CORRECCIONES"}),
            titulo="Escrituras en corrección",
            estatus="A",
            show_button_list_working=current_user.can_admin(MODULO) or ROL_NOTARIA in current_user_roles,
            show_button_list_send=current_user.can_admin(MODULO) or ROL_NOTARIA in current_user_roles or ROL_JUZGADO in current_user_roles,
            show_button_list_update=current_user.can_admin(MODULO) or ROL_NOTARIA in current_user_roles or ROL_JUZGADO in current_user_roles,
            show_button_list_all=current_user.can_admin(MODULO) or ROL_NOTARIA in current_user_roles or ROL_JUZGADO in current_user_roles,
        )
    # si no, redirigir a la lista general
    return redirect(url_for("not_escrituras.list_active"))


@not_escrituras.route("/not_escrituras/trabajando")
def list_working():
    """Listado de Escrituras trabajadas y enviadas activos"""
    # Consultar los roles del usuario
    current_user_roles = current_user.get_roles()
    # Si es administrador o notaría, mostrar las Escrituras que se estan trabajando
    if current_user.can_admin(MODULO) or ROL_JUZGADO in current_user_roles or ROL_NOTARIA in current_user_roles:
        return render_template(
            "not_escrituras/list.jinja2",
            filtros=json.dumps({"estatus": "A", "estado": "TRABAJANDO"}),
            titulo="Escrituras trabajando",
            estatus="A",
            show_button_list_working=current_user.can_admin(MODULO) or ROL_NOTARIA in current_user_roles,
            show_button_list_send=current_user.can_admin(MODULO) or ROL_NOTARIA in current_user_roles or ROL_JUZGADO in current_user_roles,
            show_button_list_update=current_user.can_admin(MODULO) or ROL_NOTARIA in current_user_roles or ROL_JUZGADO in current_user_roles,
            show_button_list_all=current_user.can_admin(MODULO) or ROL_NOTARIA in current_user_roles,
        )
    # si no, redirigir a la lista general
    return redirect(url_for("not_escrituras.list_active"))


@not_escrituras.route("/not_escrituras/enviadas")
def list_send():
    """Listado de Escrituras enviadas activos"""
    # Consultar los roles del usuario
    current_user_roles = current_user.get_roles()
    # Si es administrador o notaría, mostrar las Escrituras que se estan trabajando
    if not (current_user.can_admin(MODULO) or ROL_JUZGADO == current_user.autoridad_id or ROL_NOTARIA == current_user.autoridad_id):

        if current_user.can_admin(MODULO) or ROL_JUZGADO in current_user_roles or ROL_NOTARIA in current_user_roles:
            return render_template(
                "not_escrituras/list.jinja2",
                filtros=json.dumps({"estatus": "A", "estado": "ENVIADO"}),
                titulo="Escrituras enviadas",
                estatus="A",
                show_button_list_working=current_user.can_admin(MODULO) or ROL_NOTARIA in current_user_roles,
                show_button_list_send=current_user.can_admin(MODULO) or ROL_NOTARIA in current_user_roles or ROL_JUZGADO in current_user_roles,
                show_button_list_update=current_user.can_admin(MODULO) or ROL_NOTARIA in current_user_roles or ROL_JUZGADO in current_user_roles,
                show_button_list_all=current_user.can_admin(MODULO) or ROL_NOTARIA in current_user_roles or ROL_JUZGADO in current_user_roles,
            )
    # si no, redirigir a la lista general
    return redirect(url_for("not_escrituras.list_active"))


@not_escrituras.route("/not_escrituras/todas")
def list_all():
    """Listado de Todas las Escrituras"""
    # Consultar los roles del usuario
    current_user_roles = current_user.get_roles()
    # Si es administrador, juzgado o notaría, mostrar todas las Escrituras
    if current_user.can_admin(MODULO) or ROL_JUZGADO in current_user_roles or ROL_NOTARIA in current_user_roles:
        return render_template(
            "not_escrituras/list.jinja2",
            filtros=json.dumps({"estatus": "A"}),
            titulo="Todas las Escrituras",
            estatus="A",
            show_button_list_working=current_user.can_admin(MODULO) or ROL_NOTARIA in current_user_roles,
            show_button_list_send=True,
            show_button_list_update=True,
            show_button_list_all=True,
        )
    # Si no, redirigir a la lista general
    return redirect(url_for("not_esrituras.list_active"))


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
        show_button_edit_juzgado=ROL_JUZGADO in current_user.get_roles(),
        show_button_edit_notaria=current_user.can_admin(MODULO) or ROL_NOTARIA in current_user.get_roles(),
    )


@not_escrituras.route("/not_escrituras/nuevo", methods=["GET", "POST"])
@permission_required(MODULO, Permiso.CREAR)
def new():
    """Nuevo Escrituras"""
    form = NotEscriturasForm()
    if form.validate_on_submit():
        if form.estado.data not in NotEscritura.ESTADOS:
            flash("No es un estado valido", "warning")
        else:
            juzgado = Autoridad.query.get_or_404(form.juzgado.data)
            not_escritura = NotEscritura(
                notaria=current_user.autoridad,
                juzgado=juzgado,
                contenido=form.contenido.data,
                estado=form.estado.data,
                expediente=form.expediente.data,
            )

            not_escritura.save()
            bitacora = Bitacora(
                modulo=Modulo.query.filter_by(nombre=MODULO).first(),
                usuario=current_user,
                descripcion=safe_message(f"Nuevo Escrituras {not_escritura.id}"),
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
    return render_template("not_escrituras/new.jinja2", buscar=buscar, form=form)


@not_escrituras.route("/not_escrituras/edicion/<int:not_escritura_id>", methods=["GET", "POST"])
@permission_required(MODULO, Permiso.MODIFICAR)
def edit(not_escritura_id):
    """Editar Escrituras"""
    not_escritura = NotEscritura.query.get_or_404(not_escritura_id)
    if not_escritura.estado not in ["TRABAJANDO", "CORRECCIONES"]:
        flash(f"No puede editar la escritura porque ya fue {not_escritura.estado}.", "warning")
        return redirect(url_for("not_escrituras.detail", not_escritura_id=not_escritura_id))
    form = NotEscriturasEditForm()
    if form.validate_on_submit():
        if form.estado.data not in NotEscritura.ESTADOS:
            flash("No es un estado valido", "warning")
        else:
            juzgado = Autoridad.query.get_or_404(form.juzgado.data)
            not_escritura.contenido = form.contenido.data
            not_escritura.juzgado = juzgado
            not_escritura.estado = form.estado.data
            not_escritura.expediente = form.expediente.data
            not_escritura.save()
            bitacora = Bitacora(
                modulo=Modulo.query.filter_by(nombre=MODULO).first(),
                usuario=current_user,
                descripcion=safe_message(f"Editado Escrituras {not_escritura.id}"),
                url=url_for("not_escrituras.detail", not_escritura_id=not_escritura.id),
            )
            bitacora.save()
            flash(bitacora.descripcion, "success")
            return redirect(bitacora.url)
    form.distrito.data = not_escritura.notaria.distrito.nombre
    form.notaria.data = not_escritura.notaria.descripcion
    form.juzgado.data = not_escritura.juzgado_id
    form.expediente.data = not_escritura.expediente
    form.contenido.data = not_escritura.contenido
    buscar = "Busca un juzgado o notaria"
    if current_user.autoridad.es_notaria:
        buscar = "JUZGADO"
    elif current_user.autoridad.es_jurisdiccional:
        buscar = "NOTARIA"
    return render_template(
        "not_escrituras/editar_borrador.jinja2",
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
    if not_escritura.estado not in ["TRABAJANDO", "CORRECCIONES"]:
        flash(f"No puede editar la escritura porque ya fue {not_escritura.estado}.", "warning")
        return redirect(url_for("not_escrituras.detail", not_escritura_id=not_escritura_id))
    form = NotEscriturasEditJuzgadoForm()
    if form.validate_on_submit():
        if form.estado.data not in NotEscritura.ESTADOS:
            flash("No es un estado valido", "warning")
        else:
            # juzgado = Autoridad.query.get_or_404(form.juzgado.data)
            not_escritura.contenido = form.contenido.data
            # not_escritura.juzgado = juzgado
            not_escritura.estado = form.estado.data
            not_escritura.expediente = form.expediente.data
            # not_escritura.save()
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
    form.distrito.data = not_escritura.notaria.distrito.nombre
    form.notaria.data = not_escritura.notaria.descripcion
    form.juzgado.data = not_escritura.juzgado_id
    form.expediente.data = not_escritura.expediente
    form.contenido.data = not_escritura.contenido
    buscar = "Busca un juzgado o notaria"
    if current_user.autoridad.es_notaria:
        buscar = "JUZGADO"
    elif current_user.autoridad.es_jurisdiccional:
        buscar = "NOTARIA"
    return render_template(
        "not_escrituras/edit_juzgado.jinja2",
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


@not_escrituras.route("/not_escrituras/select_juzgados_escrituras/<string:tipo>", methods=["POST"])
def select_juzgados_escrituras(tipo):
    """Listado de Autoridades filtrar por juzgado"""
    # Consultar
    consulta = Autoridad.query
    if tipo == "juzgado":
        consulta = consulta.filter_by(estatus="A").filter_by(es_notaria=False)
    elif tipo == "notaria":
        consulta = consulta.filter_by(estatus="A").filter_by(es_notaria=True)
    if "searchString" in request.form:
        busqueda = request.form["searchString"]
        consulta = consulta.filter(or_(Autoridad.clave.contains(busqueda), Autoridad.descripcion.contains(busqueda)))
        consulta = consulta.order_by(Autoridad.id).limit(15).all()

    # Elaborar datos para el Select2
    results = []
    for autoridad in consulta:
        results.append({"id": autoridad.id, "text": autoridad.clave + " : " + autoridad.descripcion})

    return {"results": results, "pagination": {"more": False}}

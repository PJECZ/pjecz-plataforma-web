"""
Ubicacion de Expedientes, vistas
"""
import json
from flask import Blueprint, flash, redirect, request, render_template, url_for
from flask_login import current_user, login_required
from lib.safe_string import safe_expediente, safe_message

from plataforma_web.blueprints.roles.models import Permiso
from plataforma_web.blueprints.usuarios.decorators import permission_required

from plataforma_web.blueprints.autoridades.models import Autoridad
from plataforma_web.blueprints.bitacoras.models import Bitacora
from plataforma_web.blueprints.distritos.models import Distrito
from plataforma_web.blueprints.ubicaciones_expedientes.models import UbicacionExpediente
from plataforma_web.blueprints.ubicaciones_expedientes.forms import UbicacionExpedienteNewForm, UbicacionExpedienteEditForm, UbicacionExpedienteSearchForm, UbicacionExpedienteSearchAdminForm

ubicaciones_expedientes = Blueprint("ubicaciones_expedientes", __name__, template_folder="templates")

MODULO = "UBICACIONES DE EXPEDIENTES"


@ubicaciones_expedientes.before_request
@login_required
@permission_required(Permiso.VER_JUSTICIABLES)
def before_request():
    """Permiso por defecto"""


@ubicaciones_expedientes.route("/ubicaciones_expedientes")
def list_active():
    """Listado de Ubicaciones de Expedientes"""
    # Si es administrador ve todo
    if current_user.can_admin("ubicaciones_expedientes"):
        return render_template(
            "ubicaciones_expedientes/list_admin.jinja2",
            autoridad=None,
            filtros=json.dumps({"estatus": "A"}),
            titulo="Todas las Ubicaciones de Expedientes",
        )
    # Si es jurisdiccional ve lo de su autoridad
    if current_user.autoridad.es_jurisdiccional:
        autoridad = current_user.autoridad
        return render_template(
            "ubicaciones_expedientes/list.jinja2",
            autoridad=autoridad,
            filtros=json.dumps({"autoridad_id": autoridad.id, "estatus": "A"}),
            titulo=f"Ubicaciones de Expedientes de {autoridad.distrito.nombre_corto}, {autoridad.descripcion_corta}",
        )
    # Ninguno de los anteriores, se redirige al listado de distritos
    return redirect(url_for("ubicaciones_expedientes.list_distritos"))


@ubicaciones_expedientes.route("/ubicaciones_expedientes/inactivos")
@permission_required(Permiso.MODIFICAR_JUSTICIABLES)
def list_inactive():
    """Listado de Ubicaciones de Expedientes inactivos"""
    # Si es administrador ve todo
    if current_user.can_admin("ubicaciones_expedientes"):
        return render_template(
            "ubicaciones_expedientes/list_admin.jinja2",
            autoridad=None,
            filtros=json.dumps({"estatus": "B"}),
            titulo="Todas las Ubicaciones de Expedientes inactivos",
        )
    # Si es jurisdiccional ve lo de su autoridad
    if current_user.autoridad.es_jurisdiccional:
        autoridad = current_user.autoridad
        return render_template(
            "ubicaciones_expedientes/list.jinja2",
            autoridad=autoridad,
            filtros=json.dumps({"autoridad_id": autoridad.id, "estatus": "B"}),
            titulo=f"Ubicaciones de Expedientes inactivos de {autoridad.distrito.nombre_corto}, {autoridad.descripcion_corta}",
        )
    # Ninguno de los anteriores, se redirige al listado de distritos
    return redirect(url_for("ubicaciones_expedientes.list_distritos"))


@ubicaciones_expedientes.route("/ubicaciones_expedientes/distritos")
def list_distritos():
    """Listado de Distritos"""
    return render_template(
        "ubicaciones_expedientes/list_distritos.jinja2",
        distritos=Distrito.query.filter(Distrito.es_distrito_judicial == True).filter(Distrito.estatus == "A").order_by(Distrito.nombre).all(),
    )


@ubicaciones_expedientes.route("/ubicaciones_expedientes/distrito/<int:distrito_id>")
def list_autoridades(distrito_id):
    """Listado de Autoridades de un distrito"""
    distrito = Distrito.query.get_or_404(distrito_id)
    return render_template(
        "ubicaciones_expedientes/list_autoridades.jinja2",
        distrito=distrito,
        autoridades=Autoridad.query.filter(Autoridad.distrito == distrito).filter(Autoridad.es_jurisdiccional == True).filter(Autoridad.es_notaria == False).filter(Autoridad.estatus == "A").order_by(Autoridad.clave).all(),
    )


@ubicaciones_expedientes.route("/ubicaciones_expedientes/autoridad/<int:autoridad_id>")
def list_autoridad_ubicaciones_expedientes(autoridad_id):
    """Listado de Ubicaciones de Expedientes activas de una autoridad"""
    autoridad = Autoridad.query.get_or_404(autoridad_id)
    if current_user.can_admin("ubicaciones_expedientes"):
        plantilla = "ubicaciones_expedientes/list_admin.jinja2"
    else:
        plantilla = "ubicaciones_expedientes/list.jinja2"
    return render_template(
        plantilla,
        autoridad=autoridad,
        filtros=json.dumps({"autoridad_id": autoridad.id, "estatus": "A"}),
        titulo=f"Ubicaciones de Expedientes de {autoridad.distrito.nombre_corto}, {autoridad.descripcion_corta}",
    )


@ubicaciones_expedientes.route("/ubicaciones_expedientes/inactivos/autoridad/<int:autoridad_id>")
@permission_required(Permiso.ADMINISTRAR_JUSTICIABLES)
def list_autoridad_ubicaciones_expedientes_inactive(autoridad_id):
    """Listado de Ubicaciones de Expedientes inactivos de una autoridad"""
    autoridad = Autoridad.query.get_or_404(autoridad_id)
    if current_user.can_admin("ubicaciones_expedientes"):
        plantilla = "ubicaciones_expedientes/list_admin.jinja2"
    else:
        plantilla = "ubicaciones_expedientes/list.jinja2"
    return render_template(
        plantilla,
        autoridad=autoridad,
        filtros=json.dumps({"autoridad_id": autoridad.id, "estatus": "B"}),
        titulo=f"Ubicaciones de Expedientes inactivas de {autoridad.distrito.nombre_corto}, {autoridad.descripcion_corta}",
    )


@ubicaciones_expedientes.route("/ubicaciones_expedientes/buscar", methods=["GET", "POST"])
def search():
    """Buscar Ubicacion de Expediente"""
    if current_user.can_admin("ubicaciones_expedientes"):
        puede_elegir_autoridad = True
    elif current_user.autoridad.es_jurisdiccional:
        puede_elegir_autoridad = False
    else:
        puede_elegir_autoridad = True
    if puede_elegir_autoridad:
        form_search = UbicacionExpedienteSearchAdminForm()  # Puede elegir la autoridad
    else:
        form_search = UbicacionExpedienteSearchForm()  # Sólo puede buscar en su autoridad
    if form_search.validate_on_submit():
        busqueda = {"estatus": "A"}
        titulos = []
        # Autoridad es un campo obligatorio
        if puede_elegir_autoridad:
            autoridad = Autoridad.query.get(form_search.autoridad.data)
            plantilla = "ubicaciones_expedientes/list_admin.jinja2"
        else:
            autoridad = current_user.autoridad
            plantilla = "ubicaciones_expedientes/list.jinja2"
        busqueda["autoridad_id"] = autoridad.id
        titulos.append(autoridad.distrito.nombre_corto + ", " + autoridad.descripcion_corta)
        # Expediente es un campo obligatorio
        busqueda["expediente"] = safe_expediente(form_search.expediente.data)
        titulos.append("expediente " + busqueda["expediente"])
        # Mostrar resultados
        return render_template(
            plantilla,
            filtros=json.dumps(busqueda),
            titulo="Ubicaciones de Expedientes con " + ", ".join(titulos),
        )
    # Mostrar buscador donde puede elegir la autoridad
    if puede_elegir_autoridad:
        return render_template(
            "ubicaciones_expedientes/search_admin.jinja2",
            form=form_search,
            distritos=Distrito.query.filter(Distrito.es_distrito_judicial == True).filter(Distrito.estatus == "A").order_by(Distrito.nombre).all(),
            autoridades=Autoridad.query.filter(Autoridad.es_jurisdiccional == True).filter(Autoridad.es_notaria == False).filter(Autoridad.estatus == "A").order_by(Autoridad.clave).all(),
        )
    # Mostrar buscador con la autoridad fija
    form_search.distrito.data = current_user.autoridad.distrito.nombre
    form_search.autoridad.data = current_user.autoridad.descripcion
    return render_template("ubicaciones_expedientes/search.jinja2", form=form_search)


@ubicaciones_expedientes.route("/ubicaciones_expedientes/datatable_json", methods=["GET", "POST"])
def datatable_json():
    """DataTable JSON para listado de ubicaciones de expedientes"""

    # Tomar parámetros de Datatables
    try:
        draw = int(request.form["draw"])
        start = int(request.form["start"])
        rows_per_page = int(request.form["length"])
    except (TypeError, ValueError):
        draw = 1
        start = 1
        rows_per_page = 10

    # Consultar
    consulta = UbicacionExpediente.query
    if "estatus" in request.form:
        consulta = consulta.filter(UbicacionExpediente.estatus == request.form["estatus"])
    else:
        consulta = consulta.filter(UbicacionExpediente.estatus == "A")
    if "autoridad_id" in request.form:
        autoridad = Autoridad.query.get(request.form["autoridad_id"])
        if autoridad:
            consulta = consulta.filter(UbicacionExpediente.autoridad == autoridad)
    if "expediente" in request.form:
        try:
            consulta = consulta.filter(UbicacionExpediente.expediente == safe_expediente(request.form["expediente"]))
        except (IndexError, ValueError):
            pass
    registros = consulta.order_by(UbicacionExpediente.creado.desc()).offset(start).limit(rows_per_page).all()
    total = consulta.count()

    # Elaborar datos para DataTable
    data = []
    for ubicacion_expediente in registros:
        data.append(
            {
                "creado": ubicacion_expediente.creado.strftime("%Y-%m-%d %H:%M:%S"),
                "detalle": {
                    "expediente": ubicacion_expediente.expediente,
                    "url": url_for("ubicaciones_expedientes.detail", ubicacion_expediente_id=ubicacion_expediente.id),
                },
                "ubicacion": ubicacion_expediente.ubicacion,
            }
        )

    # Entregar JSON
    return {
        "draw": draw,
        "iTotalRecords": total,
        "iTotalDisplayRecords": total,
        "aaData": data,
    }


@ubicaciones_expedientes.route("/ubicaciones_expedientes/datatable_json_admin", methods=["GET", "POST"])
@permission_required(Permiso.ADMINISTRAR_JUSTICIABLES)
def datatable_json_admin():
    """DataTable JSON para listado de ubicaciones de expedientes admin"""

    # Tomar parámetros de Datatables
    try:
        draw = int(request.form["draw"])
        start = int(request.form["start"])
        rows_per_page = int(request.form["length"])
    except (TypeError, ValueError):
        draw = 1
        start = 1
        rows_per_page = 10

    # Consultar
    consulta = UbicacionExpediente.query
    if "estatus" in request.form:
        consulta = consulta.filter(UbicacionExpediente.estatus == request.form["estatus"])
    else:
        consulta = consulta.filter(UbicacionExpediente.estatus == "A")
    if "autoridad_id" in request.form:
        autoridad = Autoridad.query.get(request.form["autoridad_id"])
        if autoridad:
            consulta = consulta.filter(UbicacionExpediente.autoridad == autoridad)
    if "expediente" in request.form:
        try:
            consulta = consulta.filter(UbicacionExpediente.expediente == safe_expediente(request.form["expediente"]))
        except (IndexError, ValueError):
            pass
    registros = consulta.order_by(UbicacionExpediente.creado.desc()).offset(start).limit(rows_per_page).all()
    total = consulta.count()

    # Elaborar datos para DataTable
    data = []
    for ubicacion_expediente in registros:
        data.append(
            {
                "creado": ubicacion_expediente.creado.strftime("%Y-%m-%d %H:%M:%S"),
                "autoridad": ubicacion_expediente.autoridad.clave,
                "detalle": {
                    "expediente": ubicacion_expediente.expediente,
                    "url": url_for("ubicaciones_expedientes.detail", ubicacion_expediente_id=ubicacion_expediente.id),
                },
                "ubicacion": ubicacion_expediente.ubicacion,
            }
        )

    # Entregar JSON
    return {
        "draw": draw,
        "iTotalRecords": total,
        "iTotalDisplayRecords": total,
        "aaData": data,
    }


@ubicaciones_expedientes.route("/ubicaciones_expedientes/<int:ubicacion_expediente_id>")
def detail(ubicacion_expediente_id):
    """Detalle de una Ubicacion de Expediente"""
    ubicacion_expediente = UbicacionExpediente.query.get_or_404(ubicacion_expediente_id)
    return render_template("ubicaciones_expedientes/detail.jinja2", ubicacion_expediente=ubicacion_expediente)


def new_success(ubicacion_expediente):
    """Mensaje de éxito en nueva ubicación de expediente"""
    bitacora = Bitacora(
        modulo=MODULO,
        usuario=current_user,
        descripcion=safe_message(f"Nueva ubicación del expediente {ubicacion_expediente.expediente} en {ubicacion_expediente.ubicacion} de {ubicacion_expediente.autoridad.clave}"),
        url=url_for("ubicaciones_expedientes.detail", ubicacion_expediente_id=ubicacion_expediente.id),
    )
    bitacora.save()
    return bitacora


@ubicaciones_expedientes.route("/ubicaciones_expedientes/nuevo", methods=["GET", "POST"])
@permission_required(Permiso.CREAR_JUSTICIABLES)
def new():
    """Nuevo Ubicación de Expedientes como juzgado"""

    # Validar autoridad
    autoridad = current_user.autoridad
    if autoridad is None or autoridad.estatus != "A":
        flash("El juzgado/autoridad no existe o no es activa.", "warning")
        return redirect(url_for("ubicaciones_expedientes.list_active"))
    if not autoridad.distrito.es_distrito_judicial:
        flash("El juzgado/autoridad no está en un distrito jurisdiccional.", "warning")
        return redirect(url_for("ubicaciones_expedientes.list_active"))
    if not autoridad.es_jurisdiccional:
        flash("El juzgado/autoridad no es jurisdiccional.", "warning")
        return redirect(url_for("ubicaciones_expedientes.list_active"))

    # Si viene el formulario
    form = UbicacionExpedienteNewForm()
    if form.validate_on_submit():

        # Validar expediente
        try:
            expediente = safe_expediente(form.expediente.data)
        except (IndexError, ValueError):
            flash("El expediente es incorrecto.", "warning")
            return render_template("ubicaciones_expedientes/new.jinja2", form=form)

        # Ubicación
        ubicacion = form.ubicacion.data

        # Insertar registro
        ubicacion_expediente = UbicacionExpediente(
            autoridad=autoridad,
            expediente=expediente,
            ubicacion=ubicacion,
        )
        ubicacion_expediente.save()

        # Mostrar mensaje de éxito e ir al detalle
        bitacora = new_success(ubicacion_expediente)
        flash(bitacora.descripcion, "success")
        return redirect(bitacora.url)

    # Prellenado del formulario
    form.distrito.data = autoridad.distrito.nombre
    form.autoridad.data = autoridad.descripcion
    return render_template("ubicaciones_expedientes/new.jinja2", form=form)


@ubicaciones_expedientes.route("/ubicaciones_expedientes/nuevo/<int:autoridad_id>", methods=["GET", "POST"])
@permission_required(Permiso.CREAR_JUSTICIABLES)
def new_for_autoridad(autoridad_id):
    """Nuevo Ubicación de Expedientes para una autoridad dada"""

    # Validar autoridad
    autoridad = Autoridad.query.get_or_404(autoridad_id)
    if autoridad is None:
        flash("El juzgado/autoridad no existe.", "warning")
        return redirect(url_for("ubicaciones_expedientes.list_active"))
    if autoridad.estatus != "A":
        flash("El juzgado/autoridad no es activa.", "warning")
        return redirect(url_for("autoridades.detail", autoridad_id=autoridad.id))
    if not autoridad.distrito.es_distrito_judicial:
        flash("El juzgado/autoridad no está en un distrito jurisdiccional.", "warning")
        return redirect(url_for("autoridades.detail", autoridad_id=autoridad.id))
    if not autoridad.es_jurisdiccional:
        flash("El juzgado/autoridad no es jurisdiccional.", "warning")
        return redirect(url_for("autoridades.detail", autoridad_id=autoridad.id))

    # Si viene el formulario
    form = UbicacionExpedienteNewForm()
    if form.validate_on_submit():

        # Validar expediente
        try:
            expediente = safe_expediente(form.expediente.data)
        except (IndexError, ValueError):
            flash("El expediente es incorrecto.", "warning")
            return render_template("ubicaciones_expedientes/new.jinja2", form=form)

        # Ubicación
        ubicacion = form.ubicacion.data

        # Insertar registro
        ubicacion_expediente = UbicacionExpediente(
            autoridad=autoridad,
            expediente=expediente,
            ubicacion=ubicacion,
        )
        ubicacion_expediente.save()

        # Registrar en bitácoras e ir al detalle
        bitacora = new_success(ubicacion_expediente)
        flash(bitacora.descripcion, "success")
        return redirect(bitacora.url)

    # Prellenado del formulario
    form.distrito.data = autoridad.distrito.nombre
    form.autoridad.data = autoridad.descripcion
    return render_template("ubicaciones_expedientes/new_for_autoridad.jinja2", form=form, autoridad=autoridad)


def edit_success(ubicacion_expediente):
    """Mensaje de éxito al editar una ubicación de expediente"""
    bitacora = Bitacora(
        modulo=MODULO,
        usuario=current_user,
        descripcion=safe_message(f"Editada la ubicación del expediente {ubicacion_expediente.expediente} en {ubicacion_expediente.ubicacion} de {ubicacion_expediente.autoridad.clave}"),
        url=url_for("ubicaciones_expedientes.detail", ubicacion_expediente_id=ubicacion_expediente.id),
    )
    bitacora.save()
    return bitacora


@ubicaciones_expedientes.route("/ubicaciones_expedientes/edicion/<int:ubicacion_expediente_id>", methods=["GET", "POST"])
@permission_required(Permiso.MODIFICAR_JUSTICIABLES)
def edit(ubicacion_expediente_id):
    """Editar Ubicación de Expedientes"""

    # Validar ubicación de expediente
    ubicacion_expediente = UbicacionExpediente.query.get_or_404(ubicacion_expediente_id)
    if not (current_user.can_admin("ubicaciones_expedientes") or current_user.autoridad_id == ubicacion_expediente.autoridad_id):
        flash("No tiene permiso para editar esta ubicación de expediente.", "warning")
        return redirect(url_for("ubicaciones_expedientes.list_active"))

    form = UbicacionExpedienteEditForm()
    if form.validate_on_submit():

        # Validar expediente
        try:
            expediente = safe_expediente(form.expediente.data)
        except (IndexError, ValueError):
            flash("El expediente es incorrecto.", "warning")
            return render_template("ubicaciones_expedientes/new.jinja2", form=form)

        # Actualizar registro
        ubicacion_expediente.expediente = expediente
        ubicacion_expediente.ubicacion = form.ubicacion.data
        ubicacion_expediente.save()

        # Registrar en bitácora e ir al detalle
        bitacora = edit_success(ubicacion_expediente)
        flash(bitacora.descripcion, "success")
        return redirect(bitacora.url)

    # Prellenado del formulario
    form.expediente.data = ubicacion_expediente.expediente
    form.ubicacion.data = ubicacion_expediente.ubicacion
    return render_template("ubicaciones_expedientes/edit.jinja2", form=form, ubicacion_expediente=ubicacion_expediente)


def delete_success(ubicacion_expediente):
    """Mensaje de éxito al eliminar una ubicacion de expediente"""
    bitacora = Bitacora(
        modulo=MODULO,
        usuario=current_user,
        descripcion=safe_message(f"Eliminada la ubicación del expediente {ubicacion_expediente.expediente} de {ubicacion_expediente.autoridad.clave}"),
        url=url_for("ubicaciones_expedientes.detail", ubicacion_expediente_id=ubicacion_expediente.id),
    )
    bitacora.save()
    return bitacora


@ubicaciones_expedientes.route("/ubicaciones_expedientes/eliminar/<int:ubicacion_expediente_id>")
@permission_required(Permiso.MODIFICAR_JUSTICIABLES)
def delete(ubicacion_expediente_id):
    """Eliminar Ubicacion de Expedientes"""
    ubicacion_expediente = UbicacionExpediente.query.get_or_404(ubicacion_expediente_id)
    if ubicacion_expediente.estatus == "A":
        if current_user.can_admin("ubicaciones_expedientes") or current_user.autoridad_id == ubicacion_expediente.autoridad_id:
            ubicacion_expediente.delete()
            bitacora = delete_success(ubicacion_expediente)
            flash(bitacora.descripcion, "success")
            return redirect(bitacora.url)
        flash("No tiene permiso para eliminar.", "warning")
    return redirect(url_for("ubicaciones_expedientes.detail", ubicacion_expediente_id=ubicacion_expediente_id))


def recover_success(ubicacion_expediente):
    """Mensaje de éxito al recuperar una ubicacion de expediente"""
    bitacora = Bitacora(
        modulo=MODULO,
        usuario=current_user,
        descripcion=safe_message(f"Recuperada la ubicación del expediente {ubicacion_expediente.expediente} de {ubicacion_expediente.autoridad.clave}"),
        url=url_for("ubicaciones_expedientes.detail", ubicacion_expediente_id=ubicacion_expediente.id),
    )
    bitacora.save()
    return bitacora


@ubicaciones_expedientes.route("/ubicaciones_expedientes/recuperar/<int:ubicacion_expediente_id>")
@permission_required(Permiso.MODIFICAR_JUSTICIABLES)
def recover(ubicacion_expediente_id):
    """Recuperar Ubicacion de Expedientes"""
    ubicacion_expediente = UbicacionExpediente.query.get_or_404(ubicacion_expediente_id)
    if ubicacion_expediente.estatus == "B":
        if current_user.can_admin("ubicaciones_expedientes") or current_user.autoridad_id == ubicacion_expediente.autoridad_id:
            ubicacion_expediente.recover()
            bitacora = recover_success(ubicacion_expediente)
            flash(bitacora.descripcion, "success")
            return redirect(bitacora.url)
        flash("No tiene permiso para recuperar.", "warning")
    return redirect(url_for("ubicaciones_expedientes.detail", ubicacion_expediente_id=ubicacion_expediente_id))

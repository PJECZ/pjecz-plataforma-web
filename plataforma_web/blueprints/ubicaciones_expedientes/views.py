"""
Ubicacion de Expedientes, vistas
"""
from flask import Blueprint, flash, redirect, render_template, url_for
from flask_login import current_user, login_required
from lib.safe_string import safe_expediente, safe_message

from plataforma_web.blueprints.roles.models import Permiso
from plataforma_web.blueprints.usuarios.decorators import permission_required

from plataforma_web.blueprints.autoridades.models import Autoridad
from plataforma_web.blueprints.bitacoras.models import Bitacora
from plataforma_web.blueprints.distritos.models import Distrito
from plataforma_web.blueprints.ubicaciones_expedientes.models import UbicacionExpediente
from plataforma_web.blueprints.ubicaciones_expedientes.forms import UbicacionExpedienteNewForm, UbicacionExpedienteEditForm, UbicacionExpedienteSearchForm

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
    # Si es administrador, ve las ubicaciones de expedientes de todas las autoridades
    if current_user.can_admin("ubicaciones_expedientes"):
        ubicaciones_expedientes_activos = UbicacionExpediente.query.filter(UbicacionExpediente.estatus == "A").order_by(UbicacionExpediente.creado.desc()).limit(100).all()
        return render_template("ubicaciones_expedientes/list_admin.jinja2", autoridad=None, ubicaciones_expedientes=ubicaciones_expedientes_activos, estatus="A")
    # No es administrador, consultar su autoridad
    if current_user.autoridad.es_jurisdiccional:
        sus_ubicaciones_expedientes_activos = UbicacionExpediente.query.filter(UbicacionExpediente.autoridad == current_user.autoridad).filter(UbicacionExpediente.estatus == "A").order_by(UbicacionExpediente.creado.desc()).limit(100).all()
        return render_template("ubicaciones_expedientes/list.jinja2", autoridad=current_user.autoridad, ubicaciones_expedientes=sus_ubicaciones_expedientes_activos, estatus="A")
    # No es jurisdiccional, se redirige al listado de distritos
    return redirect(url_for("ubicaciones_expedientes.list_distritos"))


@ubicaciones_expedientes.route("/ubicaciones_expedientes/inactivos")
@permission_required(Permiso.MODIFICAR_JUSTICIABLES)
def list_inactive():
    """Listado de Ubicaciones de Expedientes inactivos"""
    # Si es administrador, ve las ubicaciones de expedientes de todas las autoridades
    if current_user.can_admin("ubicaciones_expedientes"):
        ubicaciones_expedientes_inactivos = UbicacionExpediente.query.filter(UbicacionExpediente.estatus == "B").order_by(UbicacionExpediente.creado.desc()).limit(100).all()
        return render_template("ubicaciones_expedientes/list_admin.jinja2", autoridad=None, ubicaciones_expedientes=ubicaciones_expedientes_inactivos, estatus="B")
    # No es administrador, consultar su autoridad
    if current_user.autoridad.es_jurisdiccional:
        sus_ubicaciones_expedientes_inactivos = UbicacionExpediente.query.filter(UbicacionExpediente.autoridad == current_user.autoridad).filter(UbicacionExpediente.estatus == "B").order_by(UbicacionExpediente.creado.desc()).limit(100).all()
        return render_template("ubicaciones_expedientes/list.jinja2", autoridad=current_user.autoridad, ubicaciones_expedientes=sus_ubicaciones_expedientes_inactivos, estatus="B")
    # No es jurisdiccional, se redirige al listado de distritos
    return redirect(url_for("ubicaciones_expedientes.list_distritos"))


@ubicaciones_expedientes.route("/ubicaciones_expedientes/distritos")
def list_distritos():
    """Listado de Distritos"""
    distritos = Distrito.query.filter(Distrito.es_distrito_judicial == True).filter(Distrito.estatus == "A").order_by(Distrito.nombre).all()
    return render_template("ubicaciones_expedientes/list_distritos.jinja2", distritos=distritos)


@ubicaciones_expedientes.route("/ubicaciones_expedientes/distrito/<int:distrito_id>")
def list_autoridades(distrito_id):
    """Listado de Autoridades de un distrito"""
    distrito = Distrito.query.get_or_404(distrito_id)
    autoridades = Autoridad.query.filter(Autoridad.distrito == distrito).filter(Autoridad.es_jurisdiccional == True).filter(Autoridad.es_notaria == False).filter(Autoridad.estatus == "A").order_by(Autoridad.clave).all()
    return render_template("ubicaciones_expedientes/list_autoridades.jinja2", distrito=distrito, autoridades=autoridades)


@ubicaciones_expedientes.route("/ubicaciones_expedientes/autoridad/<int:autoridad_id>")
def list_autoridad_ubicaciones_expedientes(autoridad_id):
    """Listado de Ubicaciones de Expedientes activasode una autoridad"""
    autoridad = Autoridad.query.get_or_404(autoridad_id)
    ubicaciones_expedientes_activos = UbicacionExpediente.query.filter(UbicacionExpediente.autoridad == autoridad).filter(UbicacionExpediente.estatus == "A").order_by(UbicacionExpediente.creado.desc()).limit(100).all()
    return render_template("ubicaciones_expedientes/list.jinja2", autoridad=autoridad, ubicaciones_expedientes=ubicaciones_expedientes_activos, estatus="A")


@ubicaciones_expedientes.route("/ubicaciones_expedientes/inactivos/autoridad/<int:autoridad_id>")
@permission_required(Permiso.ADMINISTRAR_JUSTICIABLES)
def list_autoridad_ubicaciones_expedientes_inactive(autoridad_id):
    """Listado de Ubicaciones de Expedientes inactivos de una autoridad"""
    autoridad = Autoridad.query.get_or_404(autoridad_id)
    ubicaciones_expedientes_inactivos = UbicacionExpediente.query.filter(UbicacionExpediente.autoridad == autoridad).filter(UbicacionExpediente.estatus == "B").order_by(UbicacionExpediente.creado.desc()).limit(100).all()
    return render_template("ubicaciones_expedientes/list.jinja2", autoridad=autoridad, ubicaciones_expedientes=ubicaciones_expedientes_inactivos, estatus="B")


@ubicaciones_expedientes.route("/ubicaciones_expedientes/<int:ubicacion_expediente_id>")
def detail(ubicacion_expediente_id):
    """Detalle de una Ubicacion de Expediente"""
    ubicacion_expediente = UbicacionExpediente.query.get_or_404(ubicacion_expediente_id)
    return render_template("ubicaciones_expedientes/detail.jinja2", ubicacion_expediente=ubicacion_expediente)


@ubicaciones_expedientes.route("/ubicaciones_expedientes/buscar", methods=["GET", "POST"])
def search():
    """Buscar Ubicacion de Expediente"""
    form_search = UbicacionExpedienteSearchForm()
    if form_search.validate_on_submit():
        mostrar_resultados = True

        # Los administradores pueden buscar en todas las autoridades
        if current_user.can_admin("sentencias"):
            autoridad = Autoridad.query.get(form_search.autoridad.data)
        else:
            autoridad = Autoridad.query.get(current_user.autoridad)
        consulta = UbicacionExpediente.query.filter(UbicacionExpediente.autoridad == autoridad)

        # Expediente
        try:
            expediente = safe_expediente(form_search.expediente.data)
            consulta = consulta.filter(UbicacionExpediente.expediente == expediente)
        except (IndexError, ValueError):
            flash("El expediente es incorrecto.", "warning")
            mostrar_resultados = False

        # Mostrar resultados
        if mostrar_resultados:
            consulta = consulta.order_by(UbicacionExpediente.creado.desc()).limit(100).all()
            return render_template("ubicaciones_expedientes/list.jinja2", ubicaciones_expedientes=consulta)

    # Los administradores pueden buscar en todas las autoridades
    if current_user.can_admin("sentencias"):
        distritos = Distrito.query.filter(Distrito.es_distrito_judicial == True).filter(Distrito.estatus == "A").order_by(Distrito.nombre).all()
        autoridades = Autoridad.query.filter(Autoridad.es_jurisdiccional == True).filter(Autoridad.es_notaria == False).filter(Autoridad.estatus == "A").order_by(Autoridad.clave).all()
        return render_template("ubicaciones_expedientes/search_admin.jinja2", form=form_search, distritos=distritos, autoridades=autoridades)
    return render_template("ubicaciones_expedientes/search.jinja2", form=form_search)


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
    ubicacion_expediente = UbicacionExpediente.query.get_or_404(ubicacion_expediente_id)
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
        if current_user.can_admin("sentencias") or current_user.autoridad_id == ubicacion_expediente.autoridad_id:
            ubicacion_expediente.delete()
            bitacora = delete_success(ubicacion_expediente)
            flash(bitacora.descripcion, "success")
            return redirect(bitacora.url)
        else:
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
        if current_user.can_admin("sentencias") or current_user.autoridad_id == ubicacion_expediente.autoridad_id:
            ubicacion_expediente.recover()
            bitacora = recover_success(ubicacion_expediente)
            flash(bitacora.descripcion, "success")
            return redirect(bitacora.url)
        else:
            flash("No tiene permiso para recuperar.", "warning")
    return redirect(url_for("ubicaciones_expedientes.detail", ubicacion_expediente_id=ubicacion_expediente_id))

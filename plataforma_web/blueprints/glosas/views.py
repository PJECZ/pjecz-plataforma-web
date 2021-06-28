"""
Glosas, vistas
"""
import datetime
from pathlib import Path

from flask import Blueprint, current_app, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required
from google.cloud import storage
from werkzeug.datastructures import CombinedMultiDict
from werkzeug.utils import secure_filename
from lib.safe_string import safe_expediente, safe_message, safe_string
from lib.time_to_text import dia_mes_ano, mes_en_palabra

from plataforma_web.blueprints.roles.models import Permiso
from plataforma_web.blueprints.usuarios.decorators import permission_required

from plataforma_web.blueprints.autoridades.models import Autoridad
from plataforma_web.blueprints.bitacoras.models import Bitacora
from plataforma_web.blueprints.distritos.models import Distrito
from plataforma_web.blueprints.glosas.forms import GlosaEditForm, GlosaNewForm, GlosaSearchForm
from plataforma_web.blueprints.glosas.models import Glosa

glosas = Blueprint("glosas", __name__, template_folder="templates")

MODULO = "GLOSAS"
SUBDIRECTORIO = "Glosas"
LIMITE_DIAS = 30
LIMITE_ADMINISTRADORES_DIAS = 90
CONSULTAS_LIMITE = 100


@glosas.route("/glosas/acuses/<id_hashed>")
def checkout(id_hashed):
    """Acuse"""
    glosa = Glosa.query.get_or_404(Glosa.decode_id(id_hashed))
    dia, mes, ano = dia_mes_ano(glosa.creado)
    return render_template("glosas/checkout.jinja2", glosa=glosa, dia=dia, mes=mes.upper(), ano=ano)


@glosas.before_request
@login_required
@permission_required(Permiso.VER_SEGUNDAS)
def before_request():
    """Permiso por defecto"""


@glosas.route("/glosas")
def list_active():
    """Listado de Glosas activos"""
    # Si es administrador, ve las glosas de todas las autoridades
    if current_user.can_admin("glosas"):
        glosas_activas = Glosa.query.filter(Glosa.estatus == "A").order_by(Glosa.fecha.desc()).limit(CONSULTAS_LIMITE).all()
        return render_template("glosas/list_admin.jinja2", autoridad=None, glosas=glosas_activas, estatus="A")
    # Si puede editar o crear glosas
    if current_user.can_edit("glosas") or current_user.can_insert("glosas"):
        autoridad = Autoridad.query.get_or_404(current_user.autoridad_id)
        sus_glosas_activas = Glosa.query.filter(Glosa.autoridad == autoridad).filter(Glosa.estatus == "A").order_by(Glosa.fecha.desc()).limit(CONSULTAS_LIMITE).all()
        return render_template("glosas/list.jinja2", autoridad=autoridad, glosas=sus_glosas_activas, estatus="A")
    # No es ninguno de los anteriores
    glosas_activas = Glosa.query.filter(Glosa.estatus == "A").order_by(Glosa.fecha.desc()).limit(CONSULTAS_LIMITE).all()
    return render_template("glosas/list.jinja2", autoridad=None, glosas=glosas_activas, estatus="A")


@glosas.route("/glosas/inactivos")
@permission_required(Permiso.MODIFICAR_SEGUNDAS)
def list_inactive():
    """Listado de Glosas inactivas"""
    # Si es administrador, ve las glosas de todas las autoridades
    if current_user.can_admin("glosas"):
        glosas_inactivas = Glosa.query.filter(Glosa.estatus == "B").order_by(Glosa.creado.desc()).limit(CONSULTAS_LIMITE).all()
        return render_template("glosas/list_admin.jinja2", autoridad=None, glosas=glosas_inactivas, estatus="B")
    # Si es jurisdiccional, ve sus propios glosas
    if current_user.autoridad.es_jurisdiccional:
        sus_glosas_inactivas = Glosa.query.filter(Glosa.autoridad == current_user.autoridad).filter(Glosa.estatus == "B").order_by(Glosa.fecha.desc()).limit(CONSULTAS_LIMITE).all()
        return render_template("glosas/list.jinja2", autoridad=current_user.autoridad, glosas=sus_glosas_inactivas, estatus="B")
    # No es jurisdiccional, se redirige al listado de distritos
    return redirect(url_for("glosas.list_distritos"))


@glosas.route("/glosas/distritos")
def list_distritos():
    """Listado de Distritos"""
    distritos = Distrito.query.filter(Distrito.es_distrito_judicial == True).filter(Distrito.estatus == "A").order_by(Distrito.nombre).all()
    return render_template("glosas/list_distritos.jinja2", distritos=distritos)


@glosas.route("/glosas/distrito/<int:distrito_id>")
def list_autoridades(distrito_id):
    """Listado de Autoridades de un distrito"""
    distrito = Distrito.query.get_or_404(distrito_id)
    autoridades = Autoridad.query.filter(Autoridad.distrito == distrito).filter(Autoridad.es_jurisdiccional == True).filter(Autoridad.es_notaria == False).filter(Autoridad.estatus == "A").order_by(Autoridad.clave).all()
    return render_template("glosas/list_autoridades.jinja2", distrito=distrito, autoridades=autoridades)


@glosas.route("/glosas/autoridad/<int:autoridad_id>")
def list_autoridad_glosas(autoridad_id):
    """Listado de Glosas activas de una autoridad"""
    autoridad = Autoridad.query.get_or_404(autoridad_id)
    glosas_activas = Glosa.query.filter(Glosa.autoridad == autoridad).filter(Glosa.estatus == "A").order_by(Glosa.fecha.desc()).limit(CONSULTAS_LIMITE).all()
    if current_user.can_admin("glosas"):
        return render_template("glosas/list_admin.jinja2", autoridad=autoridad, glosas=glosas_activas, estatus="A")
    return render_template("glosas/list.jinja2", autoridad=autoridad, glosas=glosas_activas, estatus="A")


@glosas.route("/glosas/inactivos/autoridad/<int:autoridad_id>")
@permission_required(Permiso.ADMINISTRAR_SEGUNDAS)
def list_autoridad_glosas_inactive(autoridad_id):
    """Listado de Glosas inactivas de una autoridad"""
    autoridad = Autoridad.query.get_or_404(autoridad_id)
    glosas_inactivas = Glosa.query.filter(Glosa.autoridad == autoridad).filter(Glosa.estatus == "B").order_by(Glosa.creado.desc()).limit(CONSULTAS_LIMITE).all()
    if current_user.can_admin("glosas"):
        return render_template("glosas/list_admin.jinja2", autoridad=autoridad, glosas=glosas_inactivas, estatus="B")
    return render_template("glosas/list.jinja2", autoridad=autoridad, glosas=glosas_inactivas, estatus="B")


@glosas.route("/glosas/refrescar/<int:autoridad_id>")
@permission_required(Permiso.ADMINISTRAR_SEGUNDAS)
def refresh(autoridad_id):
    """Refrescar Glosas"""
    autoridad = Autoridad.query.get_or_404(autoridad_id)
    if current_user.get_task_in_progress("glosas.tasks.refrescar"):
        flash("Debe esperar porque hay una tarea en el fondo sin terminar.", "warning")
    else:
        tarea = current_user.launch_task(
            nombre="glosas.tasks.refrescar",
            descripcion=f"Refrescar glosas de {autoridad.clave}",
            usuario_id=current_user.id,
            autoridad_id=autoridad.id,
        )
        flash(f"{tarea.descripcion} está corriendo en el fondo.", "info")
    return redirect(url_for("glosas.list_autoridad_glosas", autoridad_id=autoridad.id))


@glosas.route("/glosas/<int:glosa_id>")
def detail(glosa_id):
    """Detalle de una Lista de Acuerdos"""
    glosa = Glosa.query.get_or_404(glosa_id)
    return render_template("glosas/detail.jinja2", glosa=glosa)


@glosas.route("/glosas/buscar", methods=["GET", "POST"])
def search():
    """Buscar Glosas"""
    form_search = GlosaSearchForm()
    if form_search.validate_on_submit():
        autoridad = Autoridad.query.get(form_search.autoridad.data)
        consulta = Glosa.query.filter(Glosa.autoridad == autoridad)
        if form_search.fecha_desde.data:
            consulta = consulta.filter(Glosa.fecha >= form_search.fecha_desde.data)
        if form_search.fecha_hasta.data:
            consulta = consulta.filter(Glosa.fecha <= form_search.fecha_hasta.data)
        consulta = consulta.order_by(Glosa.creado.desc()).limit(CONSULTAS_LIMITE).all()
        return render_template("glosas/list.jinja2", glosas=consulta)
    distritos = Distrito.query.filter(Distrito.es_distrito_judicial == True).filter(Distrito.estatus == "A").order_by(Distrito.nombre).all()
    autoridades = Autoridad.query.filter(Autoridad.es_jurisdiccional == True).filter(Autoridad.es_notaria == False).filter(Autoridad.estatus == "A").order_by(Autoridad.clave).all()
    return render_template("glosas/search.jinja2", form=form_search, distritos=distritos, autoridades=autoridades)


def new_success(glosa):
    """Mensaje de éxito en nueva glosa"""
    bitacora = Bitacora(
        modulo=MODULO,
        usuario=current_user,
        descripcion=safe_message(f"Nueva glosa con fecha {glosa.fecha}, tipo {glosa.tipo_juicio} y expediente {glosa.expediente}"),
        url=url_for("glosas.detail", glosa_id=glosa.id),
    )
    bitacora.save()
    return bitacora


@glosas.route("/glosas/nuevo", methods=["GET", "POST"])
@permission_required(Permiso.CREAR_SEGUNDAS)
def new():
    """Subir Glosa como juzgado"""

    # Para validar la fecha
    hoy = datetime.date.today()
    hoy_dt = datetime.datetime(year=hoy.year, month=hoy.month, day=hoy.day)
    limite_dt = hoy_dt + datetime.timedelta(days=-LIMITE_DIAS)

    # Validar autoridad
    autoridad = current_user.autoridad
    if autoridad is None or autoridad.estatus != "A":
        flash("El juzgado/autoridad no existe o no es activa.", "warning")
        return redirect(url_for("glosas.list_active"))
    if not autoridad.distrito.es_distrito_judicial:
        flash("El juzgado/autoridad no está en un distrito jurisdiccional.", "warning")
        return redirect(url_for("glosas.list_active"))
    if not autoridad.es_jurisdiccional:
        flash("El juzgado/autoridad no es jurisdiccional.", "warning")
        return redirect(url_for("glosas.list_active"))
    if autoridad.directorio_glosas is None or autoridad.directorio_glosas == "":
        flash("El juzgado/autoridad no tiene directorio para glosas.", "warning")
        return redirect(url_for("glosas.list_active"))

    # Si viene el formulario
    form = GlosaNewForm(CombinedMultiDict((request.files, request.form)))
    if form.validate_on_submit():

        # Validar fecha
        fecha = form.fecha.data
        if not limite_dt <= datetime.datetime(year=fecha.year, month=fecha.month, day=fecha.day) <= hoy_dt:
            flash(f"La fecha no debe ser del futuro ni anterior a {LIMITE_DIAS} días.", "warning")
            form.fecha.data = hoy
            return render_template("glosas/new.jinja2", form=form)

        # Tomar tipo de juicio
        tipo_juicio = form.tipo_juicio.data

        # Validar descripcion
        descripcion = safe_string(form.descripcion.data)
        if descripcion == "":
            flash("La descripción es incorrecta.", "warning")
            return render_template("glosas/new.jinja2", form=form)

        # Validar expediente
        try:
            expediente = safe_expediente(form.expediente.data)
        except (IndexError, ValueError):
            flash("El expediente es incorrecto.", "warning")
            return render_template("glosas/new.jinja2", form=form)

        # Validar archivo
        archivo = request.files["archivo"]
        archivo_nombre = secure_filename(archivo.filename.lower())
        if "." not in archivo_nombre or archivo_nombre.rsplit(".", 1)[1] != "pdf":
            flash("No es un archivo PDF.", "warning")
            return render_template("glosas/new.jinja2", form=form)

        # Insertar registro
        glosa = Glosa(
            autoridad=autoridad,
            fecha=fecha,
            tipo_juicio=tipo_juicio,
            descripcion=descripcion,
            expediente=expediente,
        )
        glosa.save()

        # Elaborar nombre del archivo
        ano_str = fecha.strftime("%Y")
        mes_str = mes_en_palabra(fecha.month)
        fecha_str = fecha.strftime("%Y-%m-%d")
        expediente_str = expediente.replace("/", "-")
        descripcion_str = descripcion.replace(" ", "-")
        archivo_str = f"{fecha_str}-{expediente_str}-{descripcion_str}-{glosa.encode_id()}.pdf"
        ruta_str = str(Path(SUBDIRECTORIO, autoridad.directorio_glosas, ano_str, mes_str, archivo_str))

        # Subir el archivo
        deposito = current_app.config["CLOUD_STORAGE_DEPOSITO"]
        storage_client = storage.Client()
        bucket = storage_client.bucket(deposito)
        blob = bucket.blob(ruta_str)
        blob.upload_from_string(archivo.stream.read(), content_type="application/pdf")
        url = blob.public_url

        # Actualizar el nombre del archivo y el url
        glosa.archivo = archivo_str
        glosa.url = url
        glosa.save()

        # Mostrar mensaje de éxito e ir al detalle
        bitacora = new_success(glosa)
        flash(bitacora.descripcion, "success")
        return redirect(bitacora.url)

    # Prellenado de los campos
    form.distrito.data = autoridad.distrito.nombre
    form.autoridad.data = autoridad.descripcion
    form.fecha.data = hoy
    return render_template("glosas/new.jinja2", form=form)


@glosas.route("/glosas/nuevo/<int:autoridad_id>", methods=["GET", "POST"])
@permission_required(Permiso.ADMINISTRAR_SEGUNDAS)
def new_for_autoridad(autoridad_id):
    """Subir Glosa para una autoridad dada"""

    # Para validar la fecha
    hoy = datetime.date.today()
    hoy_dt = datetime.datetime(year=hoy.year, month=hoy.month, day=hoy.day)
    limite_dt = hoy_dt + datetime.timedelta(days=-LIMITE_ADMINISTRADORES_DIAS)

    # Validar autoridad
    autoridad = Autoridad.query.get_or_404(autoridad_id)
    if autoridad is None:
        flash("El juzgado/autoridad no existe.", "warning")
        return redirect(url_for("glosas.list_active"))
    if autoridad.estatus != "A":
        flash("El juzgado/autoridad no existe o no es activa.", "warning")
        return redirect(url_for("autoridades.detail", autoridad_id=autoridad.id))
    if not autoridad.distrito.es_distrito_judicial:
        flash("El juzgado/autoridad no está en un distrito jurisdiccional.", "warning")
        return redirect(url_for("autoridades.detail", autoridad_id=autoridad.id))
    if not autoridad.es_jurisdiccional:
        flash("El juzgado/autoridad no es jurisdiccional.", "warning")
        return redirect(url_for("autoridades.detail", autoridad_id=autoridad.id))
    if autoridad.directorio_glosas is None or autoridad.directorio_glosas == "":
        flash("El juzgado/autoridad no tiene directorio para glosas.", "warning")
        return redirect(url_for("autoridades.detail", autoridad_id=autoridad.id))

    # Si viene el formulario
    form = GlosaNewForm(CombinedMultiDict((request.files, request.form)))
    if form.validate_on_submit():

        # Validar fecha
        fecha = form.fecha.data
        if not limite_dt <= datetime.datetime(year=fecha.year, month=fecha.month, day=fecha.day) <= hoy_dt:
            flash(f"La fecha no debe ser del futuro ni anterior a {LIMITE_ADMINISTRADORES_DIAS} días.", "warning")
            form.fecha.data = hoy
            return render_template("glosas/new_for_autoridad.jinja2", form=form, autoridad=autoridad)

        # Tomar tipo de juicio
        tipo_juicio = form.tipo_juicio.data

        # Validar descripcion, porque safe_string puede resultar vacío
        descripcion = safe_string(form.descripcion.data)
        if descripcion == "":
            flash("La descripción es incorrecta.", "warning")
            return render_template("glosas/new_for_autoridad.jinja2", form=form, autoridad=autoridad)

        # Validar expediente
        try:
            expediente = safe_expediente(form.expediente.data)
        except (IndexError, ValueError):
            flash("El expediente es incorrecto.", "warning")
            return render_template("glosas/new_for_autoridad.jinja2", form=form, autoridad=autoridad)

        # Validar archivo
        archivo = request.files["archivo"]
        archivo_nombre = secure_filename(archivo.filename.lower())
        if "." not in archivo_nombre or archivo_nombre.rsplit(".", 1)[1] != "pdf":
            flash("No es un archivo PDF.", "warning")
            return render_template("glosas/new_for_autoridad.jinja2", form=form, autoridad=autoridad)

        # Insertar registro
        glosa = Glosa(
            autoridad=autoridad,
            fecha=fecha,
            tipo_juicio=tipo_juicio,
            descripcion=descripcion,
            expediente=form.expediente.data,
        )
        glosa.save()

        # Elaborar nombre del archivo
        ano_str = fecha.strftime("%Y")
        mes_str = mes_en_palabra(fecha.month)
        fecha_str = fecha.strftime("%Y-%m-%d")
        expediente_str = expediente.replace("/", "-")
        descripcion_str = descripcion.replace(" ", "-")
        archivo_str = f"{fecha_str}-{expediente_str}-{descripcion_str}-{glosa.encode_id()}.pdf"
        ruta_str = str(Path(SUBDIRECTORIO, autoridad.directorio_glosas, ano_str, mes_str, archivo_str))

        # Subir el archivo
        deposito = current_app.config["CLOUD_STORAGE_DEPOSITO"]
        storage_client = storage.Client()
        bucket = storage_client.bucket(deposito)
        blob = bucket.blob(ruta_str)
        blob.upload_from_string(archivo.stream.read(), content_type="application/pdf")
        url = blob.public_url

        # Actualizar el nombre del archivo y el url
        glosa.archivo = archivo_str
        glosa.url = url
        glosa.save()

        # Mostrar mensaje de éxito e ir al detalle
        bitacora = new_success(glosa)
        flash(bitacora.descripcion, "success")
        return redirect(bitacora.url)

    # Prellenado de los campos
    form.distrito.data = autoridad.distrito.nombre
    form.autoridad.data = autoridad.descripcion
    form.fecha.data = hoy
    return render_template("glosas/new_for_autoridad.jinja2", form=form, autoridad=autoridad)


def edit_success(glosa):
    """Mensaje de éxito al editar una glosa"""
    bitacora = Bitacora(
        modulo=MODULO,
        usuario=current_user,
        descripcion=safe_message(f"Editada glosa con fecha {glosa.fecha}, tipo {glosa.tipo_juicio} y expediente {glosa.expediente}"),
        url=url_for("glosas.detail", glosa_id=glosa.id),
    )
    bitacora.save()
    return bitacora


@glosas.route("/glosas/edicion/<int:glosa_id>", methods=["GET", "POST"])
@permission_required(Permiso.MODIFICAR_SEGUNDAS)
def edit(glosa_id):
    """Editar Glosa"""

    # Validar glosa
    glosa = Glosa.query.get_or_404(glosa_id)
    if not (current_user.can_admin("glosas") or current_user.autoridad_id == glosa.autoridad_id):
        flash("No tiene permiso para editar esta glosa.", "warning")
        return redirect(url_for("glosas.list_active"))

    form = GlosaEditForm()
    if form.validate_on_submit():
        es_valido = True
        glosa.fecha = form.fecha.data
        glosa.tipo_juicio = form.tipo_juicio.data
        glosa.descripcion = safe_string(form.descripcion.data)
        try:
            glosa.expediente = safe_expediente(form.expediente.data)
        except (IndexError, ValueError):
            flash("El expediente es incorrecto.", "warning")
            es_valido = False
        if es_valido:
            glosa.save()
            bitacora = edit_success(glosa)
            flash(bitacora.descripcion, "success")
            return redirect(bitacora.url)
    form.fecha.data = glosa.fecha
    form.tipo_juicio.data = glosa.tipo_juicio
    form.descripcion.data = glosa.descripcion
    form.expediente.data = glosa.expediente
    return render_template("glosas/edit.jinja2", form=form, glosa=glosa)


def delete_success(glosa):
    """Mensaje de éxito al eliminar una glosa"""
    bitacora = Bitacora(
        modulo=MODULO,
        usuario=current_user,
        descripcion=safe_message(f"Eliminada glosa con fecha {glosa.fecha}, tipo {glosa.tipo_juicio} y expediente {glosa.expediente}"),
        url=url_for("glosas.detail", glosa_id=glosa.id),
    )
    bitacora.save()
    return bitacora


@glosas.route("/glosas/eliminar/<int:glosa_id>")
@permission_required(Permiso.MODIFICAR_SEGUNDAS)
def delete(glosa_id):
    """Eliminar Glosa"""
    glosa = Glosa.query.get_or_404(glosa_id)
    if glosa.estatus == "A":
        hoy = datetime.date.today()
        hoy_dt = datetime.datetime(year=hoy.year, month=hoy.month, day=hoy.day)
        if current_user.can_admin("glosas"):
            if hoy_dt + datetime.timedelta(days=-LIMITE_ADMINISTRADORES_DIAS) <= glosa.creado:
                glosa.delete()
                bitacora = delete_success(glosa)
                flash(bitacora.descripcion, "success")
            else:
                flash(f"No tiene permiso para eliminar si fue creado hace {LIMITE_ADMINISTRADORES_DIAS} días o más.", "warning")
        elif current_user.autoridad_id == glosa.autoridad_id:
            if hoy_dt + datetime.timedelta(days=-LIMITE_DIAS) <= glosa.creado:
                glosa.delete()
                bitacora = delete_success(glosa)
                flash(bitacora.descripcion, "success")
            else:
                flash(f"No tiene permiso para eliminar si fue creado hace {LIMITE_DIAS} días o más.", "warning")
        else:
            flash("No tiene permiso para eliminar.", "warning")
    return redirect(url_for("glosas.detail", glosa_id=glosa.id))


def recover_success(glosa):
    """Mensaje de éxito al recuperar una glosa"""
    bitacora = Bitacora(
        modulo=MODULO,
        usuario=current_user,
        descripcion=safe_message(f"Recuperada glosa con fecha {glosa.fecha}, tipo {glosa.tipo_juicio} y expediente {glosa.expediente}"),
        url=url_for("glosas.detail", glosa_id=glosa.id),
    )
    bitacora.save()
    return bitacora


@glosas.route("/glosas/recuperar/<int:glosa_id>")
@permission_required(Permiso.MODIFICAR_SEGUNDAS)
def recover(glosa_id):
    """Recuperar Glosa"""
    glosa = Glosa.query.get_or_404(glosa_id)
    if glosa.estatus == "B":
        hoy = datetime.date.today()
        hoy_dt = datetime.datetime(year=hoy.year, month=hoy.month, day=hoy.day)
        if current_user.can_admin("glosas"):
            if hoy_dt + datetime.timedelta(days=-LIMITE_ADMINISTRADORES_DIAS) <= glosa.creado:
                glosa.recover()
                bitacora = recover_success(glosa)
                flash(bitacora.descripcion, "success")
            else:
                flash(f"No tiene permiso para recuperar si fue creado hace {LIMITE_ADMINISTRADORES_DIAS} días o más.", "warning")
        elif current_user.autoridad_id == glosa.autoridad_id:
            if hoy_dt + datetime.timedelta(days=-LIMITE_DIAS) <= glosa.creado:
                glosa.recover()
                bitacora = recover_success(glosa)
                flash(bitacora.descripcion, "success")
            else:
                flash(f"No tiene permiso para recuperar si fue creado hace {LIMITE_DIAS} días o más.", "warning")
        else:
            flash("No tiene permiso para recuperar.", "warning")
    return redirect(url_for("glosas.detail", glosa_id=glosa.id))

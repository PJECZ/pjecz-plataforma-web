"""
Glosas, vistas
"""
from datetime import date, timedelta
from pathlib import Path
from unidecode import unidecode

from flask import Blueprint, current_app, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required
from google.cloud import storage
from werkzeug.datastructures import CombinedMultiDict
from werkzeug.utils import secure_filename
from lib.time_to_text import dia_mes_ano, mes_en_palabra

from plataforma_web.blueprints.roles.models import Permiso
from plataforma_web.blueprints.usuarios.decorators import permission_required

from plataforma_web.blueprints.glosas.forms import GlosaEditForm, GlosaNewForm, GlosaSearchForm
from plataforma_web.blueprints.glosas.models import Glosa, GlosaException

from plataforma_web.blueprints.autoridades.models import Autoridad, AutoridadException
from plataforma_web.blueprints.distritos.models import Distrito

glosas = Blueprint("glosas", __name__, template_folder="templates")

SUBDIRECTORIO = "Glosas"
DIAS_LIMITE = 5


@glosas.route("/glosas/acuses/<id_hashed>")
def checkout(id_hashed):
    """Acuse"""
    glosa = Glosa.query.get_or_404(Glosa.decode_id(id_hashed))
    dia, mes, ano = dia_mes_ano(glosa.creado)
    return render_template("glosas/checkout.jinja2", glosa=glosa, dia=dia, mes=mes.upper(), ano=ano)


@glosas.before_request
@login_required
@permission_required(Permiso.VER_JUSTICIABLES)
def before_request():
    """Permiso por defecto"""


@glosas.route("/glosas")
def list_active():
    """Listado de Glosas activos"""
    # Si es administrador, ve las glosas de todas las autoridades
    if current_user.can_admin("glosas"):
        todas = Glosa.query.filter(Glosa.estatus == "A").order_by(Glosa.fecha.desc()).limit(100).all()
        return render_template("glosas/list_admin.jinja2", autoridad=None, glosas=todas, estatus="A")
    # No es administrador, consultar su autoridad
    autoridad = Autoridad.query.get_or_404(current_user.autoridad_id)
    # Si su autoridad es jurisdiccional, ve sus propias glosas
    if current_user.autoridad.es_jurisdiccional:
        sus_listas = Glosa.query.filter(Glosa.autoridad == autoridad).filter(Glosa.estatus == "A").order_by(Glosa.fecha.desc()).limit(100).all()
        return render_template("glosas/list.jinja2", autoridad=autoridad, glosas=sus_listas, estatus="A")
    # No es jurisdiccional, se redirige al listado de distritos
    return redirect(url_for("glosas.list_distritos"))


@glosas.route("/glosas/distritos")
def list_distritos():
    """Listado de Distritos"""
    distritos = Distrito.query.filter(Distrito.es_distrito_judicial == True).filter(Distrito.estatus == "A").order_by(Distrito.nombre).all()
    return render_template("glosas/list_distritos.jinja2", distritos=distritos, estatus="A")


@glosas.route("/glosas/distrito/<int:distrito_id>")
def list_autoridades(distrito_id):
    """Listado de Autoridades de un distrito"""
    distrito = Distrito.query.get_or_404(distrito_id)
    autoridades = Autoridad.query.filter(Autoridad.distrito == distrito).filter(Autoridad.es_jurisdiccional == True).filter(Autoridad.estatus == "A").order_by(Autoridad.clave).all()
    return render_template("glosas/list_autoridades.jinja2", distrito=distrito, autoridades=autoridades, estatus="A")


@glosas.route("/glosas/autoridad/<int:autoridad_id>")
def list_autoridad_glosas(autoridad_id):
    """Listado de Glosas activas de una autoridad"""
    autoridad = Autoridad.query.get_or_404(autoridad_id)
    glosas_activas = Glosa.query.filter(Glosa.autoridad == autoridad).filter(Glosa.estatus == "A").order_by(Glosa.fecha.desc()).limit(100).all()
    return render_template("glosas/list.jinja2", autoridad=autoridad, glosas=glosas_activas, estatus="A")


@glosas.route("/glosas/inactivos/autoridad/<int:autoridad_id>")
@permission_required(Permiso.ADMINISTRAR_JUSTICIABLES)
def list_autoridad_glosas_inactive(autoridad_id):
    """Listado de Glosas inactivas de una autoridad"""
    autoridad = Autoridad.query.get_or_404(autoridad_id)
    glosas_inactivas = Glosa.query.filter(Glosa.autoridad == autoridad).filter(Glosa.estatus == "B").order_by(Glosa.creado.desc()).limit(100).all()
    return render_template("glosas/list.jinja2", autoridad=autoridad, glosas=glosas_inactivas, estatus="B")


@glosas.route("/glosas/refrescar/<int:autoridad_id>")
@permission_required(Permiso.ADMINISTRAR_JUSTICIABLES)
@permission_required(Permiso.CREAR_ADMINISTRATIVOS)
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


@glosas.route("/glosas/<int:lista_de_acuerdo_id>")
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
        # tipo_juicio
        # expediente
        # descripcion
        consulta = consulta.order_by(Glosa.creado.desc()).limit(100).all()
        return render_template("glosas/list.jinja2", glosas=consulta)
    distritos = Distrito.query.filter(Distrito.es_distrito_judicial == True).filter(Distrito.estatus == "A").order_by(Distrito.nombre).all()
    autoridades = Autoridad.query.filter(Autoridad.es_jurisdiccional == True).filter(Autoridad.estatus == "A").order_by(Autoridad.clave).all()
    return render_template("glosas/search.jinja2", form=form_search, distritos=distritos, autoridades=autoridades)


@glosas.route("/glosas/nuevo", methods=["GET", "POST"])
@permission_required(Permiso.CREAR_JUSTICIABLES)
def new():
    """Subir Glosa como juzgado"""
    hoy = date.today()

    # Validar autoridad
    autoridad = current_user.autoridad
    try:
        if autoridad is None or autoridad.estatus != "A":
            raise AutoridadException("El juzgado/autoridad no existe o no es activa.")
        if not autoridad.distrito.es_distrito_judicial:
            raise AutoridadException("El juzgado/autoridad no está en un distrito jurisdiccional.")
        if not autoridad.es_jurisdiccional:
            raise AutoridadException("El juzgado/autoridad no es jurisdiccional.")
        if autoridad.directorio_glosas is None or autoridad.directorio_glosas == "":
            raise AutoridadException("El juzgado/autoridad no tiene directorio para glosas.")
    except AutoridadException as error:
        return redirect(url_for("sistemas.bad_request", error=str(error)))

    # Si viene el formulario
    form = GlosaNewForm(CombinedMultiDict((request.files, request.form)))
    if form.validate_on_submit():

        # Tomar valores del formulario
        fecha = form.fecha.data
        tipo_juicio = form.tipo_juicio.data
        descripcion = unidecode(form.descripcion.data.strip())
        expediente = form.expediente.data
        archivo = request.files["archivo"]

        # Validar fecha y archivo
        archivo_nombre = secure_filename(archivo.filename.lower())
        try:
            if fecha > hoy:
                raise GlosaException("La fecha no debe ser del futuro.")
            if fecha < hoy - timedelta(days=DIAS_LIMITE):
                raise GlosaException(f"La fecha no debe ser más antigua a {DIAS_LIMITE} días.")
            if "." not in archivo_nombre or archivo_nombre.rsplit(".", 1)[1] != "pdf":
                raise GlosaException("No es un archivo PDF.")
        except GlosaException as error:
            flash(str(error), "error")
            form.fecha.data = hoy
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

        # Elaborar nombre del archivo y ruta SUBDIRECTORIO/Autoridad/YYYY/MES/archivo.pdf
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

        # Mostrar mensaje de éxito y detalle
        flash(f"Glosa {glosa.descripcion} guardada.", "success")
        return redirect(url_for("glosas.detail", glosa_id=glosa.id))

    # Prellenado de los campos
    form.distrito.data = autoridad.distrito.nombre
    form.autoridad.data = autoridad.descripcion
    form.fecha.data = hoy
    return render_template("glosas/new.jinja2", form=form)


@glosas.route("/glosas/nuevo/<int:autoridad_id>", methods=["GET", "POST"])
@permission_required(Permiso.CREAR_JUSTICIABLES)
@permission_required(Permiso.ADMINISTRAR_JUSTICIABLES)
def new_for_autoridad(autoridad_id):
    """Subir Glosa para una autoridad dada"""
    hoy = date.today()

    # Validar autoridad
    autoridad = Autoridad.query.get_or_404(autoridad_id)
    try:
        if autoridad is None or autoridad.estatus != "A":
            raise AutoridadException("El juzgado/autoridad no existe o no es activa.")
        if not autoridad.distrito.es_distrito_judicial:
            raise AutoridadException("El juzgado/autoridad no está en un distrito jurisdiccional.")
        if not autoridad.es_jurisdiccional:
            raise AutoridadException("El juzgado/autoridad no es jurisdiccional.")
        if autoridad.directorio_glosas is None or autoridad.directorio_glosas == "":
            raise AutoridadException("El juzgado/autoridad no tiene directorio para glosas.")
    except AutoridadException as error:
        return redirect(url_for("sistemas.bad_request", error=str(error)))

    # Si viene el formulario
    form = GlosaNewForm(CombinedMultiDict((request.files, request.form)))
    if form.validate_on_submit():

        # Tomar valores del formulario
        fecha = form.fecha.data
        tipo_juicio = form.tipo_juicio.data
        descripcion = unidecode(form.descripcion.data.strip())
        expediente = form.expediente.data
        archivo = request.files["archivo"]

        # Validar fecha y archivo
        archivo_nombre = secure_filename(archivo.filename.lower())
        try:
            if fecha > hoy:
                raise GlosaException("La fecha no debe ser del futuro.")
            if "." not in archivo_nombre or archivo_nombre.rsplit(".", 1)[1] != "pdf":
                raise GlosaException("No es un archivo PDF.")
        except GlosaException as error:
            flash(str(error), "error")
            form.fecha.data = hoy
            return render_template("glosas/new_for_autoridad.jinja2", form=form, autoridad=autoridad)

        # Insertar registro
        glosa = Glosa(
            autoridad=autoridad,
            fecha=fecha,
            tipo_juicio=tipo_juicio,
            descripcion=unidecode(form.descripcion.data.strip()),
            expediente=form.expediente.data,
        )
        glosa.save()

        # Elaborar nombre del archivo y ruta SUBDIRECTORIO/Autoridad/YYYY/MES/archivo.pdf
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

        # Mostrar mensaje de éxito y detalle
        flash(f"Glosa {glosa.descripcion} guardada.", "success")
        return redirect(url_for("glosas.detail", glosa_id=glosa.id))

    # Prellenado de los campos
    form.distrito.data = autoridad.distrito.nombre
    form.autoridad.data = autoridad.descripcion
    form.fecha.data = hoy
    return render_template("glosas/new_for_autoridad.jinja2", form=form, autoridad=autoridad)


@glosas.route("/glosas/edicion/<int:glosa_id>", methods=["GET", "POST"])
@permission_required(Permiso.ADMINISTRAR_JUSTICIABLES)
def edit(glosa_id):
    """Editar Glosa"""
    glosa = Glosa.query.get_or_404(glosa_id)
    form = GlosaEditForm()
    if form.validate_on_submit():
        glosa.fecha = form.fecha.data
        glosa.tipo_juicio = form.tipo_juicio.data
        glosa.descripcion = form.descripcion.data
        glosa.expediente = form.expediente.data
        glosa.save()
        flash(f"Glosa {glosa.descripcion} guardada.", "success")
        return redirect(url_for("glosas.detail", glosa_id=glosa.id))
    form.fecha.data = glosa.fecha
    form.tipo_juicio.data = glosa.tipo_juicio
    form.descripcion.data = glosa.descripcion
    form.expediente.data = glosa.expediente
    return render_template("glosas/edit.jinja2", form=form, glosa=glosa)


@glosas.route("/glosas/eliminar/<int:glosa_id>")
@permission_required(Permiso.MODIFICAR_JUSTICIABLES)
def delete(glosa_id):
    """Eliminar Glosa"""
    glosa = Glosa.query.get_or_404(glosa_id)
    if glosa.estatus == "A":
        if current_user.can_admin("glosas") or (current_user.autoridad_id == glosa.autoridad_id):
            glosa.delete()
            flash(f"Glosa {glosa.descripcion} eliminada.", "success")
        else:
            flash("No tiene permiso para eliminar.", "warning")
    return redirect(url_for("glosas.detail", glosa_id=glosa.id))


@glosas.route("/glosas/recuperar/<int:glosa_id>")
@permission_required(Permiso.MODIFICAR_JUSTICIABLES)
def recover(glosa_id):
    """Recuperar Glosa"""
    glosa = Glosa.query.get_or_404(glosa_id)
    if glosa.estatus == "B":
        if current_user.can_admin("glosas") or (current_user.autoridad_id == glosa.autoridad_id):
            glosa.recover()
            flash(f"Glosa {glosa.descripcion} recuperado.", "success")
        else:
            flash("No tiene permiso para recuperar.", "warning")
    return redirect(url_for("glosas.detail", glosa_id=glosa.id))

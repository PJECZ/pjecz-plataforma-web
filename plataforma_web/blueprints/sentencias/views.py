"""
Sentencias, vistas
"""
import datetime
from pathlib import Path

from flask import Blueprint, current_app, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required
from google.cloud import storage
from werkzeug.datastructures import CombinedMultiDict
from werkzeug.utils import secure_filename
from lib.safe_string import safe_expediente, safe_sentencia
from lib.time_to_text import dia_mes_ano, mes_en_palabra

from plataforma_web.blueprints.roles.models import Permiso
from plataforma_web.blueprints.usuarios.decorators import permission_required

from plataforma_web.blueprints.sentencias.forms import SentenciaNewForm, SentenciaEditForm, SentenciaSearchForm
from plataforma_web.blueprints.sentencias.models import Sentencia

from plataforma_web.blueprints.autoridades.models import Autoridad
from plataforma_web.blueprints.distritos.models import Distrito

sentencias = Blueprint("sentencias", __name__, template_folder="templates")

SUBDIRECTORIO = "Sentencias"
LIMITE_JUSTICIABLES_DIAS = 365
LIMITE_ADMINISTRADORES_DIAS = 365


@sentencias.route("/sentencias/acuses/<id_hashed>")
def checkout(id_hashed):
    """Acuse"""
    sentencia = Sentencia.query.get_or_404(Sentencia.decode_id(id_hashed))
    dia, mes, ano = dia_mes_ano(sentencia.creado)
    return render_template("sentencias/checkout.jinja2", sentencia=sentencia, dia=dia, mes=mes.upper(), ano=ano)


@sentencias.before_request
@login_required
@permission_required(Permiso.VER_JUSTICIABLES)
def before_request():
    """Permiso por defecto"""


@sentencias.route("/sentencias")
def list_active():
    """Listado de Sentencias activas más recientes"""
    # Si es administrador, ve las sentencias de todas las autoridades
    if current_user.can_admin("sentencias"):
        sentencias_activas = Sentencia.query.filter(Sentencia.estatus == "A").order_by(Sentencia.fecha.desc()).limit(100).all()
        return render_template("sentencias/list_admin.jinja2", autoridad=None, sentencias=sentencias_activas, estatus="A")
    # Si su autoridad es jurisdiccional, ve sus propias sentencias
    if current_user.autoridad.es_jurisdiccional:
        sus_sentencias_activas = Sentencia.query.filter(Sentencia.autoridad == current_user.autoridad).filter(Sentencia.estatus == "A").order_by(Sentencia.fecha.desc()).limit(100).all()
        return render_template("sentencias/list.jinja2", autoridad=current_user.autoridad, sentencias=sus_sentencias_activas, estatus="A")
    # No es jurisdiccional, se redirige al listado de distritos
    return redirect(url_for("sentencias.list_distritos"))


@sentencias.route("/sentencias/inactivos")
@permission_required(Permiso.MODIFICAR_JUSTICIABLES)
def list_inactive():
    """Listado de Sentencias inactivas"""
    # Si es administrador, ve las sentencias de todas las autoridades
    if current_user.can_admin("sentencias"):
        sentencias_inactivas = Sentencia.query.filter(Sentencia.estatus == "B").order_by(Sentencia.creado.desc()).limit(100).all()
        return render_template("sentencias/list_admin.jinja2", autoridad=None, sentencias=sentencias_inactivas, estatus="B")
    # Si es jurisdiccional, ve sus propias sentencias
    if current_user.autoridad.es_jurisdiccional:
        sus_sentencias_inactivas = Sentencia.query.filter(Sentencia.autoridad == current_user.autoridad).filter(Sentencia.estatus == "B").order_by(Sentencia.fecha.desc()).limit(100).all()
        return render_template("sentencias/list.jinja2", autoridad=current_user.autoridad, sentencias=sus_sentencias_inactivas, estatus="B")
    # No es jurisdiccional, se redirige al listado de distritos
    return redirect(url_for("sentencias.list_distritos"))


@sentencias.route("/sentencias/distritos")
def list_distritos():
    """Listado de Distritos"""
    distritos = Distrito.query.filter(Distrito.es_distrito_judicial == True).filter(Distrito.estatus == "A").order_by(Distrito.nombre).all()
    return render_template("sentencias/list_distritos.jinja2", distritos=distritos, estatus="A")


@sentencias.route("/sentencias/distrito/<int:distrito_id>")
def list_autoridades(distrito_id):
    """Listado de Autoridades de un distrito"""
    distrito = Distrito.query.get_or_404(distrito_id)
    autoridades = Autoridad.query.filter(Autoridad.distrito == distrito).filter(Autoridad.es_jurisdiccional == True).filter(Autoridad.es_notaria == False).filter(Autoridad.estatus == "A").order_by(Autoridad.clave).all()
    return render_template("sentencias/list_autoridades.jinja2", distrito=distrito, autoridades=autoridades, estatus="A")


@sentencias.route("/sentencias/autoridad/<int:autoridad_id>")
def list_autoridad_sentencias(autoridad_id):
    """Listado de Sentencias activas de una autoridad"""
    autoridad = Autoridad.query.get_or_404(autoridad_id)
    sentencias_activas = Sentencia.query.filter(Sentencia.autoridad == autoridad).filter(Sentencia.estatus == "A").order_by(Sentencia.fecha.desc()).limit(100).all()
    return render_template("sentencias/list.jinja2", autoridad=autoridad, sentencias=sentencias_activas, estatus="A")


@sentencias.route("/sentencias/inactivos/autoridad/<int:autoridad_id>")
@permission_required(Permiso.ADMINISTRAR_JUSTICIABLES)
def list_autoridad_sentencias_inactive(autoridad_id):
    """Listado de Sentencias inactivas de una autoridad"""
    autoridad = Autoridad.query.get_or_404(autoridad_id)
    sentencias_inactivos = Sentencia.query.filter(Sentencia.autoridad == autoridad).filter(Sentencia.estatus == "B").order_by(Sentencia.creado.desc()).limit(100).all()
    return render_template("sentencias/list.jinja2", autoridad=autoridad, sentencias=sentencias_inactivos, estatus="B")


@sentencias.route("/sentencias/refrescar/<int:autoridad_id>")
@permission_required(Permiso.ADMINISTRAR_JUSTICIABLES)
def refresh(autoridad_id):
    """Refrescar Listas de Acuerdos"""
    autoridad = Autoridad.query.get_or_404(autoridad_id)
    if current_user.get_task_in_progress("sentencias.tasks.refrescar"):
        flash("Debe esperar porque hay una tarea en el fondo sin terminar.", "warning")
    else:
        tarea = current_user.launch_task(
            nombre="sentencias.tasks.refrescar",
            descripcion=f"Refrescar sentencias de {autoridad.clave}",
            usuario_id=current_user.id,
            autoridad_id=autoridad.id,
        )
        flash(f"{tarea.descripcion} está corriendo en el fondo.", "info")
    return redirect(url_for("sentencias.list_autoridad_sentencias", autoridad_id=autoridad.id))


@sentencias.route("/sentencias/<int:sentencia_id>")
def detail(sentencia_id):
    """Detalle de un Sentencia"""
    sentencia = Sentencia.query.get_or_404(sentencia_id)
    return render_template("sentencias/detail.jinja2", sentencia=sentencia)


@sentencias.route("/sentencias/buscar", methods=["GET", "POST"])
def search():
    """Buscar Sentencias"""
    form_search = SentenciaSearchForm()
    if form_search.validate_on_submit():
        mostrar_resultados = True
        autoridad = Autoridad.query.get(form_search.autoridad.data)
        consulta = Sentencia.query.filter(Sentencia.autoridad == autoridad)
        if form_search.fecha_desde.data:
            consulta = consulta.filter(Sentencia.fecha >= form_search.fecha_desde.data)
        if form_search.fecha_hasta.data:
            consulta = consulta.filter(Sentencia.fecha <= form_search.fecha_hasta.data)
        try:
            sentencia = safe_sentencia(form_search.sentencia.data)
            if sentencia != "":
                consulta = consulta.filter(Sentencia.sentencia == sentencia)
        except (IndexError, ValueError):
            flash("La sentencia es incorrecta.", "warning")
            mostrar_resultados = False
        try:
            expediente = safe_expediente(form_search.expediente.data)
            if expediente != "":
                consulta = consulta.filter(Sentencia.expediente == expediente)
        except (IndexError, ValueError):
            flash("El expediente es incorrecto.", "warning")
            mostrar_resultados = False
        if mostrar_resultados:
            consulta = consulta.order_by(Sentencia.fecha.desc()).limit(100).all()
            return render_template("sentencias/list.jinja2", autoridad=autoridad, sentencias=consulta)
    distritos = Distrito.query.filter(Distrito.es_distrito_judicial == True).filter(Distrito.estatus == "A").order_by(Distrito.nombre).all()
    autoridades = Autoridad.query.filter(Autoridad.es_jurisdiccional == True).filter(Autoridad.es_notaria == False).filter(Autoridad.estatus == "A").order_by(Autoridad.clave).all()
    return render_template("sentencias/search.jinja2", form=form_search, distritos=distritos, autoridades=autoridades)


@sentencias.route("/sentencias/nuevo", methods=["GET", "POST"])
@permission_required(Permiso.CREAR_JUSTICIABLES)
def new():
    """Nuevo Sentencia como juzgado"""

    # Para validar la fecha
    dias_limite = 365
    hoy = datetime.date.today()
    hoy_dt = datetime.datetime(year=hoy.year, month=hoy.month, day=hoy.day)
    limite_dt = hoy_dt + datetime.timedelta(days=-dias_limite)

    # Validar autoridad
    autoridad = current_user.autoridad
    if autoridad is None or autoridad.estatus != "A":
        flash("El juzgado/autoridad no existe o no es activa.", "warning")
        return redirect(url_for("sentencias.list_active"))
    if not autoridad.distrito.es_distrito_judicial:
        flash("El juzgado/autoridad no está en un distrito jurisdiccional.", "warning")
        return redirect(url_for("sentencias.list_active"))
    if not autoridad.es_jurisdiccional:
        flash("El juzgado/autoridad no es jurisdiccional.", "warning")
        return redirect(url_for("sentencias.list_active"))
    if autoridad.directorio_sentencias is None or autoridad.directorio_sentencias == "":
        flash("El juzgado/autoridad no tiene directorio para sentencias.", "warning")
        return redirect(url_for("sentencias.list_active"))

    # Si viene el formulario
    form = SentenciaNewForm(CombinedMultiDict((request.files, request.form)))
    if form.validate_on_submit():

        # Validar fecha
        fecha = form.fecha.data
        if not limite_dt <= datetime.datetime(year=fecha.year, month=fecha.month, day=fecha.day) <= hoy_dt:
            flash(f"La fecha no debe ser del futuro ni anterior a {dias_limite} días.", "warning")
            form.fecha.data = hoy
            return render_template("sentencias/new.jinja2", form=form)

        # Validar sentencia
        try:
            sentencia_input = safe_sentencia(form.sentencia.data)
        except (IndexError, ValueError):
            flash("La sentencia es incorrecta.", "warning")
            return render_template("sentencias/new.jinja2", form=form)

        # Validar expediente
        try:
            expediente = safe_expediente(form.expediente.data)
        except (IndexError, ValueError):
            flash("El expediente es incorrecto.", "warning")
            return render_template("sentencias/new.jinja2", form=form)

        # Tomar perspectiva de género
        es_paridad_genero = form.es_paridad_genero.data  # Boleano

        # Validar archivo
        archivo = request.files["archivo"]
        archivo_nombre = secure_filename(archivo.filename.lower())
        if "." not in archivo_nombre or archivo_nombre.rsplit(".", 1)[1] != "pdf":
            flash("No es un archivo PDF.", "warning")
            return render_template("sentencias/new.jinja2", form=form)

        # Insertar registro
        sentencia = Sentencia(
            autoridad=autoridad,
            fecha=fecha,
            sentencia=sentencia_input,
            expediente=expediente,
            es_paridad_genero=es_paridad_genero,
        )
        sentencia.save()

        # Elaborar nombre del archivo y ruta SUBDIRECTORIO/Autoridad/YYYY/MES/archivo.pdf
        ano_str = fecha.strftime("%Y")
        mes_str = mes_en_palabra(fecha.month)
        fecha_str = fecha.strftime("%Y-%m-%d")
        sentencia_str = sentencia_input.replace("/", "-")
        expediente_str = expediente.replace("/", "-")
        if es_paridad_genero:
            archivo_str = f"{fecha_str}-{sentencia_str}-{expediente_str}-G-{sentencia.encode_id()}.pdf"
        else:
            archivo_str = f"{fecha_str}-{sentencia_str}-{expediente_str}-{sentencia.encode_id()}.pdf"
        ruta_str = str(Path(SUBDIRECTORIO, autoridad.directorio_sentencias, ano_str, mes_str, archivo_str))

        # Subir el archivo
        deposito = current_app.config["CLOUD_STORAGE_DEPOSITO"]
        storage_client = storage.Client()
        bucket = storage_client.bucket(deposito)
        blob = bucket.blob(ruta_str)
        blob.upload_from_string(archivo.stream.read(), content_type="application/pdf")
        url = blob.public_url

        # Actualizar el nombre del archivo y el url
        sentencia.archivo = archivo_str
        sentencia.url = url
        sentencia.save()

        # Mostrar mensaje de éxito y detalle
        flash(f"Sentencia {sentencia.archivo} guardada.", "success")
        return redirect(url_for("sentencias.detail", sentencia_id=sentencia.id))

    # Prellenado de los campos
    form.distrito.data = autoridad.distrito.nombre
    form.autoridad.data = autoridad.descripcion
    form.fecha.data = hoy
    return render_template("sentencias/new.jinja2", form=form)


@sentencias.route("/sentencias/nuevo/<int:autoridad_id>", methods=["GET", "POST"])
@permission_required(Permiso.ADMINISTRAR_JUSTICIABLES)
def new_for_autoridad(autoridad_id):
    """Subir Sentencia para una autoridad dada"""

    # Para validar la fecha
    dias_limite = 365
    hoy = datetime.date.today()
    hoy_dt = datetime.datetime(year=hoy.year, month=hoy.month, day=hoy.day)
    limite_dt = hoy_dt + datetime.timedelta(days=-dias_limite)

    # Validar autoridad
    autoridad = Autoridad.query.get_or_404(autoridad_id)
    if autoridad is None:
        flash("El juzgado/autoridad no existe.", "warning")
        return redirect(url_for("sentencias.list_active"))
    if autoridad.estatus != "A":
        flash("El juzgado/autoridad no es activa.", "warning")
        return redirect(url_for("autoridades.detail", autoridad_id=autoridad.id))
    if not autoridad.distrito.es_distrito_judicial:
        flash("El juzgado/autoridad no está en un distrito jurisdiccional.", "warning")
        return redirect(url_for("autoridades.detail", autoridad_id=autoridad.id))
    if not autoridad.es_jurisdiccional:
        flash("El juzgado/autoridad no es jurisdiccional.", "warning")
        return redirect(url_for("autoridades.detail", autoridad_id=autoridad.id))
    if autoridad.directorio_sentencias is None or autoridad.directorio_sentencias == "":
        flash("El juzgado/autoridad no tiene directorio para edictos.", "warning")
        return redirect(url_for("autoridades.detail", autoridad_id=autoridad.id))

    # Si viene el formulario
    form = SentenciaNewForm(CombinedMultiDict((request.files, request.form)))
    if form.validate_on_submit():

        # Validar fecha
        fecha = form.fecha.data
        if not limite_dt <= datetime.datetime(year=fecha.year, month=fecha.month, day=fecha.day) <= hoy_dt:
            flash(f"La fecha no debe ser del futuro ni anterior a {dias_limite} días.", "warning")
            form.fecha.data = hoy
            return render_template("sentencias/new_for_autoridad.jinja2", form=form, autoridad=autoridad)

        # Validar sentencia
        try:
            sentencia_input = safe_sentencia(form.sentencia.data)
        except (IndexError, ValueError):
            flash("La sentencia es incorrecta.", "warning")
            return render_template("sentencias/new_for_autoridad.jinja2", form=form, autoridad=autoridad)

        # Validar expediente
        try:
            expediente = safe_expediente(form.expediente.data)
        except (IndexError, ValueError):
            flash("El expediente es incorrecto.", "warning")
            return render_template("sentencias/new_for_autoridad.jinja2", form=form, autoridad=autoridad)

        # Tomar perspectiva de género
        es_paridad_genero = form.es_paridad_genero.data  # Boleano

        # Validar archivo
        archivo = request.files["archivo"]
        archivo_nombre = secure_filename(archivo.filename.lower())
        if "." not in archivo_nombre or archivo_nombre.rsplit(".", 1)[1] != "pdf":
            flash("No es un archivo PDF.", "warning")
            return render_template("sentencias/new_for_autoridad.jinja2", form=form, autoridad=autoridad)

        # Insertar registro
        sentencia = Sentencia(
            autoridad=autoridad,
            fecha=fecha,
            sentencia=sentencia_input,
            expediente=expediente,
            es_paridad_genero=es_paridad_genero,
        )
        sentencia.save()

        # Elaborar nombre del archivo y ruta SUBDIRECTORIO/Autoridad/YYYY/MES/archivo.pdf
        ano_str = fecha.strftime("%Y")
        mes_str = mes_en_palabra(fecha.month)
        fecha_str = fecha.strftime("%Y-%m-%d")
        sentencia_str = sentencia_input.replace("/", "-")
        expediente_str = expediente.replace("/", "-")
        if es_paridad_genero:
            archivo_str = f"{fecha_str}-{sentencia_str}-{expediente_str}-{sentencia.encode_id()}.pdf"
        else:
            archivo_str = f"{fecha_str}-{sentencia_str}-{expediente_str}-G-{sentencia.encode_id()}.pdf"
        ruta_str = str(Path(SUBDIRECTORIO, autoridad.directorio_sentencias, ano_str, mes_str, archivo_str))

        # Subir el archivo
        deposito = current_app.config["CLOUD_STORAGE_DEPOSITO"]
        storage_client = storage.Client()
        bucket = storage_client.bucket(deposito)
        blob = bucket.blob(ruta_str)
        blob.upload_from_string(archivo.stream.read(), content_type="application/pdf")
        url = blob.public_url

        # Actualizar el nombre del archivo y el url
        sentencia.archivo = archivo_str
        sentencia.url = url
        sentencia.save()

        # Mostrar mensaje de éxito y detalle
        flash(f"Sentencia {sentencia.archivo} guardada.", "success")
        return redirect(url_for("sentencias.detail", sentencia_id=sentencia.id))

    # Prellenado de los campos
    form.distrito.data = autoridad.distrito.nombre
    form.autoridad.data = autoridad.descripcion
    form.fecha.data = hoy
    return render_template("sentencias/new_for_autoridad.jinja2", form=form, autoridad=autoridad)


@sentencias.route("/sentencias/edicion/<int:sentencia_id>", methods=["GET", "POST"])
@permission_required(Permiso.ADMINISTRAR_JUSTICIABLES)
def edit(sentencia_id):
    """Editar Sentencia"""
    sentencia = Sentencia.query.get_or_404(sentencia_id)
    form = SentenciaEditForm()
    if form.validate_on_submit():
        es_valido = True
        sentencia.fecha = form.fecha.data
        try:
            sentencia.sentencia = safe_sentencia(form.sentencia.data)
        except (IndexError, ValueError):
            flash("La sentencia es incorrecta.", "warning")
            es_valido = False
        try:
            sentencia.expediente = safe_expediente(form.expediente.data)
        except (IndexError, ValueError):
            flash("El expediente es incorrecto.", "warning")
            es_valido = False
        sentencia.es_paridad_genero = form.es_paridad_genero.data
        if es_valido:
            sentencia.save()
            flash(f"Sentencia {sentencia.archivo} guardada.", "success")
            return redirect(url_for("sentencias.detail", sentencia_id=sentencia.id))
    form.fecha.data = sentencia.fecha
    form.sentencia.data = sentencia.sentencia
    form.expediente.data = sentencia.expediente
    form.es_paridad_genero.data = sentencia.es_paridad_genero
    return render_template("sentencias/edit.jinja2", form=form, sentencia=sentencia)


@sentencias.route("/sentencias/eliminar/<int:sentencia_id>")
@permission_required(Permiso.MODIFICAR_JUSTICIABLES)
def delete(sentencia_id):
    """Eliminar Sentencia"""
    sentencia = Sentencia.query.get_or_404(sentencia_id)
    if sentencia.estatus == "A":
        hoy = datetime.date.today()
        hoy_dt = datetime.datetime(year=hoy.year, month=hoy.month, day=hoy.day)
        if current_user.can_admin("sentencias"):
            if hoy_dt + datetime.timedelta(days=-LIMITE_ADMINISTRADORES_DIAS) <= sentencia.creado:
                sentencia.delete()
                flash(f"Sentencia {sentencia.archivo} eliminada.", "success")
            else:
                flash(f"No tiene permiso para eliminar si fue creado hace {LIMITE_ADMINISTRADORES_DIAS} días o más.", "warning")
        elif current_user.autoridad_id == sentencia.autoridad_id:
            if hoy_dt + datetime.timedelta(days=-LIMITE_JUSTICIABLES_DIAS) <= sentencia.creado:
                sentencia.delete()
                flash(f"Sentencia {sentencia.archivo} eliminada.", "success")
            else:
                flash(f"No tiene permiso para eliminar si fue creado hace {LIMITE_JUSTICIABLES_DIAS} días o más.", "warning")
        else:
            flash("No tiene permiso para eliminar.", "warning")
    return redirect(url_for("sentencias.detail", sentencia_id=sentencia_id))


@sentencias.route("/sentencias/recuperar/<int:sentencia_id>")
@permission_required(Permiso.MODIFICAR_JUSTICIABLES)
def recover(sentencia_id):
    """Recuperar Sentencia"""
    sentencia = Sentencia.query.get_or_404(sentencia_id)
    if sentencia.estatus == "B":
        hoy = datetime.date.today()
        hoy_dt = datetime.datetime(year=hoy.year, month=hoy.month, day=hoy.day)
        if current_user.can_admin("sentencias"):
            if hoy_dt + datetime.timedelta(days=-LIMITE_ADMINISTRADORES_DIAS) <= sentencia.creado:
                sentencia.recover()
                flash(f"Sentencia {sentencia.archivo} recuperada.", "success")
            else:
                flash(f"No tiene permiso para eliminar si fue creado hace {LIMITE_ADMINISTRADORES_DIAS} días o más.", "warning")
        elif current_user.autoridad_id == sentencia.autoridad_id:
            if hoy_dt + datetime.timedelta(days=-LIMITE_JUSTICIABLES_DIAS) <= sentencia.creado:
                sentencia.recover()
                flash(f"Sentencia {sentencia.archivo} recuperada.", "success")
            else:
                flash(f"No tiene permiso para recuperar si fue creado hace {LIMITE_JUSTICIABLES_DIAS} días o más.", "warning")
        else:
            flash("No tiene permiso para recuperar.", "warning")
    return redirect(url_for("sentencias.detail", sentencia_id=sentencia_id))

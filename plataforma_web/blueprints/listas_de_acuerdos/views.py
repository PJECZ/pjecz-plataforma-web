"""
Listas de Acuerdos, vistas
"""
import datetime
from pathlib import Path

from flask import Blueprint, current_app, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required
from google.cloud import storage
from werkzeug.datastructures import CombinedMultiDict
from werkzeug.utils import secure_filename
from lib.safe_string import safe_string
from lib.time_to_text import dia_mes_ano, mes_en_palabra

from plataforma_web.blueprints.roles.models import Permiso
from plataforma_web.blueprints.usuarios.decorators import permission_required

from plataforma_web.blueprints.listas_de_acuerdos.forms import ListaDeAcuerdoNewForm, ListaDeAcuerdoEditForm, ListaDeAcuerdoSearchForm
from plataforma_web.blueprints.listas_de_acuerdos.models import ListaDeAcuerdo

from plataforma_web.blueprints.autoridades.models import Autoridad
from plataforma_web.blueprints.distritos.models import Distrito

listas_de_acuerdos = Blueprint("listas_de_acuerdos", __name__, template_folder="templates")

SUBDIRECTORIO = "Listas de Acuerdos"
LIMITE_JUSTICIABLES_DIAS = 1
LIMITE_ADMINISTRADORES_DIAS = 90


@listas_de_acuerdos.route("/listas_de_acuerdos/acuses/<id_hashed>")
def checkout(id_hashed):
    """Acuse"""
    lista_de_acuerdo = ListaDeAcuerdo.query.get_or_404(ListaDeAcuerdo.decode_id(id_hashed))
    dia, mes, ano = dia_mes_ano(lista_de_acuerdo.creado)
    return render_template("listas_de_acuerdos/checkout.jinja2", lista_de_acuerdo=lista_de_acuerdo, dia=dia, mes=mes.upper(), ano=ano)


@listas_de_acuerdos.before_request
@login_required
@permission_required(Permiso.VER_JUSTICIABLES)
def before_request():
    """Permiso por defecto"""


@listas_de_acuerdos.route("/listas_de_acuerdos")
def list_active():
    """Listado de Listas de Acuerdos activas más recientes"""
    # Si es administrador, ve las listas de acuerdos de todas las autoridades
    if current_user.can_admin("listas_de_acuerdos"):
        listas_activas = ListaDeAcuerdo.query.filter(ListaDeAcuerdo.estatus == "A").order_by(ListaDeAcuerdo.fecha.desc()).limit(100).all()
        return render_template("listas_de_acuerdos/list_admin.jinja2", autoridad=None, listas_de_acuerdos=listas_activas, estatus="A")
    # Si es jurisdiccional, ve sus propias listas de acuerdos
    if current_user.autoridad.es_jurisdiccional:
        sus_listas_activas = ListaDeAcuerdo.query.filter(ListaDeAcuerdo.autoridad == current_user.autoridad).filter(ListaDeAcuerdo.estatus == "A").order_by(ListaDeAcuerdo.fecha.desc()).limit(100).all()
        return render_template("listas_de_acuerdos/list.jinja2", autoridad=current_user.autoridad, listas_de_acuerdos=sus_listas_activas, estatus="A")
    # No es jurisdiccional, se redirige al listado de distritos
    return redirect(url_for("listas_de_acuerdos.list_distritos"))


@listas_de_acuerdos.route("/listas_de_acuerdos/inactivos")
@permission_required(Permiso.MODIFICAR_JUSTICIABLES)
def list_inactive():
    """Listado de Listas de Acuerdos inactivas"""
    # Si es administrador, ve las listas de acuerdos de todas las autoridades
    if current_user.can_admin("listas_de_acuerdos"):
        inactivas = ListaDeAcuerdo.query.filter(ListaDeAcuerdo.estatus == "B").order_by(ListaDeAcuerdo.creado.desc()).limit(100).all()
        return render_template("listas_de_acuerdos/list_admin.jinja2", autoridad=None, listas_de_acuerdos=inactivas, estatus="B")
    # Si es jurisdiccional, ve sus propias listas de acuerdos
    if current_user.autoridad.es_jurisdiccional:
        sus_listas_inactivas = ListaDeAcuerdo.query.filter(ListaDeAcuerdo.autoridad == current_user.autoridad).filter(ListaDeAcuerdo.estatus == "B").order_by(ListaDeAcuerdo.fecha.desc()).limit(100).all()
        return render_template("listas_de_acuerdos/list.jinja2", autoridad=current_user.autoridad, listas_de_acuerdos=sus_listas_inactivas, estatus="B")
    # No es jurisdiccional, se redirige al listado de distritos
    return redirect(url_for("listas_de_acuerdos.list_distritos"))


@listas_de_acuerdos.route("/listas_de_acuerdos/distritos")
def list_distritos():
    """Listado de Distritos"""
    distritos = Distrito.query.filter(Distrito.es_distrito_judicial == True).filter(Distrito.estatus == "A").order_by(Distrito.nombre).all()
    return render_template("listas_de_acuerdos/list_distritos.jinja2", distritos=distritos, estatus="A")


@listas_de_acuerdos.route("/listas_de_acuerdos/distrito/<int:distrito_id>")
def list_autoridades(distrito_id):
    """Listado de Autoridades de un distrito"""
    distrito = Distrito.query.get_or_404(distrito_id)
    autoridades = Autoridad.query.filter(Autoridad.distrito == distrito).filter(Autoridad.es_jurisdiccional == True).filter(Autoridad.es_notaria == False).filter(Autoridad.estatus == "A").order_by(Autoridad.clave).all()
    return render_template("listas_de_acuerdos/list_autoridades.jinja2", distrito=distrito, autoridades=autoridades, estatus="A")


@listas_de_acuerdos.route("/listas_de_acuerdos/autoridad/<int:autoridad_id>")
def list_autoridad_listas_de_acuerdos(autoridad_id):
    """Listado de Listas de Acuerdos activas de una autoridad"""
    autoridad = Autoridad.query.get_or_404(autoridad_id)
    listas_de_acuerdos_activas = ListaDeAcuerdo.query.filter(ListaDeAcuerdo.autoridad == autoridad).filter(ListaDeAcuerdo.estatus == "A").order_by(ListaDeAcuerdo.fecha.desc()).limit(100).all()
    return render_template("listas_de_acuerdos/list.jinja2", autoridad=autoridad, listas_de_acuerdos=listas_de_acuerdos_activas, estatus="A")


@listas_de_acuerdos.route("/listas_de_acuerdos/inactivos/autoridad/<int:autoridad_id>")
@permission_required(Permiso.ADMINISTRAR_JUSTICIABLES)
def list_autoridad_listas_de_acuerdos_inactive(autoridad_id):
    """Listado de Listas de Acuerdos inactivas de una autoridad"""
    autoridad = Autoridad.query.get_or_404(autoridad_id)
    listas_de_acuerdos_inactivas = ListaDeAcuerdo.query.filter(ListaDeAcuerdo.autoridad == autoridad).filter(ListaDeAcuerdo.estatus == "B").order_by(ListaDeAcuerdo.creado.desc()).limit(100).all()
    return render_template("listas_de_acuerdos/list.jinja2", autoridad=autoridad, listas_de_acuerdos=listas_de_acuerdos_inactivas, estatus="B")


@listas_de_acuerdos.route("/listas_de_acuerdos/refrescar/<int:autoridad_id>")
@permission_required(Permiso.ADMINISTRAR_JUSTICIABLES)
def refresh(autoridad_id):
    """Refrescar Listas de Acuerdos"""
    autoridad = Autoridad.query.get_or_404(autoridad_id)
    if current_user.get_task_in_progress("listas_de_acuerdos.tasks.refrescar"):
        flash("Debe esperar porque hay una tarea en el fondo sin terminar.", "warning")
    else:
        tarea = current_user.launch_task(
            nombre="listas_de_acuerdos.tasks.refrescar",
            descripcion=f"Refrescar listas de acuerdos de {autoridad.clave}",
            usuario_id=current_user.id,
            autoridad_id=autoridad.id,
        )
        flash(f"{tarea.descripcion} está corriendo en el fondo.", "info")
    return redirect(url_for("listas_de_acuerdos.list_autoridad_listas_de_acuerdos", autoridad_id=autoridad.id))


@listas_de_acuerdos.route("/listas_de_acuerdos/<int:lista_de_acuerdo_id>")
def detail(lista_de_acuerdo_id):
    """Detalle de una Lista de Acuerdos"""
    lista_de_acuerdo = ListaDeAcuerdo.query.get_or_404(lista_de_acuerdo_id)
    return render_template("listas_de_acuerdos/detail.jinja2", lista_de_acuerdo=lista_de_acuerdo)


@listas_de_acuerdos.route("/listas_de_acuerdos/buscar", methods=["GET", "POST"])
def search():
    """Buscar Lista de Acuerdos"""
    form_search = ListaDeAcuerdoSearchForm()
    if form_search.validate_on_submit():
        autoridad = Autoridad.query.get(form_search.autoridad.data)
        consulta = ListaDeAcuerdo.query.filter(ListaDeAcuerdo.autoridad == autoridad)
        if form_search.fecha_desde.data:
            consulta = consulta.filter(ListaDeAcuerdo.fecha >= form_search.fecha_desde.data)
        if form_search.fecha_hasta.data:
            consulta = consulta.filter(ListaDeAcuerdo.fecha <= form_search.fecha_hasta.data)
        consulta = consulta.order_by(ListaDeAcuerdo.fecha.desc()).limit(100).all()
        return render_template("listas_de_acuerdos/list.jinja2", autoridad=autoridad, listas_de_acuerdos=consulta)
    distritos = Distrito.query.filter(Distrito.es_distrito_judicial == True).filter(Distrito.estatus == "A").order_by(Distrito.nombre).all()
    autoridades = Autoridad.query.filter(Autoridad.es_jurisdiccional == True).filter(Autoridad.es_notaria == False).filter(Autoridad.estatus == "A").order_by(Autoridad.clave).all()
    return render_template("listas_de_acuerdos/search.jinja2", form=form_search, distritos=distritos, autoridades=autoridades)


@listas_de_acuerdos.route("/listas_de_acuerdos/nuevo", methods=["GET", "POST"])
@permission_required(Permiso.CREAR_JUSTICIABLES)
def new():
    """Subir Lista de Acuerdos como juzgado"""

    # Para validar la fecha
    hoy = datetime.date.today()
    hoy_dt = datetime.datetime(year=hoy.year, month=hoy.month, day=hoy.day)
    limite_dt = hoy_dt + datetime.timedelta(days=-LIMITE_JUSTICIABLES_DIAS)

    # Validar autoridad
    autoridad = current_user.autoridad
    if autoridad is None or autoridad.estatus != "A":
        flash("El juzgado/autoridad no existe o no es activa.", "warning")
        return redirect(url_for("listas_de_acuerdos.list_active"))
    if not autoridad.distrito.es_distrito_judicial:
        flash("El juzgado/autoridad no está en un distrito jurisdiccional.", "warning")
        return redirect(url_for("listas_de_acuerdos.list_active"))
    if not autoridad.es_jurisdiccional:
        flash("El juzgado/autoridad no es jurisdiccional.", "warning")
        return redirect(url_for("listas_de_acuerdos.list_active"))
    if autoridad.directorio_listas_de_acuerdos is None or autoridad.directorio_listas_de_acuerdos == "":
        flash("El juzgado/autoridad no tiene directorio para listas de acuerdos.", "warning")
        return redirect(url_for("listas_de_acuerdos.list_active"))

    # Si viene el formulario
    form = ListaDeAcuerdoNewForm(CombinedMultiDict((request.files, request.form)))
    if form.validate_on_submit():

        # Tomar valores del formulario
        fecha = form.fecha.data
        descripcion = safe_string(form.descripcion.data)
        archivo = request.files["archivo"]

        # Validar fecha
        if not limite_dt <= datetime.datetime(year=fecha.year, month=fecha.month, day=fecha.day) <= hoy_dt:
            flash(f"La fecha no debe ser del futuro ni anterior a {LIMITE_JUSTICIABLES_DIAS} días.", "warning")
            form.fecha.data = hoy
            return render_template("listas_de_acuerdos/new.jinja2", form=form)

        # Validar descripcion, porque safe_string puede resultar vacío
        if descripcion == "":
            flash("La descripción es incorrecta.", "warning")
            return render_template("listas_de_acuerdos/new.jinja2", form=form)

        # Validar archivo
        archivo_nombre = secure_filename(archivo.filename.lower())
        if "." not in archivo_nombre or archivo_nombre.rsplit(".", 1)[1] != "pdf":
            flash("No es un archivo PDF.", "warning")
            return render_template("listas_de_acuerdos/new.jinja2", form=form)

        # Si existe una lista de acuerdos de la misma fecha, dar de baja la antigua
        anterior_borrada = False
        anterior_lista_de_acuerdo = ListaDeAcuerdo.query.filter(ListaDeAcuerdo.autoridad == autoridad).filter(ListaDeAcuerdo.fecha == fecha).filter(ListaDeAcuerdo.estatus == "A").first()
        if anterior_lista_de_acuerdo:
            anterior_lista_de_acuerdo.delete()
            anterior_borrada = True

        # Insertar registro
        lista_de_acuerdo = ListaDeAcuerdo(
            autoridad=autoridad,
            fecha=fecha,
            descripcion=descripcion,
        )
        lista_de_acuerdo.save()

        # Elaborar nombre del archivo y ruta SUBDIRECTORIO/Autoridad/YYYY/MES/archivo.pdf
        ano_str = fecha.strftime("%Y")
        mes_str = mes_en_palabra(fecha.month)
        fecha_str = fecha.strftime("%Y-%m-%d")
        descripcion_str = descripcion.replace(" ", "-")
        archivo_str = f"{fecha_str}-{descripcion_str}-{lista_de_acuerdo.encode_id()}.pdf"
        ruta_str = str(Path(SUBDIRECTORIO, autoridad.directorio_listas_de_acuerdos, ano_str, mes_str, archivo_str))

        # Subir el archivo
        deposito = current_app.config["CLOUD_STORAGE_DEPOSITO"]
        storage_client = storage.Client()
        bucket = storage_client.bucket(deposito)
        blob = bucket.blob(ruta_str)
        blob.upload_from_string(archivo.stream.read(), content_type="application/pdf")
        url = blob.public_url

        # Actualizar el nombre del archivo y el url
        lista_de_acuerdo.archivo = archivo_str
        lista_de_acuerdo.url = url
        lista_de_acuerdo.save()

        # Mostrar mensaje de éxito y detalle
        if anterior_borrada:
            flash(f"Lista de Acuerdos del {lista_de_acuerdo.fecha} reemplazada.", "success")
        else:
            flash(f"Lista de Acuerdos del {lista_de_acuerdo.fecha} guardada.", "success")
        return redirect(url_for("listas_de_acuerdos.detail", lista_de_acuerdo_id=lista_de_acuerdo.id))

    # Prellenado de los campos
    form.distrito.data = autoridad.distrito.nombre
    form.autoridad.data = autoridad.descripcion
    form.descripcion.data = "LISTA DE ACUERDOS"
    form.fecha.data = hoy
    return render_template("listas_de_acuerdos/new.jinja2", form=form)


@listas_de_acuerdos.route("/listas_de_acuerdos/nuevo/<int:autoridad_id>", methods=["GET", "POST"])
@permission_required(Permiso.ADMINISTRAR_JUSTICIABLES)
def new_for_autoridad(autoridad_id):
    """Subir Lista de Acuerdos para una autoridad dada"""

    # Para validar la fecha
    hoy = datetime.date.today()
    hoy_dt = datetime.datetime(year=hoy.year, month=hoy.month, day=hoy.day)
    limite_dt = hoy_dt + datetime.timedelta(days=-LIMITE_ADMINISTRADORES_DIAS)

    # Validar autoridad
    autoridad = Autoridad.query.get_or_404(autoridad_id)
    if autoridad is None:
        flash("El juzgado/autoridad no existe.", "warning")
        return redirect(url_for("listas_de_acuerdos.list_active"))
    if autoridad.estatus != "A":
        flash("El juzgado/autoridad no es activa.", "warning")
        return redirect(url_for("autoridades.detail", autoridad_id=autoridad.id))
    if not autoridad.distrito.es_distrito_judicial:
        flash("El juzgado/autoridad no está en un distrito jurisdiccional.", "warning")
        return redirect(url_for("autoridades.detail", autoridad_id=autoridad.id))
    if not autoridad.es_jurisdiccional:
        flash("El juzgado/autoridad no es jurisdiccional.", "warning")
        return redirect(url_for("autoridades.detail", autoridad_id=autoridad.id))
    if autoridad.directorio_listas_de_acuerdos is None or autoridad.directorio_listas_de_acuerdos == "":
        flash("El juzgado/autoridad no tiene directorio para edictos.", "warning")
        return redirect(url_for("autoridades.detail", autoridad_id=autoridad.id))

    # Si viene el formulario
    form = ListaDeAcuerdoNewForm(CombinedMultiDict((request.files, request.form)))
    if form.validate_on_submit():

        # Tomar valores del formulario
        fecha = form.fecha.data
        descripcion = safe_string(form.descripcion.data)
        archivo = request.files["archivo"]

        # Validar fecha
        archivo_nombre = secure_filename(archivo.filename.lower())
        if not limite_dt <= datetime.datetime(year=fecha.year, month=fecha.month, day=fecha.day) <= hoy_dt:
            flash(f"La fecha no debe ser del futuro ni anterior a {LIMITE_ADMINISTRADORES_DIAS} días.", "warning")
            form.fecha.data = hoy
            return render_template("listas_de_acuerdos/new_for_autoridad.jinja2", form=form, autoridad=autoridad)

        # Validar descripcion, porque safe_string puede resultar vacío
        if descripcion == "":
            flash("La descripción es incorrecta.", "warning")
            return render_template("listas_de_acuerdos/new_for_autoridad.jinja2", form=form, autoridad=autoridad)

        # Validar archivo
        if "." not in archivo_nombre or archivo_nombre.rsplit(".", 1)[1] != "pdf":
            flash("No es un archivo PDF.", "warning")
            return render_template("listas_de_acuerdos/new_for_autoridad.jinja2", form=form, autoridad=autoridad)

        # Si existe una lista de acuerdos de la misma fecha, dar de baja la antigua
        anterior_borrada = False
        anterior_lista_de_acuerdo = ListaDeAcuerdo.query.filter(ListaDeAcuerdo.autoridad == autoridad).filter(ListaDeAcuerdo.fecha == fecha).filter(ListaDeAcuerdo.estatus == "A").first()
        if anterior_lista_de_acuerdo:
            anterior_lista_de_acuerdo.delete()
            anterior_borrada = True

        # Insertar registro
        lista_de_acuerdo = ListaDeAcuerdo(
            autoridad=autoridad,
            fecha=fecha,
            descripcion=descripcion,
        )
        lista_de_acuerdo.save()

        # Elaborar nombre del archivo y ruta SUBDIRECTORIO/Autoridad/YYYY/MES/archivo.pdf
        ano_str = fecha.strftime("%Y")
        mes_str = mes_en_palabra(fecha.month)
        fecha_str = fecha.strftime("%Y-%m-%d")
        descripcion_str = descripcion.replace(" ", "-")
        archivo_str = f"{fecha_str}-{descripcion_str}-{lista_de_acuerdo.encode_id()}.pdf"
        ruta_str = str(Path(SUBDIRECTORIO, autoridad.directorio_listas_de_acuerdos, ano_str, mes_str, archivo_str))

        # Subir el archivo
        deposito = current_app.config["CLOUD_STORAGE_DEPOSITO"]
        storage_client = storage.Client()
        bucket = storage_client.bucket(deposito)
        blob = bucket.blob(ruta_str)
        blob.upload_from_string(archivo.stream.read(), content_type="application/pdf")
        url = blob.public_url

        # Actualizar el nombre del archivo y el url
        lista_de_acuerdo.archivo = archivo_str
        lista_de_acuerdo.url = url
        lista_de_acuerdo.save()

        # Mostrar mensaje de éxito y detalle
        if anterior_borrada:
            flash(f"Lista de Acuerdos del {lista_de_acuerdo.fecha} reemplazada.", "success")
        else:
            flash(f"Lista de Acuerdos del {lista_de_acuerdo.fecha} guardada.", "success")
        return redirect(url_for("listas_de_acuerdos.detail", lista_de_acuerdo_id=lista_de_acuerdo.id))

    # Prellenado de los campos
    form.distrito.data = autoridad.distrito.nombre
    form.autoridad.data = autoridad.descripcion
    form.descripcion.data = "LISTA DE ACUERDOS"
    form.fecha.data = hoy
    return render_template("listas_de_acuerdos/new_for_autoridad.jinja2", form=form, autoridad=autoridad)


@listas_de_acuerdos.route("/listas_de_acuerdos/edicion/<int:lista_de_acuerdo_id>", methods=["GET", "POST"])
@permission_required(Permiso.ADMINISTRAR_JUSTICIABLES)
def edit(lista_de_acuerdo_id):
    """Editar Lista de Acuerdos"""
    lista_de_acuerdo = ListaDeAcuerdo.query.get_or_404(lista_de_acuerdo_id)
    form = ListaDeAcuerdoEditForm()
    if form.validate_on_submit():
        lista_de_acuerdo.fecha = form.fecha.data
        lista_de_acuerdo.descripcion = safe_string(form.descripcion.data)
        lista_de_acuerdo.save()
        flash(f"Lista de Acuerdos {lista_de_acuerdo.archivo} guardado.", "success")
        return redirect(url_for("listas_de_acuerdos.detail", lista_de_acuerdo_id=lista_de_acuerdo.id))
    form.fecha.data = lista_de_acuerdo.fecha
    form.descripcion.data = lista_de_acuerdo.descripcion
    return render_template("listas_de_acuerdos/edit.jinja2", form=form, lista_de_acuerdo=lista_de_acuerdo)


@listas_de_acuerdos.route("/listas_de_acuerdos/eliminar/<int:lista_de_acuerdo_id>")
@permission_required(Permiso.MODIFICAR_JUSTICIABLES)
def delete(lista_de_acuerdo_id):
    """Eliminar Lista de Acuerdos"""
    lista_de_acuerdo = ListaDeAcuerdo.query.get_or_404(lista_de_acuerdo_id)
    if lista_de_acuerdo.estatus == "A":
        if current_user.can_admin("listas_de_acuerdos"):
            hoy = datetime.date.today()
            hoy_dt = datetime.datetime(year=hoy.year, month=hoy.month, day=hoy.day)
            if hoy_dt + datetime.timedelta(days=-LIMITE_ADMINISTRADORES_DIAS) <= lista_de_acuerdo.creado:
                lista_de_acuerdo.delete()
                flash(f"Lista de Acuerdos {lista_de_acuerdo.archivo} eliminado.", "success")
            else:
                flash(f"No tiene permiso para eliminar si fue creado hace {LIMITE_ADMINISTRADORES_DIAS} días o más.", "warning")
        elif current_user.autoridad_id == lista_de_acuerdo.autoridad_id and lista_de_acuerdo.fecha == datetime.date.today():
            lista_de_acuerdo.delete()
            flash(f"Lista de Acuerdos {lista_de_acuerdo.archivo} eliminado.", "success")
        else:
            flash("No tiene permiso para eliminar o sólo puede eliminar de hoy.", "warning")
    return redirect(url_for("listas_de_acuerdos.detail", lista_de_acuerdo_id=lista_de_acuerdo_id))


@listas_de_acuerdos.route("/listas_de_acuerdos/recuperar/<int:lista_de_acuerdo_id>")
@permission_required(Permiso.MODIFICAR_JUSTICIABLES)
def recover(lista_de_acuerdo_id):
    """Recuperar Lista de Acuerdos"""
    lista_de_acuerdo = ListaDeAcuerdo.query.get_or_404(lista_de_acuerdo_id)
    if lista_de_acuerdo.estatus == "B":
        if ListaDeAcuerdo.query.filter(ListaDeAcuerdo.autoridad == current_user.autoridad).filter(ListaDeAcuerdo.fecha == lista_de_acuerdo.fecha).filter(ListaDeAcuerdo.estatus == "A").first():
            flash("No puede recuperar esta lista porque ya hay una activa de la misma fecha.", "warning")
        else:
            if current_user.can_admin("listas_de_acuerdos"):
                hoy = datetime.date.today()
                hoy_dt = datetime.datetime(year=hoy.year, month=hoy.month, day=hoy.day)
                if hoy_dt + datetime.timedelta(days=-LIMITE_ADMINISTRADORES_DIAS) <= lista_de_acuerdo.creado:
                    lista_de_acuerdo.recover()
                    flash(f"Lista de Acuerdos {lista_de_acuerdo.archivo} recuperado.", "success")
                else:
                    flash(f"No tiene permiso para recuperar si fue creado hace {LIMITE_ADMINISTRADORES_DIAS} días o más.", "warning")
            elif current_user.autoridad_id == lista_de_acuerdo.autoridad_id and lista_de_acuerdo.fecha == datetime.date.today():
                lista_de_acuerdo.recover()
                flash(f"Lista de Acuerdos {lista_de_acuerdo.archivo} recuperado.", "success")
            else:
                flash("No tiene permiso para recuperar o sólo puede recuperar de hoy.", "warning")
    return redirect(url_for("listas_de_acuerdos.detail", lista_de_acuerdo_id=lista_de_acuerdo_id))

"""
Edictos, vistas
"""
from datetime import date, timedelta
from pathlib import Path
from unidecode import unidecode

from flask import Blueprint, current_app, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required
from google.cloud import storage
from werkzeug.datastructures import CombinedMultiDict
from werkzeug.utils import secure_filename
from lib.time_to_text import dia_mes_ano

from plataforma_web.blueprints.roles.models import Permiso
from plataforma_web.blueprints.usuarios.decorators import permission_required

from plataforma_web.blueprints.edictos.forms import EdictoEditForm, EdictoNewForm, EdictoSearchForm
from plataforma_web.blueprints.edictos.models import Edicto

from plataforma_web.blueprints.autoridades.models import Autoridad
from plataforma_web.blueprints.distritos.models import Distrito

edictos = Blueprint("edictos", __name__, template_folder="templates")

SUBDIRECTORIO = "Edictos"
DIAS_LIMITE = 5


def subir_archivo(autoridad_id: int, fecha: date, archivo: str, puede_reemplazar: bool = False):
    """Subir archivo de edictos"""
    # Configuración
    deposito = current_app.config["CLOUD_STORAGE_DEPOSITO"]
    # Validar autoridad
    autoridad = Autoridad.query.get(autoridad_id)
    if autoridad is None or autoridad.estatus != "A":
        raise ValueError("El juzgado/autoridad no existe o no es activa.")
    if not autoridad.distrito.es_distrito_judicial:
        raise ValueError("El juzgado/autoridad no está en un distrito jurisdiccional.")
    if not autoridad.es_jurisdiccional:
        raise ValueError("El juzgado/autoridad no es jurisdiccional.")
    if autoridad.directorio_edictos is None or autoridad.directorio_edictos == "":
        raise ValueError("El juzgado/autoridad no tiene directorio para edictos.")


@edictos.before_request
@login_required
@permission_required(Permiso.VER_)
def before_request():
    """Permiso por defecto"""


@edictos.route("/edictos")
def list_active():
    """Listado de Edictos activos"""
    edictos_activos = Edicto.query.filter(Edicto.estatus == "A").order_by(Edicto.creado.desc()).limit(100).all()
    return render_template("edictos/list.jinja2", edictos=edictos_activos, estatus="A")


"""
@edictos.route("/edictos")
def list_active():
    edictos_activos = Edicto.query.filter(Edicto.estatus == "A").order_by(Edicto.fecha.desc()).limit(100).all()
    return render_template("edictos/list.jinja2", edictos=edictos_activos, estatus="A")


@edictos.route("/edictos/inactivos")
@permission_required(Permiso.MODIFICAR_JUSTICIABLES)
def list_inactive():
    edictos_inactivos = Edicto.query.filter(Edicto.estatus == "B").order_by(Edicto.fecha.desc()).limit(100).all()
    return render_template("edictos/list.jinja2", edictos=edictos_inactivos, estatus="B")


@edictos.route("/edictos/<int:edicto_id>")
def detail(edicto_id):
    edicto = Edicto.query.get_or_404(edicto_id)
    return render_template("edictos/detail.jinja2", edicto=edicto)


@edictos.route("/edictos/buscar", methods=["GET", "POST"])
def search():
    form_search = EdictoSearchForm()
    if form_search.validate_on_submit():
        consulta = Edicto.query
        if form_search.expediente.data:
            expediente = form_search.expediente.data.strip()
            consulta = consulta.filter(Edicto.expediente.like(f"%{expediente}%"))
        consulta = consulta.order_by(Edicto.fecha.desc()).limit(100).all()
        return render_template("edictos/list.jinja2", edictos=consulta)
    return render_template("edictos/search.jinja2", form=form_search)


@edictos.route("/edictos/nuevo", methods=["GET", "POST"])
@permission_required(Permiso.CREAR_JUSTICIABLES)
def new():
    form = EdictoForm()
    if form.validate_on_submit():
        edicto = Edicto(
            descripcion=form.descripcion.data,
            archivo=form.archivo.data,
            fecha=form.fecha.data,
            expediente=form.expediente.data,
            numero_publicacion=form.numero_publicacion.data,
            url=form.url.data,
        )
        edicto.save()
        flash(f"Edicto {edicto.descripcion} guardado.", "success")
        return redirect(url_for("edictos.detail", edicto_id=edicto.id))
    return render_template("edictos/new.jinja2", form=form)


@edictos.route("/edictos/edicion/<int:edicto_id>", methods=["GET", "POST"])
@permission_required(Permiso.MODIFICAR_JUSTICIABLES)
def edit(edicto_id):
    edicto = Edicto.query.get_or_404(edicto_id)
    form = EdictoForm()
    if form.validate_on_submit():
        edicto.descripcion = form.descripcion.data
        edicto.archivo = form.archivo.data
        edicto.fecha = form.fecha.data
        edicto.expediente = form.expediente.data
        edicto.numero_publicacion = form.numero_publicacion.data
        edicto.url = form.url.data
        edicto.save()
        flash(f"Edicto {edicto.descripcion} guardado.", "success")
        return redirect(url_for("edictos.detail", edicto_id=edicto.id))
    form.descripcion.data = edicto.descripcion
    form.archivo.data = edicto.archivo
    form.fecha.data = edicto.fecha
    form.expediente.data = edicto.expediente
    form.numero_publicacion.data = edicto.numero_publicacion
    form.url.data = edicto.url
    return render_template("edictos/edit.jinja2", form=form, edicto=edicto)


@edictos.route("/edictos/eliminar/<int:edicto_id>")
@permission_required(Permiso.MODIFICAR_JUSTICIABLES)
def delete(edicto_id):
    edicto = Edicto.query.get_or_404(edicto_id)
    if edicto.estatus == "A":
        edicto.delete()
        flash(f"Edicto {edicto.Edicto} eliminado.", "success")
    return redirect(url_for("edictos.detail", edicto_id=edicto_id))


@edictos.route("/edictos/recuperar/<int:edicto_id>")
@permission_required(Permiso.MODIFICAR_JUSTICIABLES)
def recover(edicto_id):
    edicto = Edicto.query.get_or_404(edicto_id)
    if edicto.estatus == "B":
        edicto.recover()
        flash(f"Edicto {edicto.Edicto} recuperado.", "success")
    return redirect(url_for("edictos.detail", edicto_id=edicto_id))
"""

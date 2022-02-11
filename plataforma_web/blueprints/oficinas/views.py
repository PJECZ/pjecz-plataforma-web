"""
Oficinas, vistas
"""
import datetime

from flask import Blueprint, flash, redirect, render_template, url_for
from flask_login import current_user, login_required

from lib.safe_string import safe_clave, safe_message, safe_string

from plataforma_web.blueprints.permisos.models import Permiso
from plataforma_web.blueprints.usuarios.decorators import permission_required

from plataforma_web.blueprints.bitacoras.models import Bitacora
from plataforma_web.blueprints.modulos.models import Modulo
from plataforma_web.blueprints.oficinas.models import Oficina

from plataforma_web.blueprints.oficinas.forms import OficinaForm

MODULO = "OFICINAS"

oficinas = Blueprint("oficinas", __name__, template_folder="templates")


@oficinas.route("/oficinas")
@login_required
@permission_required(MODULO, Permiso.VER)
def list_active():
    """Listado de Oficinas activas"""
    activos = Oficina.query.filter(Oficina.estatus == "A").all()
    return render_template(
        "oficinas/list.jinja2",
        oficinas=activos,
        titulo="Oficinas",
        estatus="A",
    )


@oficinas.route("/oficinas/inactivos")
@login_required
@permission_required(MODULO, Permiso.MODIFICAR)
def list_inactive():
    """Listado de Oficinas inactivas"""
    inactivos = Oficina.query.filter(Oficina.estatus == "B").all()
    return render_template(
        "oficinas/list.jinja2",
        oficinas=inactivos,
        titulo="Oficinas inactivas",
        estatus="B",
    )


@oficinas.route("/oficinas/<int:oficina_id>")
@login_required
@permission_required(MODULO, Permiso.VER)
def detail(oficina_id):
    """Detalle de una Oficina"""
    oficina = Oficina.query.get_or_404(oficina_id)
    return render_template("oficinas/detail.jinja2", oficina=oficina)


@oficinas.route("/oficinas/nuevo", methods=["GET", "POST"])
@login_required
@permission_required(MODULO, Permiso.CREAR)
def new():
    """Nueva Oficina"""
    form = OficinaForm()
    if form.validate_on_submit():
        clave = safe_clave(form.clave.data)
        if Oficina.query.filter(Oficina.clave == clave).first():
            flash("La clave ya está en uso. Debe de ser única.", "warning")
        else:
            oficina = Oficina(
                clave=clave,
                descripcion_corta=safe_string(form.descripcion_corta.data),
                descripcion=safe_string(form.descripcion.data),
                es_jurisdiccional=form.es_jurisdiccional.data == 1,
                apertura=form.apertura.data,
                cierre=form.cierre.data,
                limite_personas=form.limite_personas.data,
                domicilio=form.domicilio.data,
                distrito=form.distrito.data,
            )
            oficina.save()
            bitacora = Bitacora(
                modulo=Modulo.query.filter_by(nombre=MODULO).first(),
                usuario=current_user,
                descripcion=safe_message(f"Nueva Oficina {oficina.clave}"),
                url=url_for("oficinas.detail", oficina_id=oficina.id),
            )
            bitacora.save()
            flash(bitacora.descripcion, "success")
            return redirect(bitacora.url)
    return render_template("oficinas/new.jinja2", form=form)


@oficinas.route("/oficinas/edicion/<int:oficina_id>", methods=["GET", "POST"])
@login_required
@permission_required(MODULO, Permiso.MODIFICAR)
def edit(oficina_id):
    """Editar Oficina"""
    oficina = Oficina.query.get_or_404(oficina_id)
    form = OficinaForm()
    if form.validate_on_submit():
        clave = safe_clave(form.clave.data)
        # Validar que la clave este disponible
        if oficina.clave != clave and Oficina.query.filter(Oficina.clave == clave).first():
            flash("La clave ya está en uso. Debe de ser única.", "warning")
        else:
            oficina.distrito = form.distrito.data
            oficina.domicilio = form.domicilio.data
            oficina.clave = safe_string(form.clave.data)
            oficina.descripcion_corta = safe_string(form.descripcion_corta.data)
            oficina.descripcion = safe_string(form.descripcion.data)
            oficina.es_jurisdiccional = form.es_jurisdiccional.data == 1
            oficina.apertura = form.apertura.data
            oficina.cierre = form.cierre.data
            oficina.limite_personas = form.limite_personas.data
            oficina.save()
            bitacora = Bitacora(
                modulo=Modulo.query.filter_by(nombre=MODULO).first(),
                usuario=current_user,
                descripcion=safe_message(f"Editado la Oficina {oficina.clave}"),
                url=url_for("oficinas.detail", oficina_id=oficina.id),
            )
            bitacora.save()
            flash(bitacora.descripcion, "success")
            return redirect(bitacora.url)
    form.distrito.data = oficina.distrito
    form.domicilio.data = oficina.domicilio
    form.clave.data = oficina.clave
    form.descripcion_corta.data = oficina.descripcion_corta
    form.descripcion.data = oficina.descripcion
    form.es_jurisdiccional.data = oficina.es_jurisdiccional
    form.apertura.data = oficina.apertura
    form.cierre.data = oficina.cierre
    form.limite_personas.data = oficina.limite_personas
    return render_template("oficinas/edit.jinja2", form=form, oficina=oficina)


@oficinas.route("/oficinas/eliminar/<int:oficina_id>")
@login_required
@permission_required(MODULO, Permiso.MODIFICAR)
def delete(oficina_id):
    """Eliminar Oficina"""
    oficina = Oficina.query.get_or_404(oficina_id)
    if oficina.estatus == "A":
        oficina.delete()
        bitacora = Bitacora(
            modulo=Modulo.query.filter_by(nombre=MODULO).first(),
            usuario=current_user,
            descripcion=safe_message(f"Eliminado el servicio {oficina.clave}"),
            url=url_for("oficinas.detail", oficina_id=oficina.id),
        )
        bitacora.save()
        flash(bitacora.descripcion, "success")
    return redirect(url_for("oficinas.detail", oficina_id=oficina_id))


@oficinas.route("/oficinas/recuperar/<int:oficina_id>")
@login_required
@permission_required(MODULO, Permiso.MODIFICAR)
def recover(oficina_id):
    """Recuperar Oficina"""
    oficina = Oficina.query.get_or_404(oficina_id)
    if oficina.estatus == "B":
        oficina.recover()
        bitacora = Bitacora(
            modulo=Modulo.query.filter_by(nombre=MODULO).first(),
            usuario=current_user,
            descripcion=safe_message(f"Recuperado el Servicio {oficina.clave}"),
            url=url_for("oficinas.detail", oficina_id=oficina.id),
        )
        bitacora.save()
        flash(bitacora.descripcion, "success")
    return redirect(url_for("oficinas.detail", oficina_id=oficina_id))

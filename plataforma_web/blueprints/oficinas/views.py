"""
Oficinas, vistas
"""

import datetime
from dateutil.relativedelta import relativedelta

from flask import Blueprint, flash, redirect, request, render_template, url_for
from flask_login import current_user, login_required

from lib.safe_string import safe_message, safe_string

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
    """Detalle de un Servicio"""
    oficina = Oficina.query.get_or_404(oficina_id)
    return render_template("oficinas/detail.jinja2", oficina=oficina)

@oficinas.route("/oficinas/nuevo", methods=["GET", "POST"])
@login_required
@permission_required(MODULO, Permiso.CREAR)
def new():
    """Nuevo Servicio"""
    form = OficinaForm()
    validacion = False
    if form.validate_on_submit():
        try:
            _validar(form)
            validacion = True
        except Exception as err:
            flash(f"Creación de la nueva Oficina incorrecta. {str(err)}", "warning")
            validacion = False

        if validacion:
            oficina = Oficina(
                clave=safe_string(form.clave.data),
                descripcion_corta=form.descripcion_corta.data,
                descripcion=form.descripcion.data,
                es_juridiccional=form.es_juridiccional.data,
                apertura=form.apertura.data,
                cierre=form.cierre.data,
                limite_personas=form.limite_personas.data,
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
    validacion = False
    if form.validate_on_submit():

        try:
            _validar(form, True)
            validacion = True
        except Exception as err:
            flash(f"Actualización incorrecta de la oficina. {str(err)}", "warning")
            validacion = False

        if validacion:
            oficina.clave = safe_string(form.clave.data)
            oficina.descripcion_corta = safe_string(form.descripcion_corta.data)
            oficina.descripcion = safe_string(form.descripcion.data)
            oficina.es_juridiccional = form.es_juridiccional.data
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
    form.clave.data = oficina.clave
    form.descripcion_corta.data = oficina.descripcion_corta
    form.descripcion.data = oficina.descripcion
    form.es_juridiccional.data = oficina.es_juridiccional
    form.apertura.data = oficina.apertura
    form.cierre.data = oficina.cierre
    form.limite_personas.data = oficina.limite_personas
    return render_template("oficinas/edit.jinja2", form=form, oficina=oficina)


def _validar(form, same = False):
    if not same:
        clave_existente = Oficina.query.filter(Oficina.clave == form.clave.data).first()
        if clave_existente:
            raise Exception("La clave ya se encuentra en uso.")
    min_horario = datetime.time(5,0,0)
    max_horario = datetime.time(18,0,0)
    min_horario_str = min_horario.strftime("%H:%M")
    max_horario_str = max_horario.strftime("%H:%M")
    if form.apertura.data < min_horario or form.apertura.data > max_horario:
        raise Exception(f"El horario de apertura se encuentra fuera de lo permitido, el rango permitido es de: {min_horario_str} a {max_horario_str}")
    if form.cierre.data < min_horario or form.cierre.data > max_horario:
        raise Exception(f"El horario de cierre se encuentra fuera de lo permitido, el rango permitido es de: {min_horario_str} a {max_horario_str}")
    return True


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

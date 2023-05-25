"""
SIGA Salas, vistas
"""
import json
from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from lib.datatables import get_datatable_parameters, output_datatable_json
from lib.safe_string import safe_string, safe_message, safe_text
from plataforma_web.blueprints.usuarios.decorators import permission_required
from sqlalchemy import func

from plataforma_web.blueprints.bitacoras.models import Bitacora
from plataforma_web.blueprints.siga_salas.forms import SIGASalaNewForm, SIGASalaEditForm
from plataforma_web.blueprints.siga_salas.models import SIGASala
from plataforma_web.blueprints.modulos.models import Modulo
from plataforma_web.blueprints.permisos.models import Permiso
from plataforma_web.blueprints.domicilios.models import Domicilio
from plataforma_web.blueprints.materias.models import Materia
from plataforma_web.blueprints.siga_bitacoras.models import SIGABitacora
from plataforma_web.blueprints.siga_grabaciones.models import SIGAGrabacion

MODULO = "SIGA_SALAS"

siga_salas = Blueprint("siga_salas", __name__, template_folder="templates")


@siga_salas.before_request
@login_required
@permission_required(MODULO, Permiso.VER)
def before_request():
    """Permiso por defecto"""


@siga_salas.route("/siga_salas/datatable_json", methods=["GET", "POST"])
def datatable_json():
    """DataTable JSON para listado de siga_salas"""
    # Tomar parámetros de Datatables
    draw, start, rows_per_page = get_datatable_parameters()
    # Consultar
    consulta = SIGASala.query
    if "estatus" in request.form:
        consulta = consulta.filter_by(estatus=request.form["estatus"])
    else:
        consulta = consulta.filter_by(estatus="A")
    if "clave" in request.form:
        clave = safe_string(request.form["clave"])
        consulta = consulta.filter(SIGASala.clave.contains(clave))
    if "edificio" in request.form:
        edificio_id = int(request.form["edificio"])
        consulta = consulta.filter_by(domicilio_id=edificio_id)
    if "estado" in request.form:
        consulta = consulta.filter_by(estado=request.form["estado"])
    registros = consulta.order_by(SIGASala.clave).offset(start).limit(rows_per_page).all()
    total = consulta.count()
    # Elaborar datos para DataTable
    data = []
    for resultado in registros:
        data.append(
            {
                "detalle": {
                    "clave": resultado.clave,
                    "url": url_for("siga_salas.detail", siga_sala_id=resultado.id),
                },
                "edificio": resultado.domicilio.distrito.clave + " : " + resultado.domicilio.edificio,
                "direccion_ip": resultado.direccion_ip,
                "direccion_nvr": resultado.direccion_nvr,
                "estado": resultado.estado,
                "descripcion": resultado.descripcion,
            }
        )
    # Entregar JSON
    return output_datatable_json(draw, total, data)


@siga_salas.route("/siga_salas")
def list_active():
    """Listado de SIGASala activas"""
    return render_template(
        "siga_salas/list.jinja2",
        filtros=json.dumps({"estatus": "A"}),
        titulo="SIGA Salas",
        estatus="A",
        estados_salas=SIGASala.ESTADOS,
    )


@siga_salas.route("/siga_salas/inactivos")
@permission_required(MODULO, Permiso.MODIFICAR)
def list_inactive():
    """Listado de SIGASala inactivas"""
    return render_template(
        "siga_salas/list.jinja2",
        filtros=json.dumps({"estatus": "B"}),
        titulo="SIGA Salas Inactivas",
        estatus="B",
        estados_salas=SIGASala.ESTADOS,
    )


@siga_salas.route("/siga_salas/<int:siga_sala_id>")
def detail(siga_sala_id):
    """Detalle de un SIGASala"""
    siga_sala = SIGASala.query.get_or_404(siga_sala_id)
    return render_template(
        "siga_salas/detail.jinja2",
        siga_sala=siga_sala,
        filtros=json.dumps({"estatus": "A", "sala_id": siga_sala.id}),
        materias=Materia.query.filter_by(estatus="A").order_by(Materia.nombre).all(),
        acciones_bitacoras=SIGABitacora.ACCIONES,
        estados_bitacoras=SIGABitacora.ESTADOS,
        estados_grabaciones=SIGAGrabacion.ESTADOS,
    )


@siga_salas.route("/siga_salas/nuevo", methods=["GET", "POST"])
@permission_required(MODULO, Permiso.CREAR)
def new():
    """ "Crear una nueva SIGA Sala"""
    form = SIGASalaNewForm()
    if form.validate_on_submit():
        es_valido = True
        clave = safe_string(form.clave.data)
        if SIGASala.query.filter_by(clave=clave).first():
            es_valido = False
            flash("La Clave de la Sala ya está en uso.", "warning")
        edificio_id = int(form.edificio.data)
        edificio = Domicilio.query.filter_by(id=edificio_id).first()
        if edificio is None:
            es_valido = False
            flash("El Edificio no es válido.", "warning")
        # Si es valido, insertar
        if es_valido:
            sala = SIGASala(
                clave=clave,
                domicilio=edificio,
                direccion_ip=form.direccion_ip.data,
                direccion_nvr=form.direccion_nvr.data,
                estado="OPERATIVO",
                descripcion=safe_text(form.descripcion.data),
            )
            sala.save()
            bitacora = Bitacora(
                modulo=Modulo.query.filter_by(nombre=MODULO).first(),
                usuario=current_user,
                descripcion=safe_message(f"Nueva SIGA Sala {sala}"),
                url=url_for("siga_salas.list_active"),
            )
            bitacora.save()
            flash(bitacora.descripcion, "success")
            return redirect(bitacora.url)
    # Mostrar formulario
    return render_template("siga_salas/new.jinja2", form=form)


@siga_salas.route("/siga_salas/edicion/<int:siga_sala_id>", methods=["GET", "POST"])
@permission_required(MODULO, Permiso.MODIFICAR)
def edit(siga_sala_id):
    """Editar SIGASala"""
    siga_sala = SIGASala.query.get_or_404(siga_sala_id)
    form = SIGASalaEditForm()
    if form.validate_on_submit():
        es_valido = True
        clave = safe_string(form.clave.data)
        if SIGASala.query.filter_by(clave=clave).filter(SIGASala.id != siga_sala_id).first():
            es_valido = False
            flash("La Clave de la Sala ya está en uso.", "warning")
        edificio_id = int(form.edificio.data)
        edificio = Domicilio.query.filter_by(id=edificio_id).first()
        if edificio is None:
            es_valido = False
            flash("El Edificio no es válido.", "warning")
        # Si es valido, actualizar
        if es_valido:
            siga_sala.clave = clave
            siga_sala.edificio = edificio
            siga_sala.direccion_ip = form.direccion_ip.data
            siga_sala.direccion_nvr = form.direccion_nvr.data
            siga_sala.estado = form.estado.data
            siga_sala.descripcion = safe_text(form.descripcion.data)
            siga_sala.save()
            bitacora = Bitacora(
                modulo=Modulo.query.filter_by(nombre=MODULO).first(),
                usuario=current_user,
                descripcion=safe_message(f"Editado la Sala {siga_sala.clave}"),
                url=url_for("siga_salas.list_active"),
            )
            bitacora.save()
            flash(bitacora.descripcion, "success")
            return redirect(bitacora.url)
    form.clave.data = siga_sala.clave
    form.edificio.data = siga_sala.domicilio
    form.direccion_ip.data = siga_sala.direccion_ip
    form.direccion_nvr.data = siga_sala.direccion_nvr
    form.estado.data = siga_sala.estado
    form.descripcion.data = siga_sala.descripcion
    return render_template("siga_salas/edit.jinja2", form=form, siga_sala=siga_sala)


@siga_salas.route("/siga_salas/eliminar/<int:siga_sala_id>")
@permission_required(MODULO, Permiso.MODIFICAR)
def delete(siga_sala_id):
    """Eliminar SIGASala"""
    siga_sala = SIGASala.query.get_or_404(siga_sala_id)
    if siga_sala.estatus == "A":
        siga_sala.delete()
        bitacora = Bitacora(
            modulo=Modulo.query.filter_by(nombre=MODULO).first(),
            usuario=current_user,
            descripcion=safe_message(f"Eliminada la SIGA_Sala {siga_sala.clave}"),
            url=url_for("siga_salas.detail", siga_sala_id=siga_sala.id),
        )
        bitacora.save()
        flash(bitacora.descripcion, "success")
    return redirect(url_for("siga_salas.detail", siga_sala_id=siga_sala_id))


@siga_salas.route("/siga_salas/recuperar/<int:siga_sala_id>")
@permission_required(MODULO, Permiso.MODIFICAR)
def recover(siga_sala_id):
    """Recuperar SIGASala"""
    siga_sala = SIGASala.query.get_or_404(siga_sala_id)
    if siga_sala.estatus == "B":
        siga_sala.recover()
        bitacora = Bitacora(
            modulo=Modulo.query.filter_by(nombre=MODULO).first(),
            usuario=current_user,
            descripcion=safe_message(f"Recuperada la SIGA_Sala {siga_sala.clave}"),
            url=url_for("siga_salas.detail", siga_sala_id=siga_sala.id),
        )
        bitacora.save()
        flash(bitacora.descripcion, "success")
    return redirect(url_for("siga_salas.detail", siga_sala_id=siga_sala_id))


@siga_salas.route("/siga_salas/salas_json", methods=["POST"])
def query_salas_json():
    """Proporcionar el JSON de salas para elegir Salas con un Select2"""
    consulta = SIGASala.query.filter(SIGASala.estatus == "A")
    if "clave" in request.form:
        consulta = consulta.filter(SIGASala.clave.contains(request.form["clave"]))
    results = []
    for sala in consulta.order_by(SIGASala.clave).limit(15).all():
        results.append({"id": sala.id, "text": sala.clave + " : " + sala.domicilio.edificio})
    return {"results": results, "pagination": {"more": False}}

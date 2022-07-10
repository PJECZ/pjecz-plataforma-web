"""
Financieros Vales, vistas
"""
import json
from flask import Blueprint, current_app, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from lib.datatables import get_datatable_parameters, output_datatable_json
from lib.safe_string import safe_email, safe_string, safe_message

from plataforma_web.blueprints.bitacoras.models import Bitacora
from plataforma_web.blueprints.fin_vales.models import FinVale
from plataforma_web.blueprints.fin_vales.forms import (
    FinValeStep1CreateForm,
    FinValeStep2RequestForm,
    FinValeCancel2RequestForm,
    FinValeStep3AuthorizeForm,
    FinValeCancel3AuthorizeForm,
    FinValeStep4DeliverForm,
    FinValeStep5AttachmentsForm,
    FinValeStep6ArchiveForm,
)
from plataforma_web.blueprints.modulos.models import Modulo
from plataforma_web.blueprints.permisos.models import Permiso
from plataforma_web.blueprints.usuarios.decorators import permission_required

MODULO = "FIN VALES"

ROL_SOLICITANTES = "FINANCIEROS SOLICITANTES"
ROL_AUTORIZANTES = "FINANCIEROS AUTORIZANTES"

fin_vales = Blueprint("fin_vales", __name__, template_folder="templates")


@fin_vales.before_request
@login_required
@permission_required(MODULO, Permiso.VER)
def before_request():
    """Permiso por defecto"""


@fin_vales.route("/fin_vales/datatable_json", methods=["GET", "POST"])
def datatable_json():
    """DataTable JSON para listado de vales"""
    # Tomar parámetros de Datatables
    draw, start, rows_per_page = get_datatable_parameters()
    # Consultar
    consulta = FinVale.query
    if "estatus" in request.form:
        consulta = consulta.filter_by(estatus=request.form["estatus"])
    else:
        consulta = consulta.filter_by(estatus="A")
    if "usuario_id" in request.form:
        consulta = consulta.filter_by(usuario_id=request.form["usuario_id"])
    if "estado" in request.form:
        consulta = consulta.filter_by(estado=request.form["estado"])
    registros = consulta.order_by(FinVale.id.desc()).offset(start).limit(rows_per_page).all()
    total = consulta.count()
    # Elaborar datos para DataTable
    data = []
    for resultado in registros:
        data.append(
            {
                "detalle": {
                    "id": resultado.id,
                    "url": url_for("fin_vales.detail", fin_vale_id=resultado.id),
                },
                "estado": resultado.estado,
                "justificacion": resultado.justificacion,
                "monto": resultado.monto,
                "tipo": resultado.tipo,
                "usuario_nombre": resultado.usuario.nombre,
            }
        )
    # Entregar JSON
    return output_datatable_json(draw, total, data)


@fin_vales.route("/fin_vales")
def list_active():
    """Listado de Vales activos"""
    if current_user.can_admin(MODULO):
        return render_template(
            "fin_vales/list.jinja2",
            filtros=json.dumps({"estatus": "A"}),
            titulo="Todos los Vales",
            estatus="A",
        )
    return render_template(
        "fin_vales/list.jinja2",
        filtros=json.dumps({"estatus": "A", "usuario_id": current_user.id}),
        titulo="Vales",
        estatus="A",
    )


@fin_vales.route("/fin_vales/inactivos")
@permission_required(MODULO, Permiso.MODIFICAR)
def list_inactive():
    """Listado de Vales inactivos"""
    if current_user.can_admin(MODULO):
        return render_template(
            "fin_vales/list.jinja2",
            filtros=json.dumps({"estatus": "B"}),
            titulo="Todos los Vales inactivos",
            estatus="B",
        )
    return render_template(
        "fin_vales/list.jinja2",
        filtros=json.dumps({"estatus": "B", "usuario_id": current_user.id}),
        titulo="Vales inactivos",
        estatus="B",
    )


@fin_vales.route("/fin_vales/<int:fin_vale_id>")
def detail(fin_vale_id):
    """Detalle de un Vale"""
    fin_vale = FinVale.query.get_or_404(fin_vale_id)
    # Validar que sea el usuario que creo el vale o un administrador
    if not (current_user.can_admin(MODULO) or current_user.id == fin_vale.usuario_id):
        flash("No tiene permiso para ver el detalle de este Vale", "warning")
        return redirect(url_for("fin_vales.list_active"))
    return render_template("fin_vales/detail.jinja2", fin_vale=fin_vale)


@fin_vales.route("/fin_vale/crear", methods=["GET", "POST"])
@permission_required(MODULO, Permiso.CREAR)
def step_1_create():
    """Formulario Vale (step 1 create) Crear"""
    form = FinValeStep1CreateForm()
    if form.validate_on_submit():
        fin_vale = FinVale(
            usuario=current_user,
            estado="PENDIENTE",
            justificacion=safe_string(form.justificacion.data, max_len=1020, to_uppercase=False, do_unidecode=False),
            monto=form.monto.data,
            tipo=form.tipo.data,
        )
        fin_vale.save()
        bitacora = Bitacora(
            modulo=Modulo.query.filter_by(nombre=MODULO).first(),
            usuario=current_user,
            descripcion=safe_message(f"Vale creado {fin_vale.justificacion}"),
            url=url_for("fin_vales.detail", fin_vale_id=fin_vale.id),
        )
        bitacora.save()
        flash(bitacora.descripcion, "success")
        return redirect(bitacora.url)
    form.usuario_nombre.data = current_user.nombre
    form.usuario_puesto.data = current_user.puesto
    form.usuario_email.data = current_user.email
    form.tipo.data = "GASOLINA"
    form.justificacion.data = "Solicito un vale de gasolina de $100.00 (cien pesos 00/100 m.n), para NOMBRE COMPLETO con el objetivo de ir a DESTINO U OFICINA."
    form.monto.data = 100.00
    return render_template("fin_vales/step_1_create.jinja2", form=form)


@fin_vales.route("/fin_vales/solicitar/<int:fin_vale_id>", methods=["GET", "POST"])
@permission_required(MODULO, Permiso.MODIFICAR)
def step_2_request(fin_vale_id):
    """Formulario Vale (step 2 request) Solicitar"""
    fin_vale = FinVale.query.get_or_404(fin_vale_id)
    puede_firmarlo = True
    # Validar que sea activo
    if fin_vale.estatus != "A":
        flash("El vale esta eliminado", "warning")
        puede_firmarlo = False
    # Validar el estado
    if fin_vale.estado != "PENDIENTE":
        flash("El vale NO esta en estado PENDIENTE", "warning")
        puede_firmarlo = False
    # Validar que el usuario puede solicitarlo
    # Si no puede solicitarlo, redireccionar a la pagina de detalle
    if not puede_firmarlo:
        return redirect(url_for("fin_vales.detail", fin_vale_id=fin_vale_id))
    # Si viene el formulario
    form = FinValeStep2RequestForm()
    if form.validate_on_submit():
        # Actualizar
        # Crear la tarea en el fondo
        current_app.task_queue.enqueue(
            "plataforma_web.blueprints.fin_vales.tasks.solicitar",
            fin_vale_id=fin_vale.id,
            contrasena=form.contrasena.data,
        )
        flash("Tarea en el fondo lanzada para comunicarse con el motor de firma electrónica", "success")
        return redirect(url_for("fin_vales.detail", fin_vale_id=fin_vale_id))
    # Mostrar formulario
    form.solicito_nombre.data = current_user.nombre
    form.solicito_puesto.data = current_user.puesto
    form.solicito_email.data = current_user.email
    return render_template("fin_vales/step_2_request.jinja2", form=form, fin_vale=fin_vale)


@fin_vales.route("/fin_vales/cancelar_solicitado/<int:fin_vale_id>", methods=["GET", "POST"])
@permission_required(MODULO, Permiso.MODIFICAR)
def cancel_2_request(fin_vale_id):
    """Formulario Vale (cancel 2 request) Cancelar solicitado"""
    fin_vale = FinVale.query.get_or_404(fin_vale_id)
    puede_cancelarlo = True
    # Validar que sea activo
    if fin_vale.estatus != "A":
        flash("El vale esta eliminado", "warning")
        puede_cancelarlo = False
    # Validar el estado
    if fin_vale.estado != "SOLICITADO":
        flash("El vale NO esta en estado SOLICITADO", "warning")
        puede_cancelarlo = False
    # Validar que el usuario puede cancelarlo
    # Si no puede cancelarlo, redireccionar a la pagina de detalle
    if not puede_cancelarlo:
        return redirect(url_for("fin_vales.detail", fin_vale_id=fin_vale_id))
    # Si viene el formulario
    form = FinValeCancel2RequestForm()
    # Mostrar formulario
    form.solicito_nombre.data = current_user.nombre
    form.solicito_puesto.data = current_user.puesto
    form.solicito_email.data = current_user.email
    return render_template("fin_vales/cancel_2_request.jinja2", form=form, fin_vale=fin_vale)


@fin_vales.route("/fin_vales/autorizar/<int:fin_vale_id>", methods=["GET", "POST"])
@permission_required(MODULO, Permiso.MODIFICAR)
def step_3_authorize(fin_vale_id):
    """Formulario Vale (step 3 authorize) Autorizar"""
    fin_vale = FinVale.query.get_or_404(fin_vale_id)
    puede_firmarlo = True
    # Validar que sea activo
    if fin_vale.estatus != "A":
        flash("El vale esta eliminado", "warning")
        puede_firmarlo = False
    # Validar el estado
    if fin_vale.estado != "SOLICITADO":
        flash("El vale NO esta en estado SOLICITADO", "warning")
        puede_firmarlo = False
    # Validar que el usuario puede autorizar el vale
    if not (current_user.can_admin(MODULO) or current_user.email == fin_vale.autorizo_email):
        flash(f"Usted no es quien puede autorizar este vale; es {fin_vale.autorizo_email}", "warning")
        puede_firmarlo = False
    # Si no puede autorizarlo, redireccionar a la pagina de detalle
    if not puede_firmarlo:
        return redirect(url_for("fin_vales.detail", fin_vale_id=fin_vale_id))
    # Si viene el formulario
    form = FinValeStep3AuthorizeForm()
    # Mostrar formulario
    form.autorizo_nombre.data = current_user.nombre
    form.autorizo_puesto.data = current_user.puesto
    form.autorizo_email.data = current_user.email
    return render_template("fin_vales/step_3_authorize.jinja2", form=form, fin_vale=fin_vale)


@fin_vales.route("/fin_vales/cancelar_autorizado/<int:fin_vale_id>", methods=["GET", "POST"])
@permission_required(MODULO, Permiso.MODIFICAR)
def cancel_3_authorize(fin_vale_id):
    """Formulario Vale (cancel 3 authorize) Cancelar autorizado"""
    fin_vale = FinVale.query.get_or_404(fin_vale_id)
    puede_cancelarlo = True
    # Validar que sea activo
    if fin_vale.estatus != "A":
        flash("El vale esta eliminado", "warning")
        puede_cancelarlo = False
    # Validar el estado
    if fin_vale.estado != "AUTORIZADO":
        flash("El vale NO esta en estado AUTORIZADO", "warning")
        puede_cancelarlo = False
    # Validar que el usuario puede solicitar el vale
    if not (current_user.can_admin(MODULO) or current_user.email == fin_vale.autorizo_email):
        flash(f"Usted no es quien puede cancelar esta firma electronica; es {fin_vale.solicito_email}", "warning")
        puede_cancelarlo = False
    # Si no puede cancelarlo, redireccionar a la pagina de detalle
    if not puede_cancelarlo:
        return redirect(url_for("fin_vales.detail", fin_vale_id=fin_vale_id))
    # Si viene el formulario
    form = FinValeCancel3AuthorizeForm()
    # Mostrar formulario
    form.autorizo_nombre.data = current_user.nombre
    form.autorizo_puesto.data = current_user.puesto
    form.autorizo_email.data = current_user.email
    return render_template("fin_vales/cancel_3_authorize.jinja2", form=form, fin_vale=fin_vale)


@fin_vales.route("/fin_vales/entregar/<int:fin_vale_id>", methods=["GET", "POST"])
@permission_required(MODULO, Permiso.MODIFICAR)
def step_4_deliver(fin_vale_id):
    """Formulario Vale (step 4 deliver) Entregar"""
    fin_vale = FinVale.query.get_or_404(fin_vale_id)
    form = FinValeStep4DeliverForm()
    # Mostrar formulario
    return render_template("fin_vales/step_4_deliver.jinja2", form=form, fin_vale=fin_vale)


@fin_vales.route("/fin_vales/por_revisar/<int:fin_vale_id>", methods=["GET", "POST"])
@permission_required(MODULO, Permiso.MODIFICAR)
def step_5_attachments(fin_vale_id):
    """Formulario Vale (step 5 attachments) Adjuntar"""
    fin_vale = FinVale.query.get_or_404(fin_vale_id)
    form = FinValeStep5AttachmentsForm()
    # Mostrar formulario
    return render_template("fin_vales/step_5_attachments.jinja2", form=form, fin_vale=fin_vale)


@fin_vales.route("/fin_vales/archivar/<int:fin_vale_id>", methods=["GET", "POST"])
@permission_required(MODULO, Permiso.MODIFICAR)
def step_6_archive(fin_vale_id):
    """Formulario Vale (step 6 archive) Archivar"""
    fin_vale = FinVale.query.get_or_404(fin_vale_id)
    form = FinValeStep6ArchiveForm()
    # Mostrar formulario
    return render_template("fin_vales/step_6_archive.jinja2", form=form, fin_vale=fin_vale)


@fin_vales.route("/fin_vales/eliminar/<int:fin_vale_id>")
@permission_required(MODULO, Permiso.ADMINISTRAR)
def delete(fin_vale_id):
    """Eliminar Vale"""
    fin_vale = FinVale.query.get_or_404(fin_vale_id)
    if fin_vale.estatus == "A":
        if (fin_vale.usuario == current_user or current_user.can_admin(MODULO)) and fin_vale.estado == "PENDIENTE":
            fin_vale.estado = "ELIMINADO POR USUARIO"
        elif (fin_vale.solicito_email == current_user.email or current_user.can_admin(MODULO)) and fin_vale.estado == "SOLICITADO":
            fin_vale.estado = "ELIMINADO POR SOLICITANTE"
        elif (fin_vale.autorizo_email == current_user.email or current_user.can_admin(MODULO)) and fin_vale.estado == "AUTORIZADO":
            fin_vale.estado = "ELIMINADO POR AUTORIZADOR"
        else:
            flash("No tiene permisos para eliminar o tiene un estado particular este vale", "warning")
            return redirect(url_for("fin_vales.detail", fin_vale_id=fin_vale_id))
        fin_vale.delete()
        bitacora = Bitacora(
            modulo=Modulo.query.filter_by(nombre=MODULO).first(),
            usuario=current_user,
            descripcion=safe_message(f"Eliminado Vale {fin_vale.justificacion}"),
            url=url_for("fin_vales.detail", fin_vale_id=fin_vale.id),
        )
        bitacora.save()
        flash(bitacora.descripcion, "success")
    return redirect(url_for("fin_vales.detail", fin_vale_id=fin_vale.id))


@fin_vales.route("/fin_vales/recuperar/<int:fin_vale_id>")
@permission_required(MODULO, Permiso.MODIFICAR)
def recover(fin_vale_id):
    """Recuperar Vale"""
    fin_vale = FinVale.query.get_or_404(fin_vale_id)
    if fin_vale.estatus == "B":
        if (fin_vale.usuario == current_user or current_user.can_admin(MODULO)) and fin_vale.estado == "ELIMINADO POR USUARIO":
            fin_vale.estado = "PENDIENTE"
        elif (fin_vale.solicito_email == current_user.email or current_user.can_admin(MODULO)) and fin_vale.estado == "ELIMINADO POR SOLICITANTE":
            fin_vale.estado = "SOLICITADO"
        elif (fin_vale.autorizo_email == current_user.email or current_user.can_admin(MODULO)) and fin_vale.estado == "ELIMINADO POR AUTORIZADOR":
            fin_vale.estado = "AUTORIZADO"
        else:
            flash("No tiene permisos para recuperar o tiene un estado particular este vale", "warning")
            return redirect(url_for("fin_vales.detail", fin_vale_id=fin_vale_id))
        fin_vale.recover()
        bitacora = Bitacora(
            modulo=Modulo.query.filter_by(nombre=MODULO).first(),
            usuario=current_user,
            descripcion=safe_message(f"Recuperado Vale {fin_vale.justificacion}"),
            url=url_for("fin_vales.detail", fin_vale_id=fin_vale.id),
        )
        bitacora.save()
        flash(bitacora.descripcion, "success")
    return redirect(url_for("fin_vales.detail", fin_vale_id=fin_vale.id))

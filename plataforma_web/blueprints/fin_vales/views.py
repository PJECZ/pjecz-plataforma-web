"""
Financieros Vales, vistas
"""
import json
from flask import Blueprint, current_app, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from lib.datatables import get_datatable_parameters, output_datatable_json
from lib.safe_string import safe_string, safe_message

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

fin_vales = Blueprint("fin_vales", __name__, template_folder="templates")

MODULO = "FIN VALES"

# Roles que deben estar en la base de datos
ROL_SOLICITANTES = "FINANCIEROS SOLICITANTES"
ROL_AUTORIZANTES = "FINANCIEROS AUTORIZANTES"


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
                "usuario_oficina_clave": resultado.usuario.oficina.clave,
            }
        )
    # Entregar JSON
    return output_datatable_json(draw, total, data)


@fin_vales.route("/fin_vales")
def list_active():
    """Listado de Vales activos"""
    # Si es administrador puede ver Todos los Vales activos
    if current_user.can_admin(MODULO):
        return render_template(
            "fin_vales/list.jinja2",
            filtros=json.dumps({"estatus": "A"}),
            titulo="Todos los Vales",
            estatus="A",
        )
    # Consultar los roles del usuario
    current_user_roles = current_user.get_roles()
    # Si es autorizante, mostrar Vales por Autorizar
    if ROL_AUTORIZANTES in current_user_roles:
        return render_template(
            "fin_vales/list.jinja2",
            filtros=json.dumps({"estatus": "A", "estado": "SOLICITADO"}),
            titulo="Vales Solicitados (por autorizar)",
            estatus="A",
        )
    # Si es solicitante, mostrar Vales por Solicitar
    if ROL_SOLICITANTES in current_user_roles:
        return render_template(
            "fin_vales/list.jinja2",
            filtros=json.dumps({"estatus": "A", "estado": "CREADO"}),
            titulo="Vales Creados (por solicitar)",
            estatus="A",
        )
    # Mostrar Mis Vales
    return render_template(
        "fin_vales/list.jinja2",
        filtros=json.dumps({"estatus": "A", "usuario_id": current_user.id}),
        titulo="Mis Vales",
        estatus="A",
    )


@fin_vales.route("/fin_vales/mis_vales")
def list_mine_active():
    """Listado de Mis Vales activos"""
    return render_template(
        "fin_vales/list.jinja2",
        filtros=json.dumps({"estatus": "A", "usuario_id": current_user.id}),
        titulo="Mis Vales",
        estatus="A",
    )


@fin_vales.route("/fin_vales/creados")
def list_create_active():
    """Listado de Vales Creados activos"""
    return render_template(
        "fin_vales/list.jinja2",
        filtros=json.dumps({"estatus": "A", "estado": "CREADO"}),
        titulo="Vales Creados",
        estatus="A",
    )


@fin_vales.route("/fin_vales/solicitados")
def list_request_active():
    """Listado de Vales Solicitados activos"""
    return render_template(
        "fin_vales/list.jinja2",
        filtros=json.dumps({"estatus": "A", "estado": "SOLICITADO"}),
        titulo="Vales Solicitados",
        estatus="A",
    )


@fin_vales.route("/fin_vales/autorizados")
def list_authorize_active():
    """Listado de Vales Autorizados activos"""
    return render_template(
        "fin_vales/list.jinja2",
        filtros=json.dumps({"estatus": "A", "estado": "AUTORIZADO"}),
        titulo="Vales Autorizados",
        estatus="A",
    )


@fin_vales.route("/fin_vales/entregados")
def list_deliver_active():
    """Listado de Vales Entregados activos"""
    return render_template(
        "fin_vales/list.jinja2",
        filtros=json.dumps({"estatus": "A", "estado": "ENTREGADO"}),
        titulo="Vales Entregados",
        estatus="A",
    )


@fin_vales.route("/fin_vales/por_revisar")
def list_attachments_active():
    """Listado de Vales Por Revisar activos"""
    return render_template(
        "fin_vales/list.jinja2",
        filtros=json.dumps({"estatus": "A", "estado": "POR REVISAR"}),
        titulo="Vales Por Revisar",
        estatus="A",
    )


@fin_vales.route("/fin_vales/archivados")
def list_archive_active():
    """Listado de Vales Archivados activos"""
    return render_template(
        "fin_vales/list.jinja2",
        filtros=json.dumps({"estatus": "A", "estado": "ARCHIVADO"}),
        titulo="Vales Archivados",
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
    current_user_roles = current_user.get_roles()
    if not (current_user.can_admin(MODULO) or ROL_SOLICITANTES in current_user_roles or ROL_AUTORIZANTES in current_user_roles or current_user.id == fin_vale.usuario_id):
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
            estado="CREADO",
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
    form.justificacion.data = f"Solicito un vale de gasolina de $100.00 (cien pesos 00/100 m.n), para {current_user.nombre} con el objetivo de ir a DESTINO U OFICINA."
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
    if fin_vale.estado != "CREADO":
        flash("El vale no esta en estado CREADO", "warning")
        puede_firmarlo = False
    # Validar el usuario
    if current_user.efirma_registro_id is None:
        flash("Usted no tiene registro en la firma electronica", "warning")
        puede_firmarlo = False
    if ROL_SOLICITANTES not in current_user.get_roles():
        flash("Usted no tiene el rol para solicitar un vale", "warning")
        puede_firmarlo = False
    # Si no puede solicitarlo, redireccionar a la pagina de detalle
    if not puede_firmarlo:
        return redirect(url_for("fin_vales.detail", fin_vale_id=fin_vale_id))
    # Si viene el formulario
    form = FinValeStep2RequestForm()
    if form.validate_on_submit():
        # Crear la tarea en el fondo
        current_app.task_queue.enqueue(
            "plataforma_web.blueprints.fin_vales.tasks.solicitar",
            fin_vale_id=fin_vale.id,
            usuario_id=current_user.id,
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
        flash("El vale no esta en estado SOLICITADO", "warning")
        puede_cancelarlo = False
    # Validar el usuario
    if current_user.efirma_registro_id is None:
        flash("Usted no tiene registro en la firma electronica", "warning")
        puede_cancelarlo = False
    if ROL_SOLICITANTES not in current_user.get_roles():
        flash("Usted no tiene el rol para cancelar un vale solicitado", "warning")
        puede_cancelarlo = False
    if fin_vale.solicito_email != current_user.email:
        flash("Usted no es el solicitante de este vale", "warning")
        puede_cancelarlo = False
    # Si no puede cancelarlo, redireccionar a la pagina de detalle
    if not puede_cancelarlo:
        return redirect(url_for("fin_vales.detail", fin_vale_id=fin_vale_id))
    # Si viene el formulario
    form = FinValeCancel2RequestForm()
    if form.validate_on_submit():
        # Crear la tarea en el fondo
        current_app.task_queue.enqueue(
            "plataforma_web.blueprints.fin_vales.tasks.cancelar_solicitar",
            fin_vale_id=fin_vale.id,
            contrasena=form.contrasena.data,
            motivo=form.motivo.data,
        )
        flash("Tarea en el fondo lanzada para comunicarse con el motor de firma electrónica", "success")
        return redirect(url_for("fin_vales.detail", fin_vale_id=fin_vale_id))
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
        flash("El vale no esta en estado SOLICITADO", "warning")
        puede_firmarlo = False
    # Validar el usuario
    if current_user.efirma_registro_id is None:
        flash("Usted no tiene registro en la firma electronica", "warning")
        puede_firmarlo = False
    if ROL_AUTORIZANTES not in current_user.get_roles():
        flash("Usted no tiene el rol para autorizar un vale", "warning")
        puede_firmarlo = False
    # Si no puede autorizarlo, redireccionar a la pagina de detalle
    if not puede_firmarlo:
        return redirect(url_for("fin_vales.detail", fin_vale_id=fin_vale_id))
    # Si viene el formulario
    form = FinValeStep3AuthorizeForm()
    if form.validate_on_submit():
        # Crear la tarea en el fondo
        current_app.task_queue.enqueue(
            "plataforma_web.blueprints.fin_vales.tasks.autorizar",
            fin_vale_id=fin_vale.id,
            usuario_id=current_user.id,
            contrasena=form.contrasena.data,
        )
        flash("Tarea en el fondo lanzada para comunicarse con el motor de firma electrónica", "success")
        return redirect(url_for("fin_vales.detail", fin_vale_id=fin_vale_id))
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
        flash("El vale no esta en estado AUTORIZADO", "warning")
        puede_cancelarlo = False
    # Validar el usuario
    if current_user.efirma_registro_id is None:
        flash("Usted no tiene registro en la firma electronica", "warning")
        puede_cancelarlo = False
    if ROL_AUTORIZANTES not in current_user.get_roles():
        flash("Usted no tiene el rol para cancelar un vale autorizado", "warning")
        puede_cancelarlo = False
    if fin_vale.autorizo_email != current_user.email:
        flash("Usted no es el autorizante de este vale", "warning")
        puede_cancelarlo = False
    # Si no puede cancelarlo, redireccionar a la pagina de detalle
    if not puede_cancelarlo:
        return redirect(url_for("fin_vales.detail", fin_vale_id=fin_vale_id))
    # Si viene el formulario
    form = FinValeCancel3AuthorizeForm()
    if form.validate_on_submit():
        # Crear la tarea en el fondo
        current_app.task_queue.enqueue(
            "plataforma_web.blueprints.fin_vales.tasks.cancelar_autorizar",
            fin_vale_id=fin_vale.id,
            contrasena=form.contrasena.data,
            motivo=form.motivo.data,
        )
        flash("Tarea en el fondo lanzada para comunicarse con el motor de firma electrónica", "success")
        return redirect(url_for("fin_vales.detail", fin_vale_id=fin_vale_id))
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
    puede_entregarlo = True
    # Validar que sea activo
    if fin_vale.estatus != "A":
        flash("El vale esta eliminado", "warning")
        puede_entregarlo = False
    # Validar el estado
    if fin_vale.estado != "AUTORIZADO":
        flash("El vale no esta en estado AUTORIZADO", "warning")
        puede_entregarlo = False
    # Validar el usuario
    if ROL_AUTORIZANTES not in current_user.get_roles():
        flash("Usted no tiene el rol para entregar un vale", "warning")
        puede_entregarlo = False
    # Si no puede entregarlo, redireccionar a la pagina de detalle
    if not puede_entregarlo:
        return redirect(url_for("fin_vales.detail", fin_vale_id=fin_vale_id))
    # Si viene el formulario
    form = FinValeStep4DeliverForm()
    if form.validate_on_submit():
        fin_vale.folio = safe_string(form.folio.data)
        fin_vale.estado = "ENTREGADO"
        fin_vale.save()
        bitacora = Bitacora(
            modulo=Modulo.query.filter_by(nombre=MODULO).first(),
            usuario=current_user,
            descripcion=safe_message(f"Entregado Vale {fin_vale.id}"),
            url=url_for("fin_vales.detail", fin_vale_id=fin_vale.id),
        )
        bitacora.save()
        flash(bitacora.descripcion, "success")
        return redirect(bitacora.url)
    # Mostrar formulario
    return render_template("fin_vales/step_4_deliver.jinja2", form=form, fin_vale=fin_vale)


@fin_vales.route("/fin_vales/por_revisar/<int:fin_vale_id>", methods=["GET", "POST"])
@permission_required(MODULO, Permiso.MODIFICAR)
def step_5_attachments(fin_vale_id):
    """Formulario Vale (step 5 attachments) Adjuntar"""
    fin_vale = FinVale.query.get_or_404(fin_vale_id)
    puede_adjuntar = True
    # Validar que sea activo
    if fin_vale.estatus != "A":
        flash("El vale esta eliminado", "warning")
        puede_adjuntar = False
    # Validar el estado
    if fin_vale.estado != "ENTREGADO" and fin_vale.estado != "POR REVISAR":
        flash("El vale no esta en estado ENTREGADO o POR REVISAR", "warning")
        puede_adjuntar = False
    # Validar el usuario
    if current_user.id != fin_vale.usuario_id:
        flash("Usted no es el usuario que creo el vale", "warning")
        puede_adjuntar = False
    # Si no puede entregarlo, redireccionar a la pagina de detalle
    if not puede_adjuntar:
        return redirect(url_for("fin_vales.detail", fin_vale_id=fin_vale_id))
    # Si viene el formulario
    form = FinValeStep5AttachmentsForm()
    if form.validate_on_submit():
        fin_vale.vehiculo_descripcion = safe_string(form.vehiculo_descripcion.data)
        fin_vale.tanque_inicial = safe_string(form.tanque_inicial.data)
        fin_vale.tanque_final = safe_string(form.tanque_final.data)
        fin_vale.kilometraje_inicial = form.kilometraje_inicial.data
        fin_vale.kilometraje_final = form.kilometraje_final.data
        fin_vale.estado = "POR REVISAR"
        fin_vale.save()
        bitacora = Bitacora(
            modulo=Modulo.query.filter_by(nombre=MODULO).first(),
            usuario=current_user,
            descripcion=safe_message(f"Por revisar Vale {fin_vale.id}"),
            url=url_for("fin_vales.detail", fin_vale_id=fin_vale.id),
        )
        bitacora.save()
        flash(bitacora.descripcion, "success")
        return redirect(bitacora.url)
    # Mostrar formulario
    form.vehiculo_descripcion.data = fin_vale.vehiculo_descripcion
    form.tanque_inicial.data = fin_vale.tanque_inicial
    form.tanque_final.data = fin_vale.tanque_final
    form.kilometraje_inicial.data = fin_vale.kilometraje_inicial
    form.kilometraje_final.data = fin_vale.kilometraje_final
    return render_template("fin_vales/step_5_attachments.jinja2", form=form, fin_vale=fin_vale)


@fin_vales.route("/fin_vales/archivar/<int:fin_vale_id>", methods=["GET", "POST"])
@permission_required(MODULO, Permiso.MODIFICAR)
def step_6_archive(fin_vale_id):
    """Formulario Vale (step 6 archive) Archivar"""
    fin_vale = FinVale.query.get_or_404(fin_vale_id)
    puede_archivarlo = True
    # Validar que sea activo
    if fin_vale.estatus != "A":
        flash("El vale esta eliminado", "warning")
        puede_archivarlo = False
    # Validar el estado
    if fin_vale.estado != "POR REVISAR":
        flash("El vale no esta en estado POR REVISAR", "warning")
        puede_archivarlo = False
    # Validar el usuario
    if ROL_AUTORIZANTES not in current_user.get_roles():
        flash("Usted no tiene el rol para archivar un vale", "warning")
        puede_archivarlo = False
    # Si no puede entregarlo, redireccionar a la pagina de detalle
    if not puede_archivarlo:
        return redirect(url_for("fin_vales.detail", fin_vale_id=fin_vale_id))
    # Si viene el formulario
    form = FinValeStep6ArchiveForm()
    if form.validate_on_submit():
        fin_vale.notas = safe_string(form.notas.data, to_uppercase=False)
        fin_vale.estado = "ARCHIVADO"
        fin_vale.save()
        bitacora = Bitacora(
            modulo=Modulo.query.filter_by(nombre=MODULO).first(),
            usuario=current_user,
            descripcion=safe_message(f"Archivado Vale {fin_vale.id}"),
            url=url_for("fin_vales.detail", fin_vale_id=fin_vale.id),
        )
        bitacora.save()
        flash(bitacora.descripcion, "success")
        return redirect(bitacora.url)
    # Mostrar formulario
    fin_vale.notas = "Ninguna"
    return render_template("fin_vales/step_6_archive.jinja2", form=form, fin_vale=fin_vale)


@fin_vales.route("/fin_vales/eliminar/<int:fin_vale_id>")
@permission_required(MODULO, Permiso.MODIFICAR)
def delete(fin_vale_id):
    """Eliminar Vale"""
    fin_vale = FinVale.query.get_or_404(fin_vale_id)
    if fin_vale.estatus == "A":
        puede_eliminarlo = False
        if current_user.can_admin(MODULO):
            puede_eliminarlo = True
        if fin_vale.usuario == current_user and fin_vale.estado == "CREADO":
            puede_eliminarlo = True
        if fin_vale.solicito_email == current_user.email and fin_vale.estado == "SOLICITADO":
            puede_eliminarlo = True
        if fin_vale.autorizo_email == current_user.email and fin_vale.estado == "AUTORIZADO":
            puede_eliminarlo = True
        if not puede_eliminarlo:
            flash("No tiene permisos para eliminar o tiene un estado particular", "warning")
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
        puede_recuperarlo = False
        if current_user.can_admin(MODULO):
            puede_recuperarlo = True
        if fin_vale.usuario == current_user and fin_vale.estado == "CREADO":
            puede_recuperarlo = True
        if fin_vale.solicito_email == current_user.email and fin_vale.estado == "SOLICITADO":
            puede_recuperarlo = True
        if fin_vale.autorizo_email == current_user.email and fin_vale.estado == "AUTORIZADO":
            puede_recuperarlo = True
        if not puede_recuperarlo:
            flash("No tiene permisos para recuperar o tiene un estado particular", "warning")
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

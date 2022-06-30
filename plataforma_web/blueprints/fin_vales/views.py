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
from plataforma_web.blueprints.fin_vales.forms import FinValeForm, FinValeRequestTaskForm, FinValeAuthorizeTaskForm
from plataforma_web.blueprints.modulos.models import Modulo
from plataforma_web.blueprints.permisos.models import Permiso
from plataforma_web.blueprints.usuarios.decorators import permission_required

MODULO = "FIN VALES"

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
                "usuario_nombre": resultado.usuario.nombre,
                "tipo": resultado.tipo,
                "justificacion": resultado.justificacion,
                "monto": resultado.monto,
                "solicito_nombre": resultado.solicito_nombre,
                "estado": resultado.estado,
            }
        )
    # Entregar JSON
    return output_datatable_json(draw, total, data)


@fin_vales.route("/fin_vales")
def list_active():
    """Listado de Vales activos"""
    return render_template(
        "fin_vales/list.jinja2",
        filtros=json.dumps({"estatus": "A"}),
        titulo="Vales",
        estatus="A",
    )


@fin_vales.route("/fin_vales/inactivos")
@permission_required(MODULO, Permiso.MODIFICAR)
def list_inactive():
    """Listado de Vales inactivos"""
    return render_template(
        "fin_vales/list.jinja2",
        filtros=json.dumps({"estatus": "B"}),
        titulo="Vales inactivos",
        estatus="B",
    )


@fin_vales.route("/fin_vales/<int:fin_vale_id>")
def detail(fin_vale_id):
    """Detalle de un Vale"""
    fin_vale = FinVale.query.get_or_404(fin_vale_id)
    return render_template("fin_vales/detail.jinja2", fin_vale=fin_vale)


@fin_vales.route("/fin_vale/nuevo", methods=["GET", "POST"])
@permission_required(MODULO, Permiso.CREAR)
def new():
    """Nuevo Vale"""
    form = FinValeForm()
    if form.validate_on_submit():
        fin_vale = FinVale(
            usuario=current_user,
            autorizo_nombre=safe_string(form.autorizo_nombre.data),
            autorizo_puesto=safe_string(form.autorizo_puesto.data),
            autorizo_email=safe_email(form.autorizo_email.data),
            estado="PENDIENTE",
            justificacion=safe_string(form.justificacion.data, max_len=1020, to_uppercase=False, do_unidecode=False),
            monto=form.monto.data,
            tipo=form.tipo.data,
            solicito_nombre=safe_string(form.solicito_nombre.data),
            solicito_puesto=safe_string(form.solicito_puesto.data),
            solicito_email=safe_email(form.solicito_email.data),
        )
        fin_vale.save()
        bitacora = Bitacora(
            modulo=Modulo.query.filter_by(nombre=MODULO).first(),
            usuario=current_user,
            descripcion=safe_message(f"Nuevo Vale {fin_vale.justificacion}"),
            url=url_for("fin_vales.detail", fin_vale_id=fin_vale.id),
        )
        bitacora.save()
        flash(bitacora.descripcion, "success")
        return redirect(bitacora.url)
    form.usuario_nombre.data = current_user.nombre
    form.autorizo_nombre.data = "C.P. SILVIA GABRIELA SAUCEDO MUÑOZ"
    form.autorizo_puesto.data = "DIRECTORA DE RECURSOS FINANCIEROS DE LA OFICIALÍA MAYOR"
    form.autorizo_email.data = "silvia.saucedo@pjecz.gob.mx"
    form.justificacion.data = "Solicito un vale de gasolina de $100.00 (cien pesos 00/100 m.n), para NOMBRE COMPLETO con el objetivo de ir a DESTINO U OFICINA."
    form.monto.data = 100.00
    form.tipo.data = "GASOLINA"
    form.solicito_nombre.data = "ING. GUILERMO VALDES LOZANO"
    form.solicito_puesto.data = "DIRECTOR DE INFORMÁTICA"
    form.solicito_email.data = "guillermo.valdes@pjecz.gob.mx"
    return render_template("fin_vales/new.jinja2", form=form)


@fin_vales.route("/fin_vales/edicion/<int:fin_vale_id>", methods=["GET", "POST"])
@permission_required(MODULO, Permiso.MODIFICAR)
def edit(fin_vale_id):
    """Editar Vale"""
    fin_vale = FinVale.query.get_or_404(fin_vale_id)
    form = FinValeForm()
    if form.validate_on_submit():
        fin_vale.autorizo_nombre = safe_string(form.autorizo_nombre.data)
        fin_vale.autorizo_puesto = safe_string(form.autorizo_puesto.data)
        fin_vale.autorizo_email = safe_email(form.autorizo_email.data)
        fin_vale.tipo = form.tipo.data
        fin_vale.justificacion = safe_string(form.justificacion.data)
        fin_vale.monto = form.monto.data
        fin_vale.solicito_nombre = safe_string(form.solicito_nombre.data)
        fin_vale.solicito_puesto = safe_string(form.solicito_puesto.data)
        fin_vale.solicito_email = safe_string(form.solicito_email.data)
        fin_vale.save()
        bitacora = Bitacora(
            modulo=Modulo.query.filter_by(nombre=MODULO).first(),
            usuario=current_user,
            descripcion=safe_message(f"Editado Vale {fin_vale.justificacion}"),
            url=url_for("fin_vales.detail", fin_vale_id=fin_vale.id),
        )
        bitacora.save()
        flash(bitacora.descripcion, "success")
        return redirect(bitacora.url)
    form.usuario_nombre.data = current_user.nombre
    form.autorizo_nombre.data = fin_vale.autorizo_nombre
    form.autorizo_puesto.data = fin_vale.autorizo_puesto
    form.autorizo_email.data = fin_vale.autorizo_email
    form.tipo.data = fin_vale.tipo
    form.justificacion.data = fin_vale.justificacion
    form.monto.data = fin_vale.monto
    form.solicito_nombre.data = fin_vale.solicito_nombre
    form.solicito_puesto.data = fin_vale.solicito_puesto
    form.solicito_email.data = fin_vale.solicito_email
    return render_template("fin_vales/edit.jinja2", form=form, fin_vale=fin_vale)


@fin_vales.route("/fin_vales/solicitar/<int:fin_vale_id>", methods=["GET", "POST"])
@permission_required(MODULO, Permiso.MODIFICAR)
def request_task(fin_vale_id):
    """Solictar Vale"""
    # Consultar el vale
    fin_vale = FinVale.query.get_or_404(fin_vale_id)
    # Validar el vale
    if fin_vale.estatus != "A":
        flash("El vale esta eliminado", "danger")
        return redirect(url_for("fin_vales.detail", fin_vale_id=fin_vale_id))
    if fin_vale.estado != "PENDIENTE":
        flash("El vale NO esta en estado PENDIENTE", "danger")
        return redirect(url_for("fin_vales.detail", fin_vale_id=fin_vale_id))
    # Validar que current_user es quien va a solicitar el vale
    # Si viene el formulario
    form = FinValeRequestTaskForm()
    if form.validate_on_submit():
        # Crear la tarea en el fondo
        current_app.task_queue.enqueue(
            "plataforma_web.blueprints.fin_vales.tasks.solicitar",
            fin_vale_id=fin_vale.id,
            contrasena=form.contrasena.data,
        )
        flash("Tarea en el fondo lanzada para comunicarse con el motor de firma electrónica", "success")
        return redirect(url_for("fin_vales.detail", fin_vale_id=fin_vale_id))
    # Mostrar el formulario
    form.solicito_nombre.data = fin_vale.solicito_nombre
    form.usuario_nombre.data = fin_vale.usuario.nombre
    form.tipo.data = fin_vale.tipo
    form.justificacion.data = fin_vale.justificacion
    form.monto.data = fin_vale.monto
    return render_template("fin_vales/request_task.jinja2", fin_vale=fin_vale, form=form)


@fin_vales.route("/fin_vales/autorizar/<int:fin_vale_id>", methods=["GET", "POST"])
@permission_required(MODULO, Permiso.MODIFICAR)
def authorize_task(fin_vale_id):
    """Autorizar Vale"""
    fin_vale = FinVale.query.get_or_404(fin_vale_id)
    # Validar el vale
    if fin_vale.estatus != "A":
        flash("El vale esta eliminado", "danger")
        return redirect(url_for("fin_vales.detail", fin_vale_id=fin_vale_id))
    if fin_vale.estado != "SOLICITADO":
        flash("El vale NO esta en estado SOLICITADO", "danger")
        return redirect(url_for("fin_vales.detail", fin_vale_id=fin_vale_id))
    # Validar que current_user es quien va a autorizar el vale
    # Si viene el formulario
    form = FinValeAuthorizeTaskForm()
    if form.validate_on_submit():
        # Crear la tarea en el fondo
        current_app.task_queue.enqueue(
            "plataforma_web.blueprints.fin_vales.tasks.autorizar",
            fin_vale_id=fin_vale.id,
            contrasena=form.contrasena.data,
        )
        flash("Tarea en el fondo lanzada para comunicarse con el motor de firma electrónica", "success")
        return redirect(url_for("fin_vales.detail", fin_vale_id=fin_vale_id))
    # Mostrar el formulario
    form.autorizo_nombre.data = fin_vale.autorizo_nombre
    form.solicito_nombre.data = fin_vale.solicito_nombre
    form.usuario_nombre.data = fin_vale.usuario.nombre
    form.tipo.data = fin_vale.tipo
    form.justificacion.data = fin_vale.justificacion
    form.monto.data = fin_vale.monto
    return render_template("fin_vales/authorize_task.jinja2", fin_vale=fin_vale, form=form)


@fin_vales.route("/fin_vales/eliminar/<int:fin_vale_id>")
@permission_required(MODULO, Permiso.ADMINISTRAR)
def delete(fin_vale_id):
    """Eliminar Vale"""
    fin_vale = FinVale.query.get_or_404(fin_vale_id)
    if fin_vale.estatus == "A":
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
@permission_required(MODULO, Permiso.ADMINISTRAR)
def recover(fin_vale_id):
    """Recuperar Vale"""
    fin_vale = FinVale.query.get_or_404(fin_vale_id)
    if fin_vale.estatus == "B":
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

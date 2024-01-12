"""
Usuarios Solicitudes, vistas
"""
import json
from random import randint
from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from lib.datatables import get_datatable_parameters, output_datatable_json
from lib.safe_string import safe_string, safe_message, safe_email

from plataforma_web.blueprints.bitacoras.models import Bitacora
from plataforma_web.blueprints.modulos.models import Modulo
from plataforma_web.blueprints.permisos.models import Permiso
from plataforma_web.blueprints.usuarios.decorators import permission_required
from plataforma_web.blueprints.usuarios_solicitudes.models import UsuarioSolicitud
from plataforma_web.blueprints.usuarios.models import Usuario

from plataforma_web.blueprints.usuarios_solicitudes.forms import UsuarioSolicitudNewForm, UsuarioSolicitudValidateTokenEmailForm, UsuarioSolicitudValidateTokenTelefonoCelularForm

MODULO = "USUARIOS SOLICITUDES"

usuarios_solicitudes = Blueprint("usuarios_solicitudes", __name__, template_folder="templates")


@usuarios_solicitudes.before_request
@login_required
@permission_required(MODULO, Permiso.VER)
def before_request():
    """Permiso por defecto"""


@usuarios_solicitudes.route("/usuarios_solicitudes/datatable_json", methods=["GET", "POST"])
def datatable_json():
    """DataTable JSON para listado de Usuarios Solicitudes"""
    # Tomar parámetros de Datatables
    draw, start, rows_per_page = get_datatable_parameters()
    # Consultar
    consulta = UsuarioSolicitud.query
    if "estatus" in request.form:
        consulta = consulta.filter_by(estatus=request.form["estatus"])
    else:
        consulta = consulta.filter_by(estatus="A")
    if "usuario_id" in request.form:
        consulta = consulta.filter_by(usuario_id=request.form["usuario_id"])
    registros = consulta.order_by(UsuarioSolicitud.id).offset(start).limit(rows_per_page).all()
    total = consulta.count()
    # Elaborar datos para DataTable
    data = []
    for resultado in registros:
        data.append(
            {
                "detalle": {
                    "id": resultado.id,
                    "url": url_for("usuarios_solicitudes.detail", usuario_solicitud_id=resultado.id),
                },
                "usuario": {
                    "email": resultado.usuario.email,
                    "url": url_for("usuarios.detail", usuario_id=resultado.usuario_id) if current_user.can_view("USUARIOS") else "",
                },
                "usuario_nombre": resultado.usuario.nombre,
                "email_personal": {
                    "email": resultado.email_personal,
                    "valido": resultado.validacion_email,
                },
                "telefono_celular": {
                    "telefono_celular": resultado.telefono_celular,
                    "valido": resultado.validacion_telefono_celular,
                },
            }
        )
    # Entregar JSON
    return output_datatable_json(draw, total, data)


@usuarios_solicitudes.route("/usuarios_solicitudes")
def list_active():
    """Listado de Usuarios Solicitudes activos"""
    return render_template(
        "usuarios_solicitudes/list.jinja2",
        filtros=json.dumps({"estatus": "A"}),
        titulo="Usuarios Solicitudes",
        estatus="A",
    )


@usuarios_solicitudes.route("/usuarios_solicitudes/inactivos")
@permission_required(MODULO, Permiso.MODIFICAR)
def list_inactive():
    """Listado de Usuarios Solicitudes inactivos"""
    return render_template(
        "usuarios_solicitudes/list.jinja2",
        filtros=json.dumps({"estatus": "B"}),
        titulo="Usuarios Solicitudes inactivos",
        estatus="B",
    )


@usuarios_solicitudes.route("/usuarios_solicitudes/<int:usuario_solicitud_id>")
def detail(usuario_solicitud_id):
    """Detalle de un Usuario Solicitud"""
    usuario_solicitud = UsuarioSolicitud.query.get_or_404(usuario_solicitud_id)
    return render_template("usuarios_solicitudes/detail.jinja2", usuario_solicitud=usuario_solicitud)


@usuarios_solicitudes.route("/usuarios_solicitudes/nuevo/<int:usuario_id>", methods=["GET", "POST"])
@permission_required(MODULO, Permiso.CREAR)
def new(usuario_id):
    """Nuevo usuario solicitud"""
    usuario = Usuario.query.get_or_404(usuario_id)

    form = UsuarioSolicitudNewForm()
    if form.validate_on_submit():
        usuario_solicitud = UsuarioSolicitud(
            usuario=usuario,
            email_personal=safe_email(form.email_personal.data),
            telefono_celular=safe_string(form.telefono_celular.data),
            token_email=randint(100000, 999999),
            token_telefono_celular=randint(100000, 999999),
        )
        usuario_solicitud.save()
        bitacora = Bitacora(
            modulo=Modulo.query.filter_by(nombre=MODULO).first(),
            usuario=current_user,
            descripcion=safe_message(f"Nueva usuario solicitud {usuario_id}"),
            url=url_for("usuarios_solicitudes.detail", usuario_solicitud_id=usuario_solicitud.id),
        )
        bitacora.save()
        flash(bitacora.descripcion, "success")
        return redirect(bitacora.url)

    form.usuario_email.data = usuario.email
    form.usuario_nombre.data = usuario.nombre

    return render_template("usuarios_solicitudes/new.jinja2", form=form, usuario=usuario, usuario_id=usuario_id)


@usuarios_solicitudes.route("/usuarios_solicitudes/token_email/<int:usuario_solicitud_id>", methods=["GET", "POST"])
@permission_required(MODULO, Permiso.MODIFICAR)
def token_email(usuario_solicitud_id):
    """Validar el Token Email Personal"""
    usuario_solicitud = UsuarioSolicitud.query.get_or_404(usuario_solicitud_id)

    if usuario_solicitud.usuario != current_user and not current_user.can_admin(MODULO):
        flash("No puede acceder a la validación de email personal de otro usuario", "warning")
        return redirect(url_for("usuarios_solicitudes.detail", usuario_solicitud_id=usuario_solicitud.id))

    if usuario_solicitud.validacion_email is True:
        flash("Validación de E-mail ya hecha correctamente", "warning")
        return redirect(url_for("usuarios_solicitudes.detail", usuario_solicitud_id=usuario_solicitud.id))

    form = UsuarioSolicitudValidateTokenEmailForm()
    if form.validate_on_submit():
        if usuario_solicitud.usuario != current_user and not current_user.can_admin(MODULO):
            flash("No puede acceder a la validación de email personal de otro usuario", "warning")
            return redirect(url_for("usuarios_solicitudes.detail", usuario_solicitud_id=usuario_solicitud.id))

        if usuario_solicitud.validacion_email is False:
            if str(usuario_solicitud.token_email) == safe_string(form.token_email.data):
                usuario_solicitud.validacion_email = True
                usuario_solicitud.save()
                bitacora = Bitacora(
                    modulo=Modulo.query.filter_by(nombre=MODULO).first(),
                    usuario=current_user,
                    descripcion=safe_message(f"Token Email - Válido para la solicitud {usuario_solicitud.id}"),
                    url=url_for("usuarios_solicitudes.detail", usuario_solicitud_id=usuario_solicitud.id),
                )
                bitacora.save()
                flash(bitacora.descripcion, "success")
            else:
                usuario_solicitud.validacion_email = False
                usuario_solicitud.save()
                bitacora = Bitacora(
                    modulo=Modulo.query.filter_by(nombre=MODULO).first(),
                    usuario=current_user,
                    descripcion=safe_message(f"Token Email - Erróneo para la solicitud {usuario_solicitud.id}"),
                    url=url_for("usuarios_solicitudes.detail", usuario_solicitud_id=usuario_solicitud.id),
                )
                bitacora.save()
                flash(bitacora.descripcion, "danger")
            return redirect(bitacora.url)

    form.usuario_email.data = usuario_solicitud.usuario.email
    form.usuario_nombre.data = usuario_solicitud.usuario.nombre
    form.email_personal.data = usuario_solicitud.email_personal

    return render_template("usuarios_solicitudes/token_email.jinja2", form=form, usuario_solicitud=usuario_solicitud)


@usuarios_solicitudes.route("/usuarios_solicitudes/token_celular/<int:usuario_solicitud_id>", methods=["GET", "POST"])
@permission_required(MODULO, Permiso.MODIFICAR)
def token_celular(usuario_solicitud_id):
    """Validar el Token Teléfono Celular"""
    usuario_solicitud = UsuarioSolicitud.query.get_or_404(usuario_solicitud_id)

    if usuario_solicitud.usuario != current_user and not current_user.can_admin(MODULO):
        flash("No puede acceder a la validación del celular personal de otro usuario", "warning")
        return redirect(url_for("usuarios_solicitudes.detail", usuario_solicitud_id=usuario_solicitud.id))

    if usuario_solicitud.validacion_telefono_celular is True:
        flash("Validación de Teléfono Celular ya hecha correctamente", "warning")
        return redirect(url_for("usuarios_solicitudes.detail", usuario_solicitud_id=usuario_solicitud.id))

    form = UsuarioSolicitudValidateTokenTelefonoCelularForm()
    if form.validate_on_submit():
        if usuario_solicitud.usuario != current_user and not current_user.can_admin(MODULO):
            flash("No puede acceder a la validación del teléfono celular personal de otro usuario", "warning")
            return redirect(url_for("usuarios_solicitudes.detail", usuario_solicitud_id=usuario_solicitud.id))

        if usuario_solicitud.validacion_telefono_celular is False:
            if str(usuario_solicitud.token_telefono_celular) == safe_string(form.token_telefono_celular.data):
                usuario_solicitud.validacion_telefono_celular = True
                usuario_solicitud.save()
                bitacora = Bitacora(
                    modulo=Modulo.query.filter_by(nombre=MODULO).first(),
                    usuario=current_user,
                    descripcion=safe_message(f"Token Teléfono Celular - Válido para la solicitud {usuario_solicitud.id}"),
                    url=url_for("usuarios_solicitudes.detail", usuario_solicitud_id=usuario_solicitud.id),
                )
                bitacora.save()
                flash(bitacora.descripcion, "success")
            else:
                usuario_solicitud.validacion_telefono_celular = False
                usuario_solicitud.save()
                bitacora = Bitacora(
                    modulo=Modulo.query.filter_by(nombre=MODULO).first(),
                    usuario=current_user,
                    descripcion=safe_message(f"Token Teléfono Celular - Erróneo para la solicitud {usuario_solicitud.id}"),
                    url=url_for("usuarios_solicitudes.detail", usuario_solicitud_id=usuario_solicitud.id),
                )
                bitacora.save()
                flash(bitacora.descripcion, "danger")
            return redirect(bitacora.url)

    form.usuario_email.data = usuario_solicitud.usuario.email
    form.usuario_nombre.data = usuario_solicitud.usuario.nombre
    form.telefono_celular.data = usuario_solicitud.telefono_celular

    return render_template("usuarios_solicitudes/token_celular.jinja2", form=form, usuario_solicitud=usuario_solicitud)

"""
Usuarios Documentos, vistas
"""
import json
from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from lib.datatables import get_datatable_parameters, output_datatable_json
from lib.safe_string import safe_string, safe_message, safe_curp

from plataforma_web.blueprints.bitacoras.models import Bitacora
from plataforma_web.blueprints.modulos.models import Modulo
from plataforma_web.blueprints.permisos.models import Permiso
from plataforma_web.blueprints.usuarios.decorators import permission_required
from plataforma_web.blueprints.usuarios_datos.models import UsuarioDato

from plataforma_web.blueprints.usuarios_solicitudes.models import UsuarioSolicitud
from plataforma_web.blueprints.usuarios_datos.forms import (
    UsuarioDatoEditEstadoCivilForm,
    UsuarioDatoValidateForm,
)

MODULO = "USUARIOS DATOS"

CAMPOS = [
    "IDENTIFICACION",
    "CP FISCAL",
    "DOMICILIO",
    "ES MADRE",
    "ESTUDIOS",
    "ESTADO CIVIL",
    "TELEFONO",
    "EMAIL",
]

usuarios_datos = Blueprint("usuarios_datos", __name__, template_folder="templates")


@usuarios_datos.before_request
@login_required
@permission_required(MODULO, Permiso.VER)
def before_request():
    """Permiso por defecto"""


@usuarios_datos.route("/usuarios_datos/datatable_json", methods=["GET", "POST"])
@permission_required(MODULO, Permiso.ADMINISTRAR)
def datatable_json():
    """DataTable JSON para listado de Usuarios Datos"""
    # Tomar parámetros de Datatables
    draw, start, rows_per_page = get_datatable_parameters()
    # Consultar
    consulta = UsuarioDato.query
    if "estatus" in request.form:
        consulta = consulta.filter_by(estatus=request.form["estatus"])
    else:
        consulta = consulta.filter_by(estatus="A")
    registros = consulta.order_by(UsuarioDato.modificado.desc()).offset(start).limit(rows_per_page).all()
    total = consulta.count()
    # Elaborar datos para DataTable
    data = []
    for resultado in registros:
        data.append(
            {
                "detalle": {
                    "email": resultado.usuario.email,
                    "url": url_for("usuarios.detail", usuario_id=resultado.usuario.id),
                },
                "nombre": {
                    "nombre": resultado.usuario.nombre,
                    "url": url_for("usuarios_datos.detail", usuario_dato_id=resultado.id),
                },
                "curp": resultado.curp,
                "estado": resultado.estado_general,
            }
        )
    # Entregar JSON
    return output_datatable_json(draw, total, data)


@usuarios_datos.route("/usuarios_datos")
@permission_required(MODULO, Permiso.ADMINISTRAR)
def list_active():
    """Listado de Usuarios Datos activos"""
    return render_template(
        "usuarios_datos/list.jinja2",
        filtros=json.dumps({"estatus": "A"}),
        titulo="Usuarios Datos",
        estatus="A",
        estados=UsuarioDato.VALIDACIONES,
        campos=CAMPOS,
    )


@usuarios_datos.route("/usuarios_datos/inactivos")
@permission_required(MODULO, Permiso.ADMINISTRAR)
def list_inactive():
    """Listado de Usuarios Datos inactivos"""
    return render_template(
        "usuarios_datos/list.jinja2",
        filtros=json.dumps({"estatus": "B"}),
        titulo="Usuarios Datos inactivos",
        estatus="B",
        estados=UsuarioDato.VALIDACIONES,
        campos=CAMPOS,
    )


@usuarios_datos.route("/usuarios_datos/<int:usuario_dato_id>")
def detail(usuario_dato_id):
    """Detalle de un Usuario Datos"""
    usuario_dato = UsuarioDato.query.get_or_404(usuario_dato_id)
    if current_user == usuario_dato.usuario:
        return render_template("usuarios_datos/detail.jinja2", usuario_dato=usuario_dato)
    if current_user.can_admin(MODULO):
        return render_template("usuarios_datos/detail_admin.jinja2", usuario_dato=usuario_dato)
    return redirect(url_for("sistemas.start"))


@usuarios_datos.route("/usuarios_datos/nuevo", methods=["GET", "POST"])
@permission_required(MODULO, Permiso.CREAR)
def new():
    """Nuevo Usuario Datos vacío"""
    curp = None
    try:
        curp = safe_curp(current_user.curp)
    except ValueError:
        flash("CURP no válida, no puede ingresar a este módulo sin una CURP.", "warning")
        return redirect(url_for("sistemas.start"))
    # Buscar si el usuario ya tiene un registro previo
    usuario_dato = UsuarioDato.query.filter_by(curp=curp).first()
    # Si no cuenta con un registro previo, crear uno nuevo vacío
    if usuario_dato is None:
        usuario_dato = UsuarioDato(
            usuario=current_user,
            curp=current_user.curp,
        ).save()

        # Copiar teléfono y email personales de la tabla de usuarios_solicitudes
        usuario_solicitud = UsuarioSolicitud.query.filter_by(usuario=current_user).first()
        if usuario_solicitud:
            usuario_dato.telefono_personal = usuario_solicitud.telefono_celular
            usuario_dato.email_personal = usuario_solicitud.email_personal
            # Si ya están validados también copiar su validación
            if usuario_solicitud.validacion_telefono_celular is True:
                usuario_dato.estado_telefono = "VALIDO"
            elif usuario_solicitud.telefono_celular == "":
                usuario_dato.estado_telefono = "NO VALIDO"
            elif usuario_solicitud.telefono_celular != "":
                usuario_dato.estado_telefono = "POR VALIDAR"
            if usuario_solicitud.validacion_email is True:
                usuario_dato.estado_email = "VALIDO"
            elif usuario_solicitud.email_personal == "":
                usuario_dato.estado_email = "NO VALIDO"
            elif usuario_solicitud.email_personal != "":
                usuario_dato.estado_email = "POR VALIDAR"
        # Guardar registro
        usuario_dato.save()
    # Redirigirlo al detalle
    return redirect(url_for("usuarios_datos.detail", usuario_dato_id=usuario_dato.id))


@usuarios_datos.route("/usuarios_datos/editar/estado_civil/<int:usuario_dato_id>", methods=["GET", "POST"])
@permission_required(MODULO, Permiso.MODIFICAR)
def edit_estado_civil(usuario_dato_id):
    """Edición del estado civil"""
    usuario_dato = UsuarioDato.query.get_or_404(usuario_dato_id)
    form = UsuarioDatoEditEstadoCivilForm()
    if form.validate_on_submit():
        usuario_dato.estado_civil = form.estado_civil.data
        usuario_dato.estado_estado_civil = "POR VALIDAR"
        usuario_dato.save()
        flash("Ha modificado su estado civil correctamente, espere a que sea validado", "success")
        return redirect(url_for("usuarios_datos.detail", usuario_dato_id=usuario_dato.id))
    # Precargar datos anteriores
    form.estado_civil.data = usuario_dato.estado_civil
    return render_template("usuarios_datos/edit_estado_civil.jinja2", form=form, usuario_dato=usuario_dato)


@usuarios_datos.route("/usuarios_datos/validar/estado_civil/<int:usuario_dato_id>", methods=["GET", "POST"])
@permission_required(MODULO, Permiso.ADMINISTRAR)
def validate_estado_civil(usuario_dato_id):
    """Validación del estado civil"""
    usuario_dato = UsuarioDato.query.get_or_404(usuario_dato_id)
    form = UsuarioDatoValidateForm()
    if form.validate_on_submit():
        if form.valido.data:
            usuario_dato.estado_estado_civil = "VALIDO"
            usuario_dato.mensaje_estado_civil = None
            usuario_dato.save()
            flash("Ha validado el estado civil correctamente", "success")
        elif form.no_valido.data:
            mensaje = safe_message(form.mensaje.data, default_output_str=None)
            if mensaje is None:
                flash("Si rechaza esta información, por favor añada un mensaje dando una explicación", "warning")
                return render_template("usuarios_datos/validate_estado_civil.jinja2", form=form, usuario_dato=usuario_dato)
            else:
                usuario_dato.mensaje_estado_civil = mensaje
                usuario_dato.estado_estado_civil = "NO VALIDO"
                usuario_dato.save()
                flash("Ha rechazado el estado civil", "success")

        return redirect(url_for("usuarios_datos.detail", usuario_dato_id=usuario_dato.id))
    # Renderiza la página de validación
    return render_template("usuarios_datos/validate_estado_civil.jinja2", form=form, usuario_dato=usuario_dato)

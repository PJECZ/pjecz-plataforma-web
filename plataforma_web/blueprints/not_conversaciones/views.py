"""
Mensajes, vistas
"""
import json
import datetime

from flask import Blueprint, flash, redirect, render_template, url_for, request, abort
from flask_login import current_user, login_required
from sqlalchemy import or_

from lib.datatables import get_datatable_parameters, output_datatable_json
from lib.safe_string import safe_string
from plataforma_web.blueprints.usuarios.decorators import permission_required
from plataforma_web.extensions import db

from plataforma_web.blueprints.permisos.models import Permiso
from plataforma_web.blueprints.not_conversaciones.models import NotConversacion
from plataforma_web.blueprints.not_mensajes.models import NotMensaje
from plataforma_web.blueprints.not_conversaciones.forms import NotConversacionNewForm
from plataforma_web.blueprints.autoridades.models import Autoridad

MODULO = "NOT CONVERSACIONES"

# Roles que deben estar en la base de datos
ROL_NOTARIA = "NOTARIA"
ROL_JUZGADO = "JUZGADO PRIMERA INSTANCIA"
ROL_ADMIN = "ADMINISTRADOR"

not_conversaciones = Blueprint("not_conversaciones", __name__, template_folder="templates")


@not_conversaciones.before_request
@login_required
@permission_required(MODULO, Permiso.VER)
def before_request():
    """Permiso por defecto"""


@not_conversaciones.route("/not_conversaciones/conversaciones/datatable_json", methods=["GET", "POST"])
def datatable_json():
    """DataTable JSON para listado de Conversaciones"""
    # Tomar parámetros de Datatables
    draw, start, rows_per_page = get_datatable_parameters()
    # Query de consulta
    consulta = db.session.query(NotConversacion, NotMensaje, Autoridad)
    consulta = consulta.join(Autoridad, NotConversacion.destinatario_id == Autoridad.id)
    consulta = consulta.join(NotMensaje, NotConversacion.ultimo_mensaje_id == NotMensaje.id)
    # Lectura de parámetros filter para hacer la consulta
    if "estatus" in request.form:
        consulta = consulta.filter(NotConversacion.estatus == request.form["estatus"])
    else:
        consulta = consulta.filter(NotConversacion.estatus == "A")
    if "estado" in request.form:
        consulta = consulta.filter(NotConversacion.estado == request.form["estado"])
    if "admin" not in request.form:
        consulta = consulta.filter(or_(NotConversacion.autor == current_user.autoridad, NotConversacion.destinatario_id == current_user.autoridad.id))
    # Ejecución de la consulta estableciendo el ordenamiento.
    registros = consulta.order_by(NotConversacion.modificado.desc()).order_by(NotConversacion.leido.desc()).offset(start).limit(rows_per_page).all()
    total = consulta.count()
    # Elaborar datos para DataTable
    data = []
    for resultado in registros:
        # definir la contraparte de la autoridad de la conversación
        if resultado.NotConversacion.autor_id == current_user.autoridad.id:
            clave = resultado.Autoridad.clave
            url_id = resultado.NotConversacion.destinatario_id
            descripcion = resultado.Autoridad.descripcion_corta + " - " + resultado.Autoridad.distrito.nombre_corto
        else:
            clave = resultado.NotConversacion.autor.clave
            url_id = resultado.NotConversacion.autor_id
            descripcion = resultado.NotConversacion.autor.descripcion_corta + " - " + resultado.NotConversacion.autor.distrito.nombre_corto
        # Añadir registros al listado
        data.append(
            {
                "id": {
                    "id": resultado.NotConversacion.id,
                    "url": url_for("not_conversaciones.detail", conversacion_id=resultado.NotConversacion.id),
                },
                "detalle": {
                    "clave": clave,
                    "url": url_for("autoridades.detail", autoridad_id=url_id),
                    "descripcion": descripcion,
                },
                "lectura": True if current_user.autoridad_id == resultado.NotMensaje.autoridad_id else resultado.NotConversacion.leido,
                "fecha_hora": resultado.NotConversacion.modificado.strftime("%Y/%m/%d %H:%M"),
                "mensaje": {
                    "mensaje": resultado.NotMensaje.contenido,
                    "url": url_for("not_conversaciones.detail", conversacion_id=resultado.NotConversacion.id),
                },
                "autor": {
                    "clave": resultado.NotConversacion.autor.clave,
                    "url": url_for("autoridades.detail", autoridad_id=resultado.NotConversacion.autor_id),
                    "descripcion": resultado.NotConversacion.autor.descripcion_corta + " - " + resultado.NotConversacion.autor.distrito.nombre_corto,
                },
                "destinatario": {
                    "clave": resultado.Autoridad.clave,
                    "url": url_for("autoridades.detail", autoridad_id=resultado.NotConversacion.destinatario_id),
                    "descripcion": resultado.Autoridad.descripcion_corta + " - " + resultado.Autoridad.distrito.nombre_corto,
                },
            }
        )
    # Entregar JSON
    return output_datatable_json(draw, total, data)


def _identifica_rol():
    """Identifica el rol del usuario actual (current_user)"""
    rol = None
    # Consultar los roles del usuario
    current_user_roles = current_user.get_roles()
    if ROL_NOTARIA in current_user_roles:
        rol = ROL_NOTARIA
    elif ROL_JUZGADO in current_user_roles:
        rol = ROL_JUZGADO
    elif current_user.can_admin(MODULO):
        return ROL_ADMIN
    # si no tiene ninguno de los dos posibles roles, abortamos
    if rol is None:
        abort(403)
    # Verificamos que tenga una autoridad asignada, porque sino se perdería el rastreo
    if rol == ROL_NOTARIA and current_user.autoridad.es_notaria:
        rol = ROL_NOTARIA
    elif rol == ROL_JUZGADO and current_user.autoridad.es_jurisdiccional:
        rol = ROL_JUZGADO
    else:
        abort(403)
    return rol


@not_conversaciones.route("/not_conversaciones")
def list_active():
    """Listado de Conversaciones Activas"""
    if current_user.can_admin(MODULO):
        return render_template(
            "not_conversaciones/list_admin.jinja2",
            filtros=json.dumps({"estatus": "A", "estado": "ACTIVO", "admin": True}),
            titulo="Conversaciones",
            mostrar_btn_nueva_conversacion=False,
            mostrar_btn_activas=False,
            mostrar_btn_archivadas=True,
            estatus="A",
        )

    # Identificamos el rol del current_user
    _identifica_rol()

    # Crea el html final
    return render_template(
        "not_conversaciones/list.jinja2",
        filtros=json.dumps({"estatus": "A", "estado": "ACTIVO"}),
        titulo="Conversaciones",
        mostrar_btn_nueva_conversacion=True,
        mostrar_btn_activas=False,
        mostrar_btn_archivadas=True,
        estatus="A",
    )


@not_conversaciones.route("/not_conversaciones/archivadas")
def list_archive():
    """Listado de Conversaciones Archivadas"""
    if current_user.can_admin(MODULO):
        return render_template(
            "not_conversaciones/list_admin.jinja2",
            filtros=json.dumps({"estatus": "A", "estado": "ARCHIVADO", "admin": True}),
            titulo="Conversaciones Archivadas",
            mostrar_btn_nueva_conversacion=False,
            mostrar_btn_activas=True,
            mostrar_btn_archivadas=False,
            estatus="A",
        )

    # Identificamos el rol del current_user
    _identifica_rol()

    # Crea el html final
    return render_template(
        "not_conversaciones/list.jinja2",
        filtros=json.dumps({"estatus": "A", "estado": "ARCHIVADO"}),
        titulo="Conversaciones Archivadas",
        mostrar_btn_nueva_conversacion=False,
        mostrar_btn_activas=True,
        mostrar_btn_archivadas=False,
        estatus="A",
    )


@not_conversaciones.route("/not_conversaciones/<int:conversacion_id>")
def detail(conversacion_id):
    """Detalle de una Conversación"""
    conversacion = NotConversacion.query.get_or_404(conversacion_id)
    destinatario = Autoridad.query.get_or_404(conversacion.destinatario_id)
    if current_user.can_admin(MODULO) is False:
        if conversacion.autor_id != current_user.autoridad_id and conversacion.destinatario_id != current_user.autoridad_id:
            flash("No tiene persmisos para ver esta conversación", "danger")
            return redirect(url_for("not_conversaciones.list_active"))
    if conversacion.leido is False:
        ultimo_mensaje = NotMensaje.query.get_or_404(conversacion.ultimo_mensaje_id)
        if ultimo_mensaje.autoridad_id != current_user.autoridad_id:
            ultimo_mensaje.leido = True
            ultimo_mensaje.save()
            conversacion.leido = True
            conversacion.save()
    mensajes = NotMensaje.query.filter_by(estatus="A").filter_by(not_conversacion=conversacion).order_by(NotMensaje.creado).all()

    # Arreglo para mostrar los mensajes agrupados por fechas
    fecha_mensaje_anterior = None
    fechas = {}
    # Recorremos los mensajes para agruparlos por fechas
    for mensaje in mensajes:
        if fecha_mensaje_anterior is None:
            fecha_mensaje_anterior = mensaje.creado.strftime("%Y/%m/%d")
            fechas[mensaje] = mensaje.creado.strftime("%Y/%m/%d")
        else:
            if fecha_mensaje_anterior == mensaje.creado.strftime("%Y/%m/%d"):
                fechas[mensaje] = None
            else:
                fechas[mensaje] = mensaje.creado.strftime("%Y/%m/%d")
                fecha_mensaje_anterior = mensaje.creado.strftime("%Y/%m/%d")
        if fechas[mensaje] == datetime.date.today().strftime("%Y/%m/%d"):
            fechas[mensaje] = "Hoy"
        elif fechas[mensaje] == (datetime.date.today() - datetime.timedelta(days=1)).strftime("%Y/%m/%d"):
            fechas[mensaje] = "Ayer"

    # Mostrar el botón de Archivar solo a los Juzgados
    mostrar_btn_archivar = False
    # Identificamos el rol del current_user
    rol = _identifica_rol()
    if rol == ROL_JUZGADO:
        mostrar_btn_archivar = True

    # Crea el html final
    return render_template(
        "not_conversaciones/detail.jinja2",
        conversacion=conversacion,
        destinatario=destinatario,
        titulo="Conversación - ID: " + str(conversacion.id),
        mostrar_btn_archivar=mostrar_btn_archivar,
        mensajes=mensajes,
        fechas=fechas,
    )


@not_conversaciones.route("/not_conversaciones/nueva", methods=["GET", "POST"])
@permission_required(MODULO, Permiso.CREAR)
def new():
    """Nueva Conversación"""
    form = NotConversacionNewForm()
    if form.validate_on_submit():
        destinatario = Autoridad.query.get_or_404(form.destinatario.data)
        if destinatario is None:
            flash("El destinatario seleccionado no existe", "warning")
        else:
            conversacion = NotConversacion(
                autor=current_user.autoridad,
                destinatario_id=int(form.destinatario.data),
                leido=False,
                estado="ACTIVO",
                ultimo_mensaje_id=0,
            )
            conversacion.save()
            mensaje = NotMensaje(
                autoridad=current_user.autoridad,
                not_conversacion=conversacion,
                contenido=safe_string(form.mensaje.data),
                leido=False,
            )
            mensaje.save()
            conversacion.ultimo_mensaje_id = mensaje.id
            conversacion.save()
            flash("Conversacion creada correctamente.", "success")
            return redirect(url_for("not_conversaciones.list_active"))
    form.autor.data = current_user.nombre
    buscar = None
    # Identificamos el rol del current_user
    rol = _identifica_rol()
    if rol == ROL_NOTARIA:
        buscar = "JUZGADO"
    elif rol == ROL_JUZGADO:
        buscar = "NOTARIA"
    return render_template("not_conversaciones/new.jinja2", buscar=buscar, form=form)


@not_conversaciones.route("/not_conversaciones/nuevo_mensaje/<int:conversacion_id>", methods=["GET", "POST"])
@permission_required(MODULO, Permiso.CREAR)
def new_message(conversacion_id):
    """Nuevo Mensaje"""
    contenido = safe_string(request.form["contenido"])
    if contenido:
        conversacion = NotConversacion.query.get_or_404(conversacion_id)
        if conversacion.autor_id != current_user.autoridad.id and conversacion.destinatario_id != current_user.autoridad.id:
            flash("No tiene permitido escribir en esta conversación", "danger")
            return redirect(url_for("not_conversaciones.list_active"))
        elif conversacion.estado != "ACTIVO":
            flash("Esta conversación no está activa", "warning")
            return redirect(url_for("not_conversaciones.list_active"))
        else:
            mensaje = NotMensaje(
                autoridad=current_user.autoridad,
                not_conversacion=conversacion,
                contenido=contenido,
                leido=False,
            )
            mensaje.save()
            conversacion.leido = False
            conversacion.ultimo_mensaje_id = mensaje.id
            conversacion.save()
    else:
        flash("Escriba algo en el mensaje", "warning")
    return redirect(url_for("not_conversaciones.detail", conversacion_id=conversacion_id))


@not_conversaciones.route("/not_conversaciones/archivar/<int:conversacion_id>")
@permission_required(MODULO, Permiso.MODIFICAR)
def archive(conversacion_id):
    """Archivar conversación"""
    # Identificamos el rol del current_user
    rol = _identifica_rol()
    conversacion = NotConversacion.query.get_or_404(conversacion_id)
    # Solo los juzgados pueden archivar conversaciones, además deben formar parte de la conversación
    if (rol == ROL_JUZGADO) and (conversacion.autor_id == current_user.autoridad.id or conversacion.destinatario_id == current_user.autoridad.id):
        conversacion.leido = True
        conversacion.estado = "ARCHIVADO"
        conversacion.save()
        flash("Conversación Archivada correctamente.", "success")
        return redirect(url_for("not_conversaciones.list_active"))
    flash("No tiene permitido Archivar esta conversación", "danger")
    return redirect(url_for("not_conversaciones.list_active"))

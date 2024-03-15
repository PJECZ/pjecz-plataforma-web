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
from plataforma_web.blueprints.usuarios.decorators import anonymous_required, permission_required
from plataforma_web.blueprints.usuarios_solicitudes.models import UsuarioSolicitud
from plataforma_web.blueprints.usuarios.models import Usuario

from plataforma_web.blueprints.usuarios_solicitudes.forms import UsuarioSolicitudNewForm, UsuarioSolicitudValidateTokenEmailForm, UsuarioSolicitudValidateTokenTelefonoCelularForm

MODULO = "USUARIOS SOLICITUDES"
VALIDACION_MAX_INTENTOS = 5

usuarios_solicitudes = Blueprint("usuarios_solicitudes", __name__, template_folder="templates")


@usuarios_solicitudes.route("/usuarios_solicitudes/token_celular/public/<id_hashed>", methods=["GET", "POST"])
def token_celular_without_session(id_hashed):
    """Validar el Token Teléfono Celular"""

    # Descifrar el id_hashed
    usuario_solicitud_id = UsuarioSolicitud.decode_id(id_hashed)

    # Si el id_hashed no es válido, mostrar mensaje de error
    if usuario_solicitud_id is None:
        return render_template(
            "usuarios_solicitudes/token_celular_message.jinja2",
            mensaje="El enlace no es válido. Por favor, solicite una nueva validación.",
        )

    # Consultamos la solicitud usuario_solicitud recibida
    usuario_solicitud = UsuarioSolicitud.query.get_or_404(usuario_solicitud_id)

    # Si el usuario que consulta no es el usuario de la solicitud, se muestra la pagina con el mesaje
    if usuario_solicitud.estatus != "A":
        return render_template(
            "usuarios_solicitudes/token_celular_message.jinja2",
            mensaje="Esta solicitud ya se vencio porque tiene mas de 24 horas. Si lo necesita haga una nueva.",
        )

    # Si ya fue validado, se muestra la pagina con el mesaje
    if usuario_solicitud.validacion_telefono_celular is True:
        return render_template(
            "usuarios_solicitudes/token_celular_message.jinja2",
            mensaje="Esta solicitud ya fue validada. Nada por hacer.",
        )

    # Si el número de intentos es igual o mayor a VALIDACION_MAX_INTENTOS, se muestra la pagina con el mesaje
    if usuario_solicitud.intentos_telefono_celular >= VALIDACION_MAX_INTENTOS:
        return render_template(
            "usuarios_solicitudes/token_celular_message.jinja2",
            mensaje="Ha superado el número de intentos para validar. Deje pasar 24 horas y haga otra solicitud.",
        )

    # Procesar el formulario de envío
    form = UsuarioSolicitudValidateTokenTelefonoCelularForm()
    if form.validate_on_submit():
        # Tomar al usuario para actualizar su telefono celular personal mas adelante
        usuario = usuario_solicitud.usuario

        # Comprobar que el token sea el mismo que se recibe
        if str(usuario_solicitud.token_telefono_celular) == safe_string(form.token_telefono_celular.data):
            # Actualizar en la solicitud el estatus de validacion_telefono_celular a True
            usuario_solicitud.validacion_telefono_celular = True
            usuario_solicitud.save()

            # Actualizar en el usuario el telefono_celular
            usuario.telefono_celular = usuario_solicitud.telefono_celular
            usuario.save()

            # Agregar a la bitácora
            bitacora = Bitacora(
                modulo=Modulo.query.filter_by(nombre=MODULO).first(),
                usuario=usuario,
                descripcion=safe_message(f"El usuario {usuario.email} ha validado su teléfono celular personal {usuario_solicitud.telefono_celular}"),
                url=url_for("usuarios_solicitudes.detail", usuario_solicitud_id=usuario_solicitud.id),
            )
            bitacora.save()

            # Mostrar el mensaje de que ha validado con éxito
            return render_template(
                "usuarios_solicitudes/token_celular_message.jinja2",
                mensaje=f"Ha validado con éxito su teléfono celular personal {usuario_solicitud.telefono_celular}",
            )

        # El token recibido NO es el mismo que se tiene en la BD, incrementar el numero de intentos
        usuario_solicitud.intentos_telefono_celular += 1
        usuario_solicitud.save()

        # Mostrar mensaje de que el token es incorrecto
        return render_template(
            "usuarios_solicitudes/token_celular_message.jinja2",
            mensaje=f"El token es INCORRECTO. Intento {usuario_solicitud.intentos_telefono_celular} de {VALIDACION_MAX_INTENTOS}",
        )

    # Cargar valores en los campos de solo lectura del formulario
    form.usuario_email.data = usuario_solicitud.usuario.email
    form.usuario_nombre.data = usuario_solicitud.usuario.nombre
    form.telefono_celular.data = usuario_solicitud.telefono_celular

    # Mostramos el formulario
    return render_template(
        "usuarios_solicitudes/token_celular.jinja2",
        form=form,
        usuario_solicitud=usuario_solicitud,
    )


@usuarios_solicitudes.route("/usuarios_solicitudes/token_celular/<id_hashed>", methods=["GET", "POST"])
def token_celular_with_session(id_hashed):
    """Validar el Token Teléfono Celular"""

    # Si no esta logeado, enviarlo a la ruta publica del token
    if not current_user.is_authenticated:
        return token_celular_without_session(id_hashed)

    # Descifrar el id_hashed
    usuario_solicitud_id = UsuarioSolicitud.decode_id(id_hashed)

    # Si el id_hashed no es válido, mostrar mensaje de error
    if usuario_solicitud_id is None:
        flash("El enlace no es válido. Por favor, solicite una nueva validación.", "warning")
        return redirect(url_for("sistemas.start"))

    # Consultamos la solicitud usuario_solicitud recibida
    usuario_solicitud = UsuarioSolicitud.query.get_or_404(usuario_solicitud_id)

    # Si el usuario que consulta no es el usuario de la solicitud, se muestra la pagina con el mesaje
    if usuario_solicitud.estatus != "A":
        flash("Esta solicitud ya se venció porque tiene mas de 24 horas. Si lo necesita haga una nueva.", "warning")
        return redirect(url_for("sistemas.start"))

    # Si ya fue validado, se muestra la pagina con el mesaje
    if usuario_solicitud.validacion_telefono_celular is True:
        flash("Esta solicitud ya fue validada. Nada por hacer.", "warning")
        return redirect(url_for("sistemas.start"))

    # Si el número de intentos es igual o mayor a VALIDACION_MAX_INTENTOS, se muestra la pagina con el mesaje
    if usuario_solicitud.intentos_telefono_celular >= VALIDACION_MAX_INTENTOS:
        flash("Ha superado el número de intentos para validar. Deje pasar 24 horas y haga otra solicitud.", "warning")
        return redirect(url_for("sistemas.start"))

    # Procesar el formulario de envío
    form = UsuarioSolicitudValidateTokenTelefonoCelularForm()
    if form.validate_on_submit():
        # Tomar al usuario para actualizar su telefono celular personal mas adelante
        usuario = usuario_solicitud.usuario

        # Comprobar que el token sea el mismo que se recibe
        if str(usuario_solicitud.token_telefono_celular) == safe_string(form.token_telefono_celular.data):
            # Actualizar en la solicitud el estatus de validacion_telefono_celular a True
            usuario_solicitud.validacion_telefono_celular = True
            usuario_solicitud.save()

            # Actualizar en el usuario el telefono_celular
            usuario.telefono_celular = usuario_solicitud.telefono_celular
            usuario.save()

            # Agregar a la bitácora
            bitacora = Bitacora(
                modulo=Modulo.query.filter_by(nombre=MODULO).first(),
                usuario=usuario,
                descripcion=safe_message(f"El usuario {usuario.email} ha validado su teléfono celular personal {usuario_solicitud.telefono_celular}"),
                url=url_for("usuarios_solicitudes.detail", usuario_solicitud_id=usuario_solicitud.id),
            )
            bitacora.save()

            # Mostrar el mensaje de que ha validado con éxito
            flash(f"Ha validado con éxito su teléfono celular personal {usuario_solicitud.email_personal}.", "success")
            return redirect(url_for("sistemas.start"))

        # El token recibido NO es el mismo que se tiene en la BD, incrementar el numero de intentos
        usuario_solicitud.intentos_telefono_celular += 1
        usuario_solicitud.save()

        # Mostrar mensaje de que el token es incorrecto
        flash(f"El token es INCORRECTO. Intento {usuario_solicitud.intentos_telefono_celular} de {VALIDACION_MAX_INTENTOS}.", "danger")
        return redirect(url_for("sistemas.start"))

    # Cargar valores en los campos de solo lectura del formulario
    form.usuario_email.data = usuario_solicitud.usuario.email
    form.usuario_nombre.data = usuario_solicitud.usuario.nombre
    form.telefono_celular.data = usuario_solicitud.telefono_celular

    # Mostramos el formulario
    return render_template(
        "usuarios_solicitudes/token_celular_active.jinja2",
        form=form,
        usuario_solicitud=usuario_solicitud,
    )

@usuarios_solicitudes.route("/usuarios_solicitudes/token_email/public/<id_hashed>", methods=["GET", "POST"])
def token_email_without_session(id_hashed):
    """Validar el Token Email Personal"""

    # Descifrar el id_hashed
    usuario_solicitud_id = UsuarioSolicitud.decode_id(id_hashed)

    # Si el id_hashed no es válido, mostrar mensaje de error
    if usuario_solicitud_id is None:
        return render_template(
            "usuarios_solicitudes/token_email_message.jinja2",
            mensaje="El enlace no es válido. Por favor, solicite una nueva validación.",
        )

    # Consultamos la solicitud usuario_solicitud recibida
    usuario_solicitud = UsuarioSolicitud.query.get_or_404(usuario_solicitud_id)

    # Si el usuario que consulta no es el usuario de la solicitud, se muestra la pagina con el mesaje
    if usuario_solicitud.estatus != "A":
        return render_template(
            "usuarios_solicitudes/token_email_message.jinja2",
            mensaje="Esta solicitud ya se vencio porque tiene mas de 24 horas. Si lo necesita haga una nueva.",
        )

    # Si ya fue validado, se muestra la pagina con el mesaje
    if usuario_solicitud.validacion_email is True:
        return render_template(
            "usuarios_solicitudes/token_email_message.jinja2",
            mensaje="Esta solicitud ya fue validada. Nada por hacer.",
        )

    # Si el número de intentos es igual o mayor a VALIDACION_MAX_INTENTOS, se muestra la pagina con el mesaje
    if usuario_solicitud.intentos_email >= VALIDACION_MAX_INTENTOS:
        return render_template(
            "usuarios_solicitudes/token_email_message.jinja2",
            mensaje="Ha superado el número de intentos para validar. Deje pasar 24 horas y haga otra solicitud.",
        )

    # Procesar el formulario de envío
    form = UsuarioSolicitudValidateTokenEmailForm()
    if form.validate_on_submit():
        # Tomar al usuario para actualizar su email personal mas adelante
        usuario = usuario_solicitud.usuario

        # Comprobar que el token sea el mismo que se recibe
        if str(usuario_solicitud.token_email) == safe_string(form.token_email.data):
            # Actualizar en la solicitud el estatus de validacion_email a True
            usuario_solicitud.validacion_email = True
            usuario_solicitud.save()

            # Actualizar en el usuario el email_personal
            usuario.email_personal = safe_email(usuario_solicitud.email_personal)
            usuario.save()

            # Agregar a la bitácora
            bitacora = Bitacora(
                modulo=Modulo.query.filter_by(nombre=MODULO).first(),
                usuario=usuario,
                descripcion=safe_message(f"El usuario {usuario.email} ha validado su correo electronico personal {usuario_solicitud.email_personal}"),
                url=url_for("usuarios_solicitudes.detail", usuario_solicitud_id=usuario_solicitud.id),
            )
            bitacora.save()

            # Mostrar el mensaje de que ha validado con éxito
            return render_template(
                "usuarios_solicitudes/token_email_message.jinja2",
                mensaje=f"Ha validado con éxito su correo electrónico personal {usuario_solicitud.email_personal}",
            )

        # El token recibido NO es el mismo que se tiene en la BD, incrementar el numero de intentos
        usuario_solicitud.intentos_email += 1
        usuario_solicitud.save()

        # Mostrar mensaje de que el token es incorrecto
        return render_template(
            "usuarios_solicitudes/token_email_message.jinja2",
            mensaje=f"El token es INCORRECTO. Intento {usuario_solicitud.intentos_email} de {VALIDACION_MAX_INTENTOS}",
        )

    # Cargar valores en los campos de solo lectura del formulario
    form.usuario_email.data = usuario_solicitud.usuario.email
    form.usuario_nombre.data = usuario_solicitud.usuario.nombre
    form.email_personal.data = usuario_solicitud.email_personal

    # Mostramos el formulario
    return render_template(
        "usuarios_solicitudes/token_email.jinja2",
        form=form,
        usuario_solicitud=usuario_solicitud,
    )


@usuarios_solicitudes.route("/usuarios_solicitudes/token_email/<id_hashed>", methods=["GET", "POST"])
def token_email_with_session(id_hashed):
    """Validar el Token Email Personal con sesion iniciada"""

    # Si no esta logeado, enviarlo a la ruta publica del token
    if not current_user.is_authenticated:
        return token_email_without_session(id_hashed)

    # Descifrar el id_hashed
    usuario_solicitud_id = UsuarioSolicitud.decode_id(id_hashed)

    # Si el id_hashed no es válido, mostrar mensaje de error
    if usuario_solicitud_id is None:
        flash("El enlace no es válido. Por favor, solicite una nueva validación.", "warning")
        return redirect(url_for("sistemas.start"))

    # Consultamos la solicitud usuario_solicitud recibida
    usuario_solicitud = UsuarioSolicitud.query.get_or_404(usuario_solicitud_id)

    # Si el usuario que consulta no es el usuario de la solicitud, se muestra la pagina con el mesaje
    if usuario_solicitud.estatus != "A":
        flash("Esta solicitud ya se venció porque tiene mas de 24 horas. Si lo necesita haga una nueva.", "warning")
        return redirect(url_for("sistemas.start"))

    # Si ya fue validado, se muestra la pagina con el mesaje
    if usuario_solicitud.validacion_email is True:
        flash("Esta solicitud ya fue validada. Nada por hacer.", "warning")
        return redirect(url_for("sistemas.start"))


    # Si el número de intentos es igual o mayor a VALIDACION_MAX_INTENTOS, se muestra la pagina con el mesaje
    if usuario_solicitud.intentos_email >= VALIDACION_MAX_INTENTOS:
        flash("Ha superado el número de intentos para validar. Deje pasar 24 horas y haga otra solicitud.", "warning")
        return redirect(url_for("sistemas.start"))
    
    # Procesar el formulario de envío
    form = UsuarioSolicitudValidateTokenEmailForm()
    if form.validate_on_submit():
        # Tomar al usuario para actualizar su email personal mas adelante
        usuario = usuario_solicitud.usuario

        # Comprobar que el token sea el mismo que se recibe
        if str(usuario_solicitud.token_email) == safe_string(form.token_email.data):
            # Actualizar en la solicitud el estatus de validacion_email a True
            usuario_solicitud.validacion_email = True
            usuario_solicitud.save()

            # Actualizar en el usuario el email_personal
            usuario.email_personal = safe_email(usuario_solicitud.email_personal)
            usuario.save()

            # Agregar a la bitácora
            bitacora = Bitacora(
                modulo=Modulo.query.filter_by(nombre=MODULO).first(),
                usuario=usuario,
                descripcion=safe_message(f"El usuario {usuario.email} ha validado su correo electronico personal {usuario_solicitud.email_personal}"),
                url=url_for("usuarios_solicitudes.detail", usuario_solicitud_id=usuario_solicitud.id),
            )
            bitacora.save()

            # Mostrar el mensaje de que ha validado con éxito
            flash(f"Ha validado con éxito su correo electrónico personal {usuario_solicitud.email_personal}.", "success")
            return redirect(url_for("sistemas.start"))

        # El token recibido NO es el mismo que se tiene en la BD, incrementar el numero de intentos
        usuario_solicitud.intentos_email += 1
        usuario_solicitud.save()

        # Mostrar mensaje de que el token es incorrecto
        flash(f"El token es INCORRECTO. Intento {usuario_solicitud.intentos_email} de {VALIDACION_MAX_INTENTOS}.", "danger")
        return redirect(url_for("sistemas.start"))

    # Cargar valores en los campos de solo lectura del formulario
    form.usuario_email.data = usuario_solicitud.usuario.email
    form.usuario_nombre.data = usuario_solicitud.usuario.nombre
    form.email_personal.data = usuario_solicitud.email_personal

    # Mostramos el formulario
    return render_template(
        "usuarios_solicitudes/token_email_session_active.jinja2",
        form=form,
        usuario_solicitud=usuario_solicitud,
    )


@usuarios_solicitudes.route("/usuarios_solicitudes/datatable_json", methods=["GET", "POST"])
@login_required
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
    registros = consulta.order_by(UsuarioSolicitud.id.desc()).offset(start).limit(rows_per_page).all()
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
@login_required
@permission_required(MODULO, Permiso.ADMINISTRAR)
def list_active():
    """Listado de Usuarios Solicitudes activos"""
    return render_template(
        "usuarios_solicitudes/list.jinja2",
        filtros=json.dumps({"estatus": "A"}),
        titulo="Usuarios Solicitudes",
        estatus="A",
    )


@usuarios_solicitudes.route("/usuarios_solicitudes/inactivos")
@login_required
@permission_required(MODULO, Permiso.ADMINISTRAR)
def list_inactive():
    """Listado de Usuarios Solicitudes inactivos"""
    return render_template(
        "usuarios_solicitudes/list.jinja2",
        filtros=json.dumps({"estatus": "B"}),
        titulo="Usuarios Solicitudes inactivos",
        estatus="B",
    )


@usuarios_solicitudes.route("/usuarios_solicitudes/<int:usuario_solicitud_id>")
@login_required
@permission_required(MODULO, Permiso.ADMINISTRAR)
def detail(usuario_solicitud_id):
    """Detalle de un Usuario Solicitud"""
    usuario_solicitud = UsuarioSolicitud.query.get_or_404(usuario_solicitud_id)
    return render_template("usuarios_solicitudes/detail.jinja2", usuario_solicitud=usuario_solicitud)


@usuarios_solicitudes.route("/usuarios_solicitudes/nuevo", methods=["GET", "POST"])
@login_required
@permission_required(MODULO, Permiso.CREAR)
def new():
    """Nuevo usuario solicitud"""

    # Si el usuario ya tiene una solicitud activa, redirigir a la pagina message
    if UsuarioSolicitud.query.filter_by(usuario_id=current_user.id).filter_by(estatus="A").first():
        return render_template(
            "usuarios_solicitudes/message.jinja2",
            usuario=current_user,
            mensaje="Ya tienes una solicitud en progreso.<br/>Revisa tu correo electrónico personal, te enviamos un mensaje con un token para validar.",
            btn_texto="Ir al Inicio",
            btn_enlace=url_for("sistemas.start"),
        )

    # Si viene el formulario
    form = UsuarioSolicitudNewForm()
    if form.validate_on_submit():
        # Validar el correo electronico personal
        es_valido = True
        email_personal = None
        try:
            email_personal = safe_email(form.email_personal.data)
        except ValueError:
            flash(f"El correo {email_personal} no es válido.", "warning")
            es_valido = False
        if email_personal.endswith("@pjecz.gob.mx") or email_personal.endswith("@coahuila.gob.mx"):
            flash("Su correo electrónico personal NO debe ser @pjecz.gob.mx o @coahuila.gob.mx", "warning")
            es_valido = False

        # Si es valido, guardar la solicitud y enviar el mensaje para validación
        if es_valido:
            # Guardar la solicitud, creando un token para el email personal y el telefono celular
            usuario_solicitud = UsuarioSolicitud(
                usuario=current_user,
                email_personal=email_personal,
                telefono_celular=safe_string(form.telefono_celular.data),
                token_email=randint(100000, 999999),
                token_telefono_celular=randint(100000, 999999),
                intentos_email=0,
                intentos_telefono_celular=0,
            )
            usuario_solicitud.save()

            # Agregar a la bitácora
            bitacora = Bitacora(
                modulo=Modulo.query.filter_by(nombre=MODULO).first(),
                usuario=current_user,
                descripcion=safe_message(f"Nueva solicitud de actualización de datos de {usuario_solicitud.usuario.email}."),
                url=url_for("usuarios_solicitudes.detail", usuario_solicitud_id=usuario_solicitud.id),
            )
            bitacora.save()
            flash(bitacora.descripcion, "success")

            # Lanzar tarea en el fondo para enviar email de validación
            current_user.launch_task(
                nombre="usuarios_solicitudes.tasks.enviar_email_validacion",
                descripcion="Enviando mensaje de validación de email personal.",
                usuario_solicitud_id=usuario_solicitud.id,
            )

            # Lanzar tarea en el fondo para enviar SMS de validación
            current_user.launch_task(
                nombre="usuarios_solicitudes.tasks.enviar_sms_validacion",
                descripcion="Enviando SMS de validación de telefono personal.",
                usuario_solicitud_id=usuario_solicitud.id,
            )

            # Redirigir a la página de mensaje
            return render_template(
                "usuarios_solicitudes/message.jinja2",
                usuario=current_user,
                cabecera=f"Gracias {current_user.nombre}",
                mensaje="En poco tiempo recibirás un mensaje en tu correo electrónico personal. Este contiene un token para validar y un enlace al que debes de ir para completar este proceso.",
                btn_texto="Regresar",
                btn_enlace=url_for("sistemas.start"),
            )

    # Si no viene el formulario, poner los valores en los campos de solo lectura
    form.usuario_email.data = current_user.email
    form.usuario_nombre.data = current_user.nombre

    # Mostrar el formulario
    return render_template("usuarios_solicitudes/new.jinja2", form=form, usuario=current_user)

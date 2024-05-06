"""
Usuarios, vistas
"""

import json
import os
import re
from datetime import datetime, timedelta
from sqlalchemy import or_

import google.auth.transport.requests
import google.oauth2.id_token
from pytz import timezone
from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required, login_user, logout_user

from lib.datatables import get_datatable_parameters, output_datatable_json
from lib.firebase_auth import firebase_auth
from lib.pwgen import generar_api_key, generar_contrasena
from lib.safe_next_url import safe_next_url
from lib.safe_string import CONTRASENA_REGEXP, EMAIL_REGEXP, TOKEN_REGEXP, safe_curp, safe_email, safe_message, safe_string

from plataforma_web.blueprints.permisos.models import Permiso
from plataforma_web.blueprints.usuarios.decorators import anonymous_required, permission_required
from plataforma_web.extensions import pwd_context

from plataforma_web.blueprints.autoridades.models import Autoridad
from plataforma_web.blueprints.bitacoras.models import Bitacora
from plataforma_web.blueprints.distritos.models import Distrito
from plataforma_web.blueprints.entradas_salidas.models import EntradaSalida
from plataforma_web.blueprints.modulos.models import Modulo
from plataforma_web.blueprints.usuarios.forms import AccesoForm, UsuarioNewForm, UsuarioEditForm, UsuarioEditAdminForm, UsuarioSearchForm
from plataforma_web.blueprints.usuarios.models import Usuario

HTTP_REQUEST = google.auth.transport.requests.Request()

MODULO = "USUARIOS"

usuarios = Blueprint("usuarios", __name__, template_folder="templates")


@usuarios.route("/login", methods=["GET", "POST"])
@anonymous_required()
def login():
    """Acceso al Sistema"""
    form = AccesoForm(siguiente=request.args.get("siguiente"))
    if form.validate_on_submit():
        # Tomar valores del formulario
        identidad = request.form.get("identidad")
        contrasena = request.form.get("contrasena")
        token = request.form.get("token")
        siguiente_url = request.form.get("siguiente")
        # Si esta definida la variable de entorno FIREBASE_APIKEY
        if os.environ.get("FIREBASE_APIKEY", "") != "":
            # Entonces debe ingresar con Google/Microsoft/GitHub
            if re.fullmatch(TOKEN_REGEXP, token) is not None:
                # Acceso por Firebase Auth
                claims = google.oauth2.id_token.verify_firebase_token(token, HTTP_REQUEST)
                if claims:
                    email = claims.get("email", "Unknown")
                    usuario = Usuario.find_by_identity(email)
                    if usuario and usuario.authenticated(with_password=False):
                        if login_user(usuario, remember=True) and usuario.is_active:
                            EntradaSalida(
                                usuario_id=usuario.id,
                                tipo="INGRESO",
                                direccion_ip=request.remote_addr,
                            ).save()
                            if siguiente_url:
                                return redirect(safe_next_url(siguiente_url))
                            return redirect(url_for("sistemas.start"))
                        else:
                            flash("No está activa esa cuenta.", "warning")
                    else:
                        flash("No existe esa cuenta.", "warning")
                else:
                    flash("Falló la autentificación.", "warning")
            else:
                flash("Token incorrecto.", "warning")
        else:
            # De lo contrario, el ingreso es con username/password
            if re.fullmatch(EMAIL_REGEXP, identidad) is None:
                flash("Correo electrónico no válido.", "warning")
            elif re.fullmatch(CONTRASENA_REGEXP, contrasena) is None:
                flash("Contraseña no válida.", "warning")
            else:
                usuario = Usuario.find_by_identity(identidad)
                if usuario and usuario.authenticated(password=contrasena):
                    if login_user(usuario, remember=True) and usuario.is_active:
                        EntradaSalida(
                            usuario_id=usuario.id,
                            tipo="INGRESO",
                            direccion_ip=request.remote_addr,
                        ).save()
                        if siguiente_url:
                            return redirect(safe_next_url(siguiente_url))
                        return redirect(url_for("sistemas.start"))
                    else:
                        flash("No está activa esa cuenta", "warning")
                else:
                    flash("Usuario o contraseña incorrectos.", "warning")
    return render_template("usuarios/login.jinja2", form=form, firebase_auth=firebase_auth, title="Plataforma Web")


@usuarios.route("/logout")
@login_required
def logout():
    """Salir del Sistema"""
    EntradaSalida(
        usuario_id=current_user.id,
        tipo="SALIO",
        direccion_ip=request.remote_addr,
    ).save()
    logout_user()
    flash("Ha salido de este sistema.", "success")
    return redirect(url_for("usuarios.login"))


@usuarios.route("/perfil")
@login_required
def profile():
    """Mostrar el Perfil"""
    ahora_utc = datetime.now(timezone("UTC"))
    ahora_mx_coah = ahora_utc.astimezone(timezone("America/Mexico_City"))
    formato_fecha = "%Y-%m-%d %H:%M %p"
    return render_template(
        "usuarios/profile.jinja2",
        ahora_utc_str=ahora_utc.strftime(formato_fecha),
        ahora_mx_coah_str=ahora_mx_coah.strftime(formato_fecha),
    )


@usuarios.route("/usuarios")
@login_required
@permission_required(MODULO, Permiso.VER)
def list_active():
    """Listado de Usuarios activos"""
    return render_template(
        "usuarios/list.jinja2",
        filtros=json.dumps({"estatus": "A"}),
        titulo="Usuarios",
        estatus="A",
    )


@usuarios.route("/usuarios/inactivos")
@login_required
@permission_required(MODULO, Permiso.MODIFICAR)
def list_inactive():
    """Listado de Usuarios inactivos"""
    return render_template(
        "usuarios/list.jinja2",
        filtros=json.dumps({"estatus": "B"}),
        titulo="Usuarios inactivos",
        estatus="B",
    )


@usuarios.route("/usuarios/buscar", methods=["GET", "POST"])
def search():
    """Buscar Usuarios"""
    form_search = UsuarioSearchForm()
    if form_search.validate_on_submit():
        busqueda = {"estatus": "A"}
        titulos = []
        if form_search.nombres.data:
            nombres = safe_string(form_search.nombres.data)
            if nombres != "":
                busqueda["nombres"] = nombres
                titulos.append("nombres " + nombres)
        if form_search.apellido_paterno.data:
            apellido_paterno = safe_string(form_search.apellido_paterno.data)
            if apellido_paterno != "":
                busqueda["apellido_paterno"] = apellido_paterno
                titulos.append("apellido paterno " + apellido_paterno)
        if form_search.apellido_materno.data:
            apellido_materno = safe_string(form_search.apellido_materno.data)
            if apellido_materno != "":
                busqueda["apellido_materno"] = apellido_materno
                titulos.append("apellido materno " + apellido_materno)
        if form_search.curp.data:
            curp = safe_string(form_search.curp.data)
            if curp != "":
                busqueda["curp"] = curp
                titulos.append("CURP " + curp)
        if form_search.puesto.data:
            puesto = safe_string(form_search.puesto.data)
            if puesto != "":
                busqueda["puesto"] = puesto
                titulos.append("puesto " + puesto)
        if form_search.email.data:
            email = safe_email(form_search.email.data, search_fragment=True)
            if email != "":
                busqueda["email"] = email
                titulos.append("e-mail " + email)
        return render_template(
            "usuarios/list.jinja2",
            filtros=json.dumps(busqueda),
            titulo="Usuarios con " + ", ".join(titulos),
            estatus="A",
        )
    return render_template("usuarios/search.jinja2", form=form_search)


@usuarios.route("/usuarios/datatable_json", methods=["GET", "POST"])
def datatable_json():
    """DataTable JSON para listado de Usuarios"""
    # Tomar parámetros de Datatables
    draw, start, rows_per_page = get_datatable_parameters()
    # Consultar
    consulta = Usuario.query
    if "estatus" in request.form:
        consulta = consulta.filter_by(estatus=request.form["estatus"])
    else:
        consulta = consulta.filter_by(estatus="A")
    # Primero filtrar por columnas propias
    if "autoridad_id" in request.form:
        consulta = consulta.filter_by(autoridad_id=request.form["autoridad_id"])
    if "oficina_id" in request.form:
        consulta = consulta.filter_by(oficina_id=request.form["oficina_id"])
    if "nombres" in request.form:
        consulta = consulta.filter(Usuario.nombres.contains(safe_string(request.form["nombres"])))
    if "apellido_paterno" in request.form:
        consulta = consulta.filter(Usuario.apellido_paterno.contains(safe_string(request.form["apellido_paterno"])))
    if "apellido_materno" in request.form:
        consulta = consulta.filter(Usuario.apellido_materno.contains(safe_string(request.form["apellido_materno"])))
    if "nombre_completo" in request.form:
        palabras = safe_string(request.form["nombre_completo"]).split(" ")
        for palabra in palabras:
            consulta = consulta.filter(or_(Usuario.nombres.contains(palabra), Usuario.apellido_paterno.contains(palabra), Usuario.apellido_materno.contains(palabra)))
    if "curp" in request.form:
        consulta = consulta.filter(Usuario.curp.contains(safe_string(request.form["curp"])))
    if "puesto" in request.form:
        consulta = consulta.filter(Usuario.puesto.contains(safe_string(request.form["puesto"])))
    if "email" in request.form:
        consulta = consulta.filter(Usuario.email.contains(safe_email(request.form["email"], search_fragment=True)))
    if "workspace" in request.form:
        consulta = consulta.filter(Usuario.workspace == safe_string(request.form["email"]))
    # Ordenar y paginar
    registros = consulta.order_by(Usuario.email).offset(start).limit(rows_per_page).all()
    total = consulta.count()
    # Elaborar datos para DataTable
    data = []
    for resultado in registros:
        data.append(
            {
                "detalle": {
                    "email": resultado.email,
                    "url": url_for("usuarios.detail", usuario_id=resultado.id),
                },
                "nombre": resultado.nombre,
                "puesto": resultado.puesto,
                "autoridad": {
                    "clave": resultado.autoridad.clave,
                    "url": url_for("autoridades.detail", autoridad_id=resultado.autoridad_id) if current_user.can_view("AUTORIDADES") else "",
                },
                "oficina": {
                    "clave": resultado.oficina.clave,
                    "url": url_for("oficinas.detail", oficina_id=resultado.oficina_id) if current_user.can_view("OFICINAS") else "",
                },
                "workspace": resultado.workspace,
            }
        )
    # Entregar JSON
    return output_datatable_json(draw, total, data)


@usuarios.route("/usuarios/list_usuarios_json/", methods=["POST"])
def list_usuarios_json():
    """Listado de Usuarios"""

    # Consultar
    consulta = Usuario.query
    if "searchString" in request.form:
        busqueda = safe_string(request.form["searchString"])
        consulta = consulta.filter(or_(Usuario.nombres.contains(busqueda), Usuario.apellido_paterno.contains(busqueda), Usuario.apellido_materno.contains(busqueda)))
        consulta = consulta.order_by(Usuario.apellido_paterno).limit(15).all()

    # Elaborar datos para el Select2
    results = []
    for usuario in consulta:
        results.append({"id": usuario.id, "text": usuario.nombre})

    return {"results": results, "pagination": {"more": False}}


@usuarios.route("/usuarios/<int:usuario_id>")
@login_required
@permission_required(MODULO, Permiso.VER)
def detail(usuario_id):
    """Detalle de un Usuario"""
    usuario = Usuario.query.get_or_404(usuario_id)
    return render_template("usuarios/detail.jinja2", usuario=usuario)


@usuarios.route("/usuarios/nuevo", methods=["GET", "POST"])
@login_required
@permission_required(MODULO, Permiso.CREAR)
def new():
    """Nuevo usuario"""
    form = UsuarioNewForm()
    if form.validate_on_submit():
        # Validar que el email no se repita
        email = safe_email(form.email.data)
        if Usuario.query.filter_by(email=email).first():
            flash("El e-mail ya está en uso. Debe de ser único.", "warning")
        else:
            # Consultar la autoridad a partir del ID que viene
            autoridad = Autoridad.query.get_or_404(form.autoridad.data)
            # Cifrar la contrasena
            if form.contrasena.data == "":
                contrasena = pwd_context.hash(generar_contrasena())
            else:
                contrasena = pwd_context.hash(form.contrasena.data)
            usuario = Usuario(
                autoridad=autoridad,
                oficina=form.oficina.data,
                nombres=safe_string(form.nombres.data, save_enie=True),
                apellido_paterno=safe_string(form.apellido_paterno.data, save_enie=True),
                apellido_materno=safe_string(form.apellido_materno.data, save_enie=True),
                curp=safe_curp(form.curp.data, is_optional=True),
                puesto=safe_string(form.puesto.data, save_enie=True),
                email=email,
                workspace=form.workspace.data,
                efirma_registro_id=form.efirma_registro_id.data,
                contrasena=contrasena,
                api_key="",
                api_key_expiracion=datetime(year=2000, month=1, day=1),
            )
            usuario.save()
            bitacora = Bitacora(
                modulo=Modulo.query.filter_by(nombre=MODULO).first(),
                usuario=current_user,
                descripcion=safe_message(f"Nuevo usuario {usuario.email}: {usuario.nombre}"),
                url=url_for("usuarios.detail", usuario_id=usuario.id),
            )
            bitacora.save()
            flash(bitacora.descripcion, "success")
            return redirect(bitacora.url)
    distritos = Distrito.query.filter_by(estatus="A").order_by(Distrito.nombre).all()
    autoridades = Autoridad.query.filter_by(estatus="A").order_by(Autoridad.clave).all()
    return render_template("usuarios/new.jinja2", form=form, distritos=distritos, autoridades=autoridades)


@usuarios.route("/usuarios/edicion/<int:usuario_id>", methods=["GET", "POST"])
@login_required
@permission_required(MODULO, Permiso.MODIFICAR)
def edit(usuario_id):
    """Editar Usuario para quien tenga el nivel de modificar"""
    usuario = Usuario.query.get_or_404(usuario_id)
    form = UsuarioEditForm()
    if form.validate_on_submit():
        usuario.nombres = safe_string(form.nombres.data, save_enie=True)
        usuario.apellido_paterno = safe_string(form.apellido_paterno.data, save_enie=True)
        usuario.apellido_materno = safe_string(form.apellido_materno.data, save_enie=True)
        usuario.curp = safe_curp(form.curp.data, is_optional=True)
        usuario.puesto = safe_string(form.puesto.data, save_enie=True)
        usuario.oficina = form.oficina.data
        usuario.efirma_registro_id = form.efirma_registro_id.data
        usuario.save()
        bitacora = Bitacora(
            modulo=Modulo.query.filter_by(nombre=MODULO).first(),
            usuario=current_user,
            descripcion=safe_message(f"Editado usuario {usuario.email}: {usuario.nombre}"),
            url=url_for("usuarios.detail", usuario_id=usuario.id),
        )
        bitacora.save()
        flash(bitacora.descripcion, "success")
        return redirect(bitacora.url)
    form.distrito.data = usuario.autoridad.distrito.nombre  # Read only
    form.autoridad.data = usuario.autoridad.descripcion  # Read only
    form.nombres.data = usuario.nombres
    form.apellido_paterno.data = usuario.apellido_paterno
    form.apellido_materno.data = usuario.apellido_materno
    form.curp.data = usuario.curp
    form.puesto.data = usuario.puesto
    form.email.data = usuario.email  # Read only
    form.workspace.data = usuario.workspace  # Read only
    form.efirma_registro_id.data = usuario.efirma_registro_id
    form.oficina.data = usuario.oficina
    return render_template("usuarios/edit.jinja2", form=form, usuario=usuario)


@usuarios.route("/usuarios/edicion_admin/<int:usuario_id>", methods=["GET", "POST"])
@login_required
@permission_required(MODULO, Permiso.ADMINISTRAR)
def edit_admin(usuario_id):
    """Editar Usuario para quien tenga el nivel de administrar"""
    usuario = Usuario.query.get_or_404(usuario_id)
    form = UsuarioEditAdminForm()
    if form.validate_on_submit():
        es_valido = True
        # Si cambia el e-mail verificar que no este en uso
        email = safe_email(form.email.data)
        if usuario.email != email:
            usuario_existente = Usuario.query.filter_by(email=email).first()
            if usuario_existente and usuario_existente.id != usuario.id:
                es_valido = False
                flash("La e-mail ya está en uso. Debe de ser único.", "warning")
        # Si es valido actualizar
        if es_valido:
            usuario.autoridad = Autoridad.query.get_or_404(form.autoridad.data)
            usuario.nombres = safe_string(form.nombres.data, save_enie=True)
            usuario.apellido_paterno = safe_string(form.apellido_paterno.data, save_enie=True)
            usuario.apellido_materno = safe_string(form.apellido_materno.data, save_enie=True)
            usuario.curp = safe_curp(form.curp.data, is_optional=True)
            usuario.puesto = safe_string(form.puesto.data, save_enie=True)
            usuario.email = email
            usuario.email_personal = safe_email(form.email_personal.data)
            usuario.workspace = safe_string(form.workspace.data)
            usuario.efirma_registro_id = form.efirma_registro_id.data
            usuario.oficina = form.oficina.data
            if form.contrasena.data != "":
                usuario.contrasena = pwd_context.hash(form.contrasena.data)
            usuario.save()
            bitacora = Bitacora(
                modulo=Modulo.query.filter_by(nombre=MODULO).first(),
                usuario=current_user,
                descripcion=safe_message(f"Editado usuario {usuario.email}: {usuario.nombre}"),
                url=url_for("usuarios.detail", usuario_id=usuario.id),
            )
            bitacora.save()
            flash(bitacora.descripcion, "success")
            return redirect(bitacora.url)
    form.distrito.data = usuario.autoridad.distrito
    form.autoridad.data = usuario.autoridad
    form.nombres.data = usuario.nombres
    form.apellido_paterno.data = usuario.apellido_paterno
    form.apellido_materno.data = usuario.apellido_materno
    form.curp.data = usuario.curp
    form.puesto.data = usuario.puesto
    form.email.data = usuario.email
    form.email_personal.data = usuario.email_personal
    form.workspace.data = usuario.workspace
    form.efirma_registro_id.data = usuario.efirma_registro_id
    form.oficina.data = usuario.oficina
    distritos = Distrito.query.filter_by(estatus="A").order_by(Distrito.nombre).all()
    autoridades = Autoridad.query.filter_by(estatus="A").order_by(Autoridad.clave).all()
    return render_template(
        "usuarios/edit_admin.jinja2",
        form=form,
        usuario=usuario,
        distritos=distritos,
        autoridades=autoridades,
    )


@usuarios.route("/usuarios/api_key/<int:usuario_id>")
@login_required
@permission_required(MODULO, Permiso.ADMINISTRAR)
def view_api_key(usuario_id):
    """Ver API Key"""

    # Consultar usuario
    usuario = Usuario.query.get_or_404(usuario_id)
    if usuario.estatus != "A":
        flash("El usuario no está activo.", "warning")
        return redirect(url_for("usuarios.detail", usuario_id=usuario.id))

    # Juntar los permisos por nivel
    permisos_por_nivel = {1: [], 2: [], 3: [], 4: []}
    for etiqueta, nivel in usuario.permisos.items():
        permisos_por_nivel[nivel].append(etiqueta)

    # Mostrar api_key.jinja2
    return render_template(
        "usuarios/api_key.jinja2",
        usuario=usuario,
        permisos_en_nivel_1=sorted(permisos_por_nivel[1]),
        permisos_en_nivel_2=sorted(permisos_por_nivel[2]),
        permisos_en_nivel_3=sorted(permisos_por_nivel[3]),
        permisos_en_nivel_4=sorted(permisos_por_nivel[4]),
    )


@usuarios.route("/usuarios/api_key_request/<int:usuario_id>", methods=["GET", "POST"])
@login_required
@permission_required(MODULO, Permiso.ADMINISTRAR)
def request_api_key_json(usuario_id):
    """Solicitar API Key"""

    # Consultar usuario
    usuario = Usuario.query.get_or_404(usuario_id)
    if usuario.estatus != "A":
        return {"success": False, "message": "El usuario no está activo", "api_key": "", "api_key_expiracion": ""}

    # Si se recibe action con clean, se va a limpiar
    if "action" in request.form and request.form["action"] == "clean":
        usuario.api_key = ""
        usuario.api_key_expiracion = datetime(year=2000, month=1, day=1)
        usuario.save()
        mensaje = f"La API Key de {usuario.email} fue eliminada"
        bitacora = Bitacora(
            modulo=Modulo.query.filter_by(nombre=MODULO).first(),
            usuario=current_user,
            descripcion=mensaje,
            url=url_for("usuarios.detail", usuario_id=usuario.id),
        )
        bitacora.save()
        return {"success": True, "message": mensaje, "api_key": usuario.api_key, "api_key_expiracion": usuario.api_key_expiracion}

    # Si se recibe action con new, se va a crear una nueva
    if "action" in request.form and request.form["action"] == "new":
        if "days" in request.form:
            days = int(request.form["days"])
        else:
            days = 90
        usuario.api_key = generar_api_key(usuario.id, usuario.email)
        usuario.api_key_expiracion = datetime.now() + timedelta(days=days)
        usuario.save()
        mensaje = f"Nueva API Key para {usuario.email} con expiración en {days} días"
        bitacora = Bitacora(
            modulo=Modulo.query.filter_by(nombre=MODULO).first(),
            usuario=current_user,
            descripcion=mensaje,
            url=url_for("usuarios.detail", usuario_id=usuario.id),
        )
        bitacora.save()
        return {"success": True, "message": mensaje, "api_key": usuario.api_key, "api_key_expiracion": usuario.api_key_expiracion}

    # Si no se recibe nada, entregar la actual
    return {"success": True, "message": "Se ha entregado la API Key a la interfaz", "api_key": usuario.api_key, "api_key_expiracion": usuario.api_key_expiracion}


@usuarios.route("/usuarios/eliminar/<int:usuario_id>")
@login_required
@permission_required(MODULO, Permiso.MODIFICAR)
def delete(usuario_id):
    """Eliminar Usuario"""
    usuario = Usuario.query.get_or_404(usuario_id)
    if usuario.estatus == "A":
        usuario.delete()
        bitacora = Bitacora(
            modulo=Modulo.query.filter_by(nombre=MODULO).first(),
            usuario=current_user,
            descripcion=safe_message(f"Eliminado usuario {usuario.email}: {usuario.nombre}"),
            url=url_for("usuarios.detail", usuario_id=usuario.id),
        )
        bitacora.save()
        flash(bitacora.descripcion, "success")
    return redirect(url_for("usuarios.detail", usuario_id=usuario_id))


@usuarios.route("/usuarios/recuperar/<int:usuario_id>")
@login_required
@permission_required(MODULO, Permiso.MODIFICAR)
def recover(usuario_id):
    """Recuperar Usuario"""
    usuario = Usuario.query.get_or_404(usuario_id)
    if usuario.estatus == "B":
        usuario.recover()
        bitacora = Bitacora(
            modulo=Modulo.query.filter_by(nombre=MODULO).first(),
            usuario=current_user,
            descripcion=safe_message(f"Recuperado usuario {usuario.email}: {usuario.nombre}"),
            url=url_for("usuarios.detail", usuario_id=usuario.id),
        )
        bitacora.save()
        flash(bitacora.descripcion, "success")
    return redirect(url_for("usuarios.detail", usuario_id=usuario_id))

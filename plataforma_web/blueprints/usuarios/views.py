"""
Usuarios, vistas
"""
import os
import re

import google.auth.transport.requests
import google.oauth2.id_token
from flask import Blueprint, flash, redirect, request, render_template, url_for
from flask_login import current_user, login_required, login_user, logout_user

from lib.firebase_auth import firebase_auth
from lib.pwgen import generar_contrasena
from lib.safe_next_url import safe_next_url
from lib.safe_string import CONTRASENA_REGEXP, EMAIL_REGEXP, TOKEN_REGEXP, safe_message

from plataforma_web.blueprints.permisos.models import Permiso
from plataforma_web.blueprints.usuarios.decorators import anonymous_required, permission_required
from plataforma_web.extensions import pwd_context

from plataforma_web.blueprints.autoridades.models import Autoridad
from plataforma_web.blueprints.bitacoras.models import Bitacora
from plataforma_web.blueprints.distritos.models import Distrito
from plataforma_web.blueprints.entradas_salidas.models import EntradaSalida
from plataforma_web.blueprints.modulos.models import Modulo
from plataforma_web.blueprints.usuarios.forms import AccesoForm, UsuarioFormNew, UsuarioFormEdit
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
    return render_template("usuarios/profile.jinja2")


@usuarios.route("/usuarios")
@login_required
@permission_required(MODULO, Permiso.VER)
def list_active():
    """Listado de Usuarios activos"""
    usuarios_activos = Usuario.query.filter(Usuario.estatus == "A").all()
    return render_template(
        "usuarios/list.jinja2",
        usuarios=usuarios_activos,
        titulo="Usuarios",
        estatus="A",
    )


@usuarios.route("/usuarios/inactivos")
@login_required
@permission_required(MODULO, Permiso.MODIFICAR)
def list_inactive():
    """Listado de Usuarios inactivos"""
    usuarios_inactivos = Usuario.query.filter(Usuario.estatus == "B").all()
    return render_template(
        "usuarios/list.jinja2",
        usuarios=usuarios_inactivos,
        titulo="Usuarios inactivos",
        estatus="B",
    )


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
    form = UsuarioFormNew()
    if form.validate_on_submit():
        autoridad = Autoridad.query.get_or_404(form.autoridad.data)
        if form.contrasena.data == "":
            contrasena = pwd_context.hash(generar_contrasena())
        else:
            contrasena = pwd_context.hash(form.contrasena.data)
        usuario = Usuario(
            autoridad=autoridad,
            oficina=form.oficina.data,
            nombres=form.nombres.data,
            apellido_paterno=form.apellido_paterno.data,
            apellido_materno=form.apellido_materno.data,
            curp=form.curp.data,
            email=form.email.data,
            workspace=form.workspace.data,
            puesto=form.puesto.data,
            contrasena=contrasena,
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
    """Editar Usuario, solo al escribir la contraseña se cambia"""
    usuario = Usuario.query.get_or_404(usuario_id)
    form = UsuarioFormEdit()
    if form.validate_on_submit():
        usuario.autoridad = Autoridad.query.get_or_404(form.autoridad.data)
        usuario.oficina = form.oficina.data
        usuario.nombres = form.nombres.data
        usuario.apellido_paterno = form.apellido_paterno.data
        usuario.apellido_materno = form.apellido_materno.data
        usuario.curp = form.curp.data
        usuario.email = form.email.data
        usuario.workspace = form.workspace.data
        usuario.puesto = form.puesto.data
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
    form.oficina.data = usuario.oficina
    form.nombres.data = usuario.nombres
    form.apellido_paterno.data = usuario.apellido_paterno
    form.apellido_materno.data = usuario.apellido_materno
    form.curp.data = usuario.curp
    form.email.data = usuario.email
    form.workspace.data = usuario.workspace
    form.puesto.data = usuario.puesto
    distritos = Distrito.query.filter_by(estatus="A").order_by(Distrito.nombre).all()
    autoridades = Autoridad.query.filter_by(estatus="A").order_by(Autoridad.clave).all()
    return render_template("usuarios/edit.jinja2", form=form, usuario=usuario, distritos=distritos, autoridades=autoridades)


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

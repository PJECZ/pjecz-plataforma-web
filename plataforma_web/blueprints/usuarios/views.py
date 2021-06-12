"""
Usuarios, vistas
"""
import google.auth.transport.requests
import google.oauth2.id_token
from flask import Blueprint, flash, redirect, request, render_template, url_for
from flask_login import current_user, login_required, login_user, logout_user
from lib.firebase_auth import firebase_auth
from lib.pwgen import generar_contrasena
from lib.safe_next_url import safe_next_url
from lib.safe_string import safe_message

from plataforma_web.blueprints.roles.models import Permiso
from plataforma_web.blueprints.usuarios.decorators import anonymous_required, permission_required
from plataforma_web.extensions import pwd_context

from plataforma_web.blueprints.autoridades.models import Autoridad
from plataforma_web.blueprints.bitacoras.models import Bitacora
from plataforma_web.blueprints.distritos.models import Distrito
from plataforma_web.blueprints.entradas_salidas.models import EntradaSalida
from plataforma_web.blueprints.usuarios.forms import AccesoForm, UsuarioFormNew, UsuarioFormEdit, CambiarContrasenaForm, UsuarioSearchForm
from plataforma_web.blueprints.usuarios.models import Usuario

HTTP_REQUEST = google.auth.transport.requests.Request()

usuarios = Blueprint("usuarios", __name__, template_folder="templates")


@usuarios.route("/login", methods=["GET", "POST"])
@anonymous_required()
def login():
    """Acceso al Sistema"""
    form = AccesoForm(siguiente=request.args.get("siguiente"))
    if form.validate_on_submit():
        # Validar
        identidad = request.form.get("identidad")
        contrasena = request.form.get("contrasena")
        id_token = request.form.get("token")
        siguiente_url = request.form.get("siguiente")
        # Elegir
        if id_token != "" and (identidad == "" and contrasena == ""):
            # Acceso por Firebase Auth
            claims = google.oauth2.id_token.verify_firebase_token(id_token, HTTP_REQUEST)
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
                    flash("No está activa esa cuenta.", "warning")
                else:
                    flash("No existe esa cuenta.", "warning")
            else:
                flash("Falló la autentificación.", "warning")
        elif identidad != "" and contrasena != "":
            # Acceso por usuario y contraseña
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
                flash("No está activa esa cuenta", "warning")
            else:
                flash("Usuario o contraseña incorrectos.", "warning")
        else:
            flash("Infomación incompleta.", "warning")
    return render_template("usuarios/login.jinja2", form=form, firebase_auth=firebase_auth)


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


@usuarios.route("/cambiar_contrasena", methods=["GET", "POST"])
@login_required
@permission_required(Permiso.MODIFICAR_CUENTAS)
def change_password():
    """Cambiar Contraseña"""
    form = CambiarContrasenaForm()
    usuario = Usuario.query.get_or_404(current_user.id)
    if form.validate_on_submit():
        if not pwd_context.verify(form.contrasena_actual.data, current_user.contrasena):
            flash("Contraseña actual incorrecta.", "warning")
        else:
            usuario.contrasena = pwd_context.hash(form.contrasena.data)
            usuario.save()
            flash("Contraseña cambiada.", "success")
            return redirect(url_for("usuarios.profile"))
    return render_template("usuarios/change_password.jinja2", form=form)


@usuarios.route("/usuarios")
@login_required
@permission_required(Permiso.VER_CUENTAS)
def list_active():
    """Listado de Usuarios activos"""
    usuarios_activos = Usuario.query.filter(Usuario.estatus == "A").limit(200).all()
    return render_template("usuarios/list.jinja2", usuarios=usuarios_activos, estatus="A")


@usuarios.route("/usuarios/inactivos")
@permission_required(Permiso.MODIFICAR_CUENTAS)
def list_inactive():
    """Listado de Usuarios inactivos"""
    usuarios_inactivos = Usuario.query.filter(Usuario.estatus == "B").limit(200).all()
    return render_template("usuarios/list.jinja2", usuarios=usuarios_inactivos, estatus="B")


@usuarios.route("/usuarios/<int:usuario_id>")
@login_required
@permission_required(Permiso.VER_CUENTAS)
def detail(usuario_id):
    """Detalle de un Usuario"""
    usuario = Usuario.query.get_or_404(usuario_id)
    return render_template("usuarios/detail.jinja2", usuario=usuario)


@usuarios.route("/usuarios/buscar", methods=["GET", "POST"])
@login_required
@permission_required(Permiso.VER_CUENTAS)
def search():
    """Buscar Usuarios"""
    form_search = UsuarioSearchForm()
    if form_search.validate_on_submit():
        consulta = Usuario.query
        if form_search.nombres.data:
            nombres = form_search.nombres.data.strip()
            consulta = consulta.filter(Usuario.nombres.like(f"%{nombres}%"))
        if form_search.apellido_paterno.data:
            apellido_paterno = form_search.apellido_paterno.data.strip()
            consulta = consulta.filter(Usuario.apellido_paterno.like(f"%{apellido_paterno}%"))
        if form_search.apellido_materno.data:
            apellido_materno = form_search.apellido_materno.data.strip()
            consulta = consulta.filter(Usuario.apellido_materno.like(f"%{apellido_materno}%"))
        consulta = consulta.limit(100).all()
        return render_template("usuarios/list.jinja2", usuarios=consulta)
    return render_template("usuarios/search.jinja2", form=form_search)


@usuarios.route("/usuarios/nuevo", methods=["GET", "POST"])
@login_required
@permission_required(Permiso.CREAR_CUENTAS)
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
            nombres=form.nombres.data,
            apellido_paterno=form.apellido_paterno.data,
            apellido_materno=form.apellido_materno.data,
            email=form.email.data,
            workspace=form.workspace.data,
            rol=form.rol.data,
            contrasena=contrasena,
        )
        usuario.save()
        bitacora = Bitacora(
            modulo="USUARIOS",
            usuario=current_user,
            descripcion=safe_message(f"Nuevo Usuario {usuario.nombre} con e-mail {usuario.email} y rol {usuario.rol.nombre}"),
            url=url_for("usuarios.detail", usuario_id=usuario.id),
        )
        bitacora.save()
        flash(bitacora.descripcion, "success")
        return redirect(bitacora.url)
    distritos = Distrito.query.filter(Distrito.estatus == "A").order_by(Distrito.nombre).all()
    autoridades = Autoridad.query.filter(Autoridad.estatus == "A").order_by(Autoridad.clave).all()
    return render_template("usuarios/new.jinja2", form=form, distritos=distritos, autoridades=autoridades)


@usuarios.route("/usuarios/edicion/<int:usuario_id>", methods=["GET", "POST"])
@login_required
@permission_required(Permiso.MODIFICAR_CUENTAS)
def edit(usuario_id):
    """Editar Usuario, solo al escribir la contraseña se cambia"""
    usuario = Usuario.query.get_or_404(usuario_id)
    form = UsuarioFormEdit()
    if form.validate_on_submit():
        usuario.nombres = form.nombres.data
        usuario.apellido_paterno = form.apellido_paterno.data
        usuario.apellido_materno = form.apellido_materno.data
        usuario.email = form.email.data
        usuario.workspace = form.workspace.data
        if form.email.data != "":
            usuario.contrasena = pwd_context.hash(form.contrasena.data)
        usuario.rol = form.rol.data
        usuario.save()
        flash(f"Usuario {usuario.nombre} guardado.", "success")
        return redirect(url_for("usuarios.detail", usuario_id=usuario.id))
    form.nombres.data = usuario.nombres
    form.apellido_paterno.data = usuario.apellido_paterno
    form.apellido_materno.data = usuario.apellido_materno
    form.email.data = usuario.email
    form.workspace.data = usuario.workspace
    form.rol.data = usuario.rol
    return render_template("usuarios/edit.jinja2", form=form, usuario=usuario)


@usuarios.route("/usuarios/eliminar/<int:usuario_id>")
@permission_required(Permiso.MODIFICAR_CUENTAS)
def delete(usuario_id):
    """Eliminar Usuario"""
    usuario = Usuario.query.get_or_404(usuario_id)
    if usuario.estatus == "A":
        usuario.delete()
        flash(f"Usuario {usuario.nombre} eliminado.", "success")
    return redirect(url_for("usuarios.detail", usuario_id=usuario_id))


@usuarios.route("/usuarios/recuperar/<int:usuario_id>")
@permission_required(Permiso.MODIFICAR_CUENTAS)
def recover(usuario_id):
    """Recuperar Usuario"""
    usuario = Usuario.query.get_or_404(usuario_id)
    if usuario.estatus == "B":
        usuario.recover()
        flash(f"Usuario {usuario.nombre} recuperado.", "success")
    return redirect(url_for("usuarios.detail", usuario_id=usuario_id))

"""
INV EQUIPOS FOTOS, vistas
"""
from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required
from werkzeug.datastructures import CombinedMultiDict

from lib.safe_string import safe_message, safe_string
from lib.storage import GoogleCloudStorage, NotAllowedExtesionError, UnknownExtesionError, NotConfiguredError
from plataforma_web.blueprints.usuarios.decorators import permission_required

from plataforma_web.blueprints.bitacoras.models import Bitacora
from plataforma_web.blueprints.inv_equipos_fotos.forms import INVEquipoFotoForm
from plataforma_web.blueprints.inv_equipos_fotos.models import INVEquipoFoto
from plataforma_web.blueprints.inv_equipos.models import INVEquipo
from plataforma_web.blueprints.modulos.models import Modulo
from plataforma_web.blueprints.permisos.models import Permiso

inv_equipos_fotos = Blueprint("inv_equipos_fotos", __name__, template_folder="templates")

MODULO = "INV EQUIPOS FOTOS"
SUBDIRECTORIO = "inv_equipos_fotos"


@inv_equipos_fotos.before_request
@login_required
@permission_required(MODULO, Permiso.VER)
def before_request():
    """Permiso por defecto"""


@inv_equipos_fotos.route("/inv_equipos_fotos")
def list_active():
    """Listado de INV EQUIPOS FOTOS activos"""
    return render_template(
        "inv_equipos_fotos/list.jinja2",
        inv_equipos_fotos=INVEquipoFoto.query.filter_by(estatus="A").all(),
        titulo="Fotos",
        estatus="A",
    )


@inv_equipos_fotos.route("/inv_equipos_fotos/inactivos")
@permission_required(MODULO, Permiso.MODIFICAR)
def list_inactive():
    """Listado de INV EQUIPOS FOTOS inactivos"""
    return render_template(
        "inv_equipos_fotos/list.jinja2",
        inv_equipos_fotos=INVEquipoFoto.query.filter_by(estatus="B").all(),
        titulo="Fotos inactivos",
        estatus="B",
    )


@inv_equipos_fotos.route("/inv_equipos_fotos/<int:equipo_foto_id>")
def detail(equipo_foto_id):
    """Detalle de un CID Formato"""
    equipo_foto = INVEquipoFoto.query.get_or_404(equipo_foto_id)
    return render_template("inv_equipos_fotos/detail.jinja2", equipo_foto=equipo_foto)


@inv_equipos_fotos.route("/inv_equipos_fotos/nuevo/<int:equipo_id>", methods=["GET", "POST"])
@permission_required(MODULO, Permiso.CREAR)
def new(equipo_id):
    """Nuevo CID Formato"""
    # Validar procedimiento
    equipo = INVEquipo.query.get_or_404(equipo_id)
    if equipo.estatus != "A":
        flash("El equipo no es activo.", "warning")
        return redirect(url_for("inv_equipos.list_active"))
    # Si viene el formulario
    form = INVEquipoFotoForm(CombinedMultiDict((request.files, request.form)))
    if form.validate_on_submit():
        es_valido = True
        # Validar el archivo
        archivo = request.files["archivo"]
        storage = GoogleCloudStorage(SUBDIRECTORIO)
        try:
            storage.set_content_type(archivo.filename)
        except NotAllowedExtesionError:
            flash("Tipo de archivo no permitido.", "warning")
            es_valido = False
        except UnknownExtesionError:
            flash("Tipo de archivo desconocido.", "warning")
            es_valido = False
        # Si es válido
        if es_valido:
            # Insertar el registro, para obtener el ID
            equipo_foto = INVEquipoFoto(
                equipo=equipo,
                archivo=archivo,
            )
            equipo_foto.save()
            # Subir el archivo a la nube
            try:
                storage.set_filename(hashed_id=equipo_foto.encode_id(), description=descripcion)
                storage.upload(archivo.stream.read())
                equipo_foto.archivo = archivo.filename  # Conservar el nombre original
                equipo_foto.url = storage.url
                equipo_foto.save()
            except NotConfiguredError:
                flash("No se ha configurado el almacenamiento en la nube.", "warning")
            except Exception:
                flash("Error al subir el archivo.", "danger")
            # Registrar la acción en la bitácora
            bitacora = Bitacora(
                modulo=Modulo.query.filter_by(nombre=MODULO).first(),
                usuario=current_user,
                descripcion=safe_message(f"Nuevo formato {equipo_foto.descripcion}"),
                url=url_for("inv_equipos_fotos.detail", equipo_foto_id=equipo_foto.id),
            )
            bitacora.save()
            flash(bitacora.descripcion, "success")
            return redirect(bitacora.url)
    # Mostrar formulario
    form.procedimiento_titulo.data = equipo.titulo_procedimiento  # Read only
    return render_template("inv_equipos_fotos/new.jinja2", form=form, equipo=equipo)


@inv_equipos_fotos.route("/inv_equipos_fotos/edicion/<int:equipo_foto_id>", methods=["GET", "POST"])
@permission_required(MODULO, Permiso.MODIFICAR)
def edit(equipo_foto_id):
    """Editar CID Formato"""
    equipo_foto = INVEquipoFoto.query.get_or_404(equipo_foto_id)
    form = INVEquipoFotoForm()
    if form.validate_on_submit():
        equipo_foto.descripcion = safe_string(form.descripcion.data)
        equipo_foto.save()
        bitacora = Bitacora(
            modulo=Modulo.query.filter_by(nombre=MODULO).first(),
            usuario=current_user,
            descripcion=safe_message(f"Editado el formato {equipo_foto.descripcion}"),
            url=url_for("inv_equipos_fotos.detail", equipo_foto_id=equipo_foto.id),
        )
        bitacora.save()
        flash(bitacora.descripcion, "success")
        return redirect(bitacora.url)
    form.procedimiento_titulo.data = equipo_foto.procedimiento.titulo_procedimiento  # Read only
    form.descripcion.data = equipo_foto.descripcion
    return render_template("inv_equipos_fotos/edit.jinja2", form=form, equipo_foto=equipo_foto)


@inv_equipos_fotos.route("/inv_equipos_fotos/eliminar/<int:equipo_foto_id>")
@permission_required(MODULO, Permiso.MODIFICAR)
def delete(equipo_foto_id):
    """Eliminar CID Formato"""
    equipo_foto = INVEquipoFoto.query.get_or_404(equipo_foto_id)
    if equipo_foto.estatus == "A":
        equipo_foto.delete()
        bitacora = Bitacora(
            modulo=Modulo.query.filter_by(nombre=MODULO).first(),
            usuario=current_user,
            descripcion=safe_message(f"Eliminado el formato {equipo_foto.descripcion}"),
            url=url_for("inv_equipos_fotos.detail", equipo_foto_id=equipo_foto.id),
        )
        bitacora.save()
        flash(bitacora.descripcion, "success")
    return redirect(url_for("inv_equipos_fotos.detail", equipo_foto_id=equipo_foto_id))


@inv_equipos_fotos.route("/inv_equipos_fotos/recuperar/<int:equipo_foto_id>")
@permission_required(MODULO, Permiso.MODIFICAR)
def recover(equipo_foto_id):
    """Recuperar CID Formato"""
    equipo_foto = INVEquipoFoto.query.get_or_404(equipo_foto_id)
    if equipo_foto.estatus == "B":
        equipo_foto.recover()
        bitacora = Bitacora(
            modulo=Modulo.query.filter_by(nombre=MODULO).first(),
            usuario=current_user,
            descripcion=safe_message(f"Recuperado el formato {equipo_foto.descripcion}"),
            url=url_for("inv_equipos_fotos.detail", equipo_foto_id=equipo_foto.id),
        )
        bitacora.save()
        flash(bitacora.descripcion, "success")
    return redirect(url_for("inv_equipos_fotos.detail", equipo_foto_id=equipo_foto_id))

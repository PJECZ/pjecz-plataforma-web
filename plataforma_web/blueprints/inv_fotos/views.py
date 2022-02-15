"""
INV FOTOS, vistas
"""
from datetime import datetime
from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required
from werkzeug.datastructures import CombinedMultiDict

from lib import datatables
from lib.safe_string import safe_string, safe_message
from lib.storage import GoogleCloudStorage, NotAllowedExtesionError, UnknownExtesionError, NotConfiguredError
from plataforma_web.blueprints.usuarios.decorators import permission_required

from plataforma_web.blueprints.bitacoras.models import Bitacora
from plataforma_web.blueprints.modulos.models import Modulo
from plataforma_web.blueprints.permisos.models import Permiso
from plataforma_web.blueprints.inv_fotos.models import INVFoto
from plataforma_web.blueprints.inv_equipos.models import INVEquipo

from plataforma_web.blueprints.inv_fotos.forms import INVFotoNewForm

MODULO = "INV FOTOS"
SUBDIRECTORIO = "inv fotos"

fotos = Blueprint("fotos", __name__, template_folder="templates")


@fotos.before_request
@login_required
@permission_required(MODULO, Permiso.VER)
def before_request():
    """Permiso por defecto"""


@fotos.route("/fotos/<int:foto_id>")
def detail(foto_id):
    """Detalle de un Soporte equipo"""
    foto = INVFoto.query.get_or_404(foto_id)
    return render_template(
        "fotos/detail.jinja2",
        foto=foto,
    )


@fotos.route("/fotos/nuevo/<int:equipo_id>", methods=["GET", "POST"])
@permission_required(MODULO, Permiso.CREAR)
def new(equipo_id):
    """Adjuntar Archivos al equipo"""
    equipo = INVEquipo.query.get_or_404(equipo_id)
    # archivo = INVEquipoFile
    detalle_url = url_for("inv_equipos.detail", equipo_id=equipo.id)
    if equipo.estatus != "A":
        flash("No puede adjuntar un archivo a un equipo eliminado.", "warning")
        return redirect(detalle_url)
    form = INVFotoNewForm(CombinedMultiDict((request.files, request.form)))
    if form.validate_on_submit():
        es_valido = True
        # Validar la descripción
        descripcion = safe_string(form.descripcion.data)
        if descripcion == "":
            flash("La descripción es requerida.", "warning")
            es_valido = False
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
            foto = INVFoto(
                equipo=equipo,
                descripcion=safe_string(descripcion),
            )
            foto.save()
            # Subir el archivo a la nube
            try:
                storage.set_filename(hashed_id=foto.encode_id(), description=descripcion)
                storage.upload(archivo.stream.read())
                foto.archivo = archivo.filename  # Conservar el nombre original
                foto.url = storage.url
                foto.save()
            except NotConfiguredError:
                flash("No se ha configurado el almacenamiento en la nube.", "warning")
            except Exception:
                flash("Error al subir el archivo.", "danger")
            # Registrar la acción en la bitácora
            bitacora = Bitacora(
                modulo=Modulo.query.filter_by(nombre=MODULO).first(),
                usuario=current_user,
                descripcion=safe_message(f"Subida de archivo {foto.archivo} al equipo {equipo.id}."),
                url=detalle_url,
            )
            bitacora.save()
            flash(bitacora.descripcion, "success")
            return redirect(bitacora.url)
    form.equipo.data = equipo.numero_inventario  # Read only
    return render_template("fotos/new.jinja2", form=form, equipo=equipo)

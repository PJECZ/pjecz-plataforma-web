"""
CID Formatos, vistas
"""
import datetime
from pathlib import Path

from flask import Blueprint, current_app, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required
from google.cloud import storage
from werkzeug.datastructures import CombinedMultiDict
from werkzeug.utils import secure_filename

from lib.safe_string import safe_message, safe_string
from plataforma_web.blueprints.usuarios.decorators import permission_required

from plataforma_web.blueprints.bitacoras.models import Bitacora
from plataforma_web.blueprints.cid_formatos.forms import CIDFormatoForm
from plataforma_web.blueprints.cid_formatos.models import CIDFormato
from plataforma_web.blueprints.cid_procedimientos.models import CIDProcedimiento
from plataforma_web.blueprints.modulos.models import Modulo
from plataforma_web.blueprints.permisos.models import Permiso

cid_formatos = Blueprint("cid_formatos", __name__, template_folder="templates")

MODULO = "CID FORMATOS"
SUBDIRECTORIO = "cid_formatos"

@cid_formatos.before_request
@login_required
@permission_required(MODULO, Permiso.VER)
def before_request():
    """Permiso por defecto"""


@cid_formatos.route("/cid_formatos")
def list_active():
    """Listado de CID Formatos activos"""
    return render_template(
        "cid_formatos/list.jinja2",
        cid_formatos=CIDFormato.query.filter_by(estatus="A").all(),
        titulo="Formatos",
        estatus="A",
    )


@cid_formatos.route("/cid_formatos/inactivos")
@permission_required(MODULO, Permiso.MODIFICAR)
def list_inactive():
    """Listado de CID Formatos inactivos"""
    return render_template(
        "cid_formatos/list.jinja2",
        cid_formatos=CIDFormato.query.filter_by(estatus="B").all(),
        titulo="Formatos inactivos",
        estatus="B",
    )


@cid_formatos.route("/cid_formatos/<int:cid_formato_id>")
def detail(cid_formato_id):
    """Detalle de un CID Formato"""
    cid_formato = CIDFormato.query.get_or_404(cid_formato_id)
    return render_template("cid_formatos/detail.jinja2", cid_formato=cid_formato)


@cid_formatos.route("/cid_formatos/nuevo/<int:cid_procedimiento_id>", methods=["GET", "POST"])
@permission_required(MODULO, Permiso.CREAR)
def new(cid_procedimiento_id):
    """Nuevo CID Formato"""
    # Validar procedimiento
    cid_procedimiento = CIDProcedimiento.query.get_or_404(cid_procedimiento_id)
    if cid_procedimiento.estatus != "A":
        flash("El procedmiento no es activo.", "warning")
        return redirect(url_for("cid_procedimientos.list_active"))
    # Si viene el formulario
    form = CIDFormatoForm()
    if form.validate_on_submit():
        es_valido = True
        # Validar la descripción
        descripcion = safe_string(form.descripcion.data)
        if descripcion == "":
            flash("La descripción es requerida.", "warning")
            es_valido = False
        # Validar el archivo
        archivo = request.files["archivo"]
        archivo_nombre = secure_filename(archivo.filename.lower())
        if "." not in archivo_nombre or archivo_nombre.rsplit(".", 1)[1] != "pdf":
            flash("No es un archivo PDF.", "warning")
            es_valido = False
        # Si es válido
        if es_valido:
            # Insertar el registro, para obtener el ID
            cid_formato = CIDFormato(
                procedimiento=cid_procedimiento,
                descripcion=descripcion,
            )
            cid_formato.save()
            # Definir el nombre del archivo
            ahora = datetime.datetime.now()
            ahora_str = ahora.strftime("%Y-%m-%d-%H%M%S")
            descripcion_corta_str = descripcion.replace(" ", "-")[:24]
            id_cifrado = cid_formato.encode_id()
            archivo_str = f"{ahora_str}-{descripcion_corta_str}-{id_cifrado}.pdf"
            # Definir la ruta en el deposito
            ruta_str = str(Path(SUBDIRECTORIO, archivo_str))
            # Subir el archivo
            deposito = current_app.config["CLOUD_STORAGE_DEPOSITO"]
            storage_client = storage.Client()
            bucket = storage_client.bucket(deposito)
            blob = bucket.blob(ruta_str)
            blob.upload_from_string(archivo.stream.read(), content_type="application/pdf")
            url = blob.public_url
            # Actualizar el registro con el nombre de archivo y la URL
            cid_formato.archivo = archivo_str
            cid_formato.url = url
            cid_formato.save()
            # Registrar la acción en la bitácora
            bitacora = Bitacora(
                modulo=Modulo.query.filter_by(nombre=MODULO).first(),
                usuario=current_user,
                descripcion=safe_message(f"Nuevo formato {cid_formato.descripcion}"),
                url=url_for("cid_formatos.detail", cid_formato_id=cid_formato.id),
            )
            bitacora.save()
            flash(bitacora.descripcion, "success")
            return redirect(bitacora.url)
    # Mostrar formulario
    form.procedimiento_titulo.data = cid_procedimiento.titulo_procedimiento  # Read only
    return render_template("cid_formatos/new.jinja2", form=form, cid_procedimiento=cid_procedimiento)


@cid_formatos.route("/cid_formatos/edicion/<int:cid_formato_id>", methods=["GET", "POST"])
@permission_required(MODULO, Permiso.MODIFICAR)
def edit(cid_formato_id):
    """Editar CID Formato"""
    cid_formato = CIDFormato.query.get_or_404(cid_formato_id)
    form = CIDFormatoForm()
    if form.validate_on_submit():
        cid_formato.descripcion = safe_string(form.descripcion.data)
        cid_formato.save()
        bitacora = Bitacora(
            modulo=Modulo.query.filter_by(nombre=MODULO).first(),
            usuario=current_user,
            descripcion=safe_message(f"Editado el formato {cid_formato.descripcion}"),
            url=url_for("cid_formatos.detail", cid_formato_id=cid_formato.id),
        )
        bitacora.save()
        flash(bitacora.descripcion, "success")
        return redirect(bitacora.url)
    form.procedimiento_titulo.data = cid_formato.procedimiento.titulo_procedimiento  # Read only
    form.descripcion.data = cid_formato.descripcion
    return render_template("cid_formatos/edit.jinja2", form=form, cid_formato=cid_formato)


@cid_formatos.route("/cid_formatos/eliminar/<int:cid_formato_id>")
@permission_required(MODULO, Permiso.MODIFICAR)
def delete(cid_formato_id):
    """Eliminar CID Formato"""
    cid_formato = CIDFormato.query.get_or_404(cid_formato_id)
    if cid_formato.estatus == "A":
        cid_formato.delete()
        bitacora = Bitacora(
            modulo=Modulo.query.filter_by(nombre=MODULO).first(),
            usuario=current_user,
            descripcion=safe_message(f"Eliminado el formato {cid_formato.descripcion}"),
            url=url_for("cid_formatos.detail", cid_formato_id=cid_formato.id),
        )
        bitacora.save()
        flash(bitacora.descripcion, "success")
    return redirect(url_for("cid_formatos.detail", cid_formato_id=cid_formato_id))


@cid_formatos.route("/cid_formatos/recuperar/<int:cid_formato_id>")
@permission_required(MODULO, Permiso.MODIFICAR)
def recover(cid_formato_id):
    """Recuperar CID Formato"""
    cid_formato = CIDFormato.query.get_or_404(cid_formato_id)
    if cid_formato.estatus == "B":
        cid_formato.recover()
        bitacora = Bitacora(
            modulo=Modulo.query.filter_by(nombre=MODULO).first(),
            usuario=current_user,
            descripcion=safe_message(f"Recuperado el formato {cid_formato.descripcion}"),
            url=url_for("cid_formatos.detail", cid_formato_id=cid_formato.id),
        )
        bitacora.save()
        flash(bitacora.descripcion, "success")
    return redirect(url_for("cid_formatos.detail", cid_formato_id=cid_formato_id))

"""
Inventarios Equipos Fotos, vistas
"""
import json
from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required
from werkzeug.datastructures import CombinedMultiDict

from lib.datatables import get_datatable_parameters, output_datatable_json
from lib.safe_string import safe_string, safe_message
from lib.storage import GoogleCloudStorage, NotAllowedExtesionError, UnknownExtesionError, NotConfiguredError

from plataforma_web.blueprints.bitacoras.models import Bitacora
from plataforma_web.blueprints.inv_equipos_fotos.models import InvEquipoFoto
from plataforma_web.blueprints.inv_equipos_fotos.forms import InvEquipoFotoNewForm
from plataforma_web.blueprints.inv_equipos.models import InvEquipo
from plataforma_web.blueprints.modulos.models import Modulo
from plataforma_web.blueprints.permisos.models import Permiso
from plataforma_web.blueprints.usuarios.decorators import permission_required

MODULO = "INV EQUIPOS FOTOS"
SUBDIRECTORIO = "inv_equipo_fotos"

inv_equipos_fotos = Blueprint("inv_equipos_fotos", __name__, template_folder="templates")


@inv_equipos_fotos.before_request
@login_required
@permission_required(MODULO, Permiso.VER)
def before_request():
    """Permiso por defecto"""


@inv_equipos_fotos.route("/inv_equipos_fotos/datatable_json", methods=["GET", "POST"])
def datatable_json():
    """DataTable JSON para listado de Equipo Foto"""
    # Tomar parámetros de Datatables
    draw, start, rows_per_page = get_datatable_parameters()
    # Consultar
    consulta = InvEquipoFoto.query
    if "estatus" in request.form:
        consulta = consulta.filter_by(estatus=request.form["estatus"])
    else:
        consulta = consulta.filter_by(estatus="A")
    if "inv_equipo_id" in request.form:
        consulta = consulta.filter_by(inv_equipo_id=request.form["inv_equipo_id"])
    registros = consulta.order_by(InvEquipoFoto.id).offset(start).limit(rows_per_page).all()
    total = consulta.count()
    # Elaborar datos para DataTable
    data = []
    for resultado in registros:
        data.append(
            {
                "detalle": {
                    "nombre": resultado.archivo,
                    "url": url_for("inv_equipos_fotos.detail", inv_equipo_foto_id=resultado.id),
                },
                "descripcion": resultado.descripcion,
            }
        )
    # Entregar JSON
    return output_datatable_json(draw, total, data)


@inv_equipos_fotos.route("/inv_equipos_fotos")
def list_active():
    """Listado de Equipos fotos activos"""
    return render_template(
        "inv_equipos_fotos/list.jinja2",
        filtros=json.dumps({"estatus": "A"}),
        titulo="Equipos fotos",
        estatus="A",
    )


@inv_equipos_fotos.route("/inv_equipos_fotos/inactivos")
@permission_required(MODULO, Permiso.MODIFICAR)
def list_inactive():
    """Listado de Equipos fotos inactivos"""
    return render_template(
        "inv_equipos_fotos/list.jinja2",
        filtros=json.dumps({"estatus": "B"}),
        titulo="Equipos fotos inactivos",
        estatus="B",
    )


@inv_equipos_fotos.route("/inv_equipos_fotos/<int:inv_equipo_foto_id>")
def detail(inv_equipo_foto_id):
    """Detalle de un Soporte equipo"""
    inv_equipo_foto = InvEquipoFoto.query.get_or_404(inv_equipo_foto_id)
    return render_template(
        "inv_equipos_fotos/detail.jinja2",
        inv_equipo_foto=inv_equipo_foto,
    )


@inv_equipos_fotos.route("/inv_equipos_fotos/nuevo/<int:inv_equipo_id>", methods=["GET", "POST"])
@permission_required(MODULO, Permiso.CREAR)
def new(inv_equipo_id):
    """Adjuntar Archivos al equipo"""
    inv_equipo = InvEquipo.query.get_or_404(inv_equipo_id)
    # archivo = InvEquipoFile
    detalle_url = url_for("inv_equipos.detail", inv_equipo_id=inv_equipo.id)
    if inv_equipo.estatus != "A":
        flash("No puede adjuntar un archivo a un equipo eliminado.", "warning")
        return redirect(detalle_url)
    form = InvEquipoFotoNewForm(CombinedMultiDict((request.files, request.form)))
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
            inv_equipo_foto = InvEquipoFoto(
                inv_equipo=inv_equipo,
                descripcion=safe_string(descripcion),
            )
            inv_equipo_foto.save()
            # Subir el archivo a la nube
            try:
                storage.set_filename(hashed_id=inv_equipo_foto.encode_id(), description=descripcion)
                storage.upload(archivo.stream.read())
                inv_equipo_foto.archivo = archivo.filename  # Conservar el nombre original
                inv_equipo_foto.url = storage.url
                inv_equipo_foto.save()
            except NotConfiguredError:
                flash("No se ha configurado el almacenamiento en la nube.", "warning")
            except Exception as err:
                flash(f"{err}Error al subir el archivo.", "danger")
            # Registrar la acción en la bitácora
            bitacora = Bitacora(
                modulo=Modulo.query.filter_by(nombre=MODULO).first(),
                usuario=current_user,
                descripcion=safe_message(f"Subida de archivo {inv_equipo_foto.archivo} al equipo {inv_equipo.id}."),
                url=detalle_url,
            )
            bitacora.save()
            flash(bitacora.descripcion, "success")
            return redirect(bitacora.url)
    return render_template("inv_equipos_fotos/new.jinja2", form=form, inv_equipo=inv_equipo)


@inv_equipos_fotos.route("/inv_equipos_fotos/eliminar/<int:inv_equipos_foto_id>")
@permission_required(MODULO, Permiso.MODIFICAR)
def delete(inv_equipos_foto_id):
    """Eliminar Equipos Fotos"""
    inv_equipo_foto = InvEquipoFoto.query.get_or_404(inv_equipos_foto_id)
    if inv_equipo_foto.estatus == "A":
        inv_equipo_foto.delete()
        bitacora = Bitacora(
            modulo=Modulo.query.filter_by(nombre=MODULO).first(),
            usuario=current_user,
            descripcion=safe_message(f"Eliminado Equipos Fotos {inv_equipo_foto.descripcion}"),
            url=url_for("inv_equipos_fotos.detail", inv_equipo_foto_id=inv_equipo_foto.id),
        )
        bitacora.save()
        flash(bitacora.descripcion, "success")
    return redirect(url_for("inv_equipos_fotos.detail", inv_equipos_foto_id=inv_equipo_foto.id))


@inv_equipos_fotos.route("/inv_equipos_fotos/recuperar/<int:inv_equipo_foto_id>")
@permission_required(MODULO, Permiso.MODIFICAR)
def recover(inv_equipo_foto_id):
    """Recuperar Equipo Foto"""
    inv_equipo_foto = InvEquipoFoto.query.get_or_404(inv_equipo_foto_id)
    if inv_equipo_foto.estatus == "B":
        inv_equipo_foto.recover()
        bitacora = Bitacora(
            modulo=Modulo.query.filter_by(nombre=MODULO).first(),
            usuario=current_user,
            descripcion=safe_message(f"Recuperado Equipo Foto {inv_equipo_foto.descripcion}"),
            url=url_for("inv_equipos_fotos.detail", inv_equipo_foto_id=inv_equipo_foto.id),
        )
        bitacora.save()
        flash(bitacora.descripcion, "success")
    return redirect(url_for("inv_equipos_fotos.detail", inv_equipo_foto_id=inv_equipo_foto.id))

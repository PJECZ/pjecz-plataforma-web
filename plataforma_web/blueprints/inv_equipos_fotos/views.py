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
from plataforma_web.blueprints.usuarios.decorators import permission_required

from plataforma_web.blueprints.bitacoras.models import Bitacora
from plataforma_web.blueprints.modulos.models import Modulo
from plataforma_web.blueprints.permisos.models import Permiso
from plataforma_web.blueprints.inv_equipos_fotos.models import InvEquipoFoto
from plataforma_web.blueprints.inv_equipos.models import InvEquipo

from plataforma_web.blueprints.inv_equipos_fotos.forms import InvEquipoFotoNewForm

MODULO = "INV EQUIPOS FOTOS"
SUBDIRECTORIO = "inv equipo_fotos"

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
    if "equipo_id" in request.form:
        consulta = consulta.filter_by(inv_equipo_id=request.form["equipo_id"])
    registros = consulta.order_by(InvEquipoFoto.id).offset(start).limit(rows_per_page).all()
    total = consulta.count()
    # Elaborar datos para DataTable
    data = []
    for resultado in registros:
        data.append(
            {
                "detalle": {
                    "nombre": resultado.archivo,
                    "url": url_for("inv_equipos_fotos.detail", equipo_foto_id=resultado.id),
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


@inv_equipos_fotos.route("/inv_equipos_fotos/<int:equipo_foto_id>")
def detail(equipo_foto_id):
    """Detalle de un Soporte equipo"""
    equipo_foto = InvEquipoFoto.query.get_or_404(equipo_foto_id)
    return render_template(
        "inv_equipos_fotos/detail.jinja2",
        equipo_foto=equipo_foto,
    )


@inv_equipos_fotos.route("/inv_equipos_fotos/nuevo/<int:equipo_id>", methods=["GET", "POST"])
@permission_required(MODULO, Permiso.CREAR)
def new(equipo_id):
    """Adjuntar Archivos al equipo"""
    equipo = InvEquipo.query.get_or_404(equipo_id)
    # archivo = InvEquipoFile
    detalle_url = url_for("inv_equipos.detail", equipo_id=equipo.id)
    if equipo.estatus != "A":
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
            equipo_foto = InvEquipoFoto(
                inv_equipo=equipo,
                descripcion=safe_string(descripcion),
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
                descripcion=safe_message(f"Subida de archivo {equipo_foto.archivo} al equipo {equipo.id}."),
                url=detalle_url,
            )
            bitacora.save()
            flash(bitacora.descripcion, "success")
            return redirect(bitacora.url)
    return render_template("inv_equipos_fotos/new.jinja2", form=form, equipo=equipo)
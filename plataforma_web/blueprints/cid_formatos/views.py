"""
CID Formatos, vistas
"""
import json
from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required
from werkzeug.datastructures import CombinedMultiDict

from lib.datatables import get_datatable_parameters, output_datatable_json
from lib.safe_string import safe_message, safe_string
from lib.storage import GoogleCloudStorage, NotAllowedExtesionError, UnknownExtesionError, NotConfiguredError

from plataforma_web.blueprints.bitacoras.models import Bitacora
from plataforma_web.blueprints.cid_formatos.forms import CIDFormatoForm
from plataforma_web.blueprints.cid_formatos.models import CIDFormato
from plataforma_web.blueprints.cid_procedimientos.models import CIDProcedimiento
from plataforma_web.blueprints.modulos.models import Modulo
from plataforma_web.blueprints.permisos.models import Permiso
from plataforma_web.blueprints.usuarios.decorators import permission_required

cid_formatos = Blueprint("cid_formatos", __name__, template_folder="templates")

MODULO = "CID FORMATOS"

SUBDIRECTORIO = "cid_formatos"

# Roles que deben estar en la base de datos
ROL_COORDINADOR = "SICGD COORDINADOR"
ROL_DIRECTOR_JEFE = "SICGD DIRECTOR O JEFE"
ROL_DUENO_PROCESO = "SICGD DUENO DE PROCESO"
ROL_INVOLUCRADO = "SICGD INVOLUCRADO"


@cid_formatos.before_request
@login_required
@permission_required(MODULO, Permiso.VER)
def before_request():
    """Permiso por defecto"""


@cid_formatos.route("/cid_formatos/datatable_json", methods=["GET", "POST"])
def datatable_json():
    """DataTable JSON para listado de Formatos"""
    # Tomar parámetros de Datatables
    draw, start, rows_per_page = get_datatable_parameters()
    # Consultar
    consulta = CIDFormato.query
    if "estatus" in request.form:
        consulta = consulta.filter_by(estatus=request.form["estatus"])
    else:
        consulta = consulta.filter_by(estatus="A")
    if "descripcion" in request.form:
        consulta = consulta.filter(CIDFormato.descripcion.contains(safe_string(request.form["descripcion"])))
    if "cid_procedimiento" in request.form:
        consulta = consulta.join(CIDProcedimiento)
        consulta = consulta.filter(CIDProcedimiento.titulo_procedimiento.contains(safe_string(request.form["cid_procedimiento"])))
    if "seguimiento" in request.form:
        consulta = consulta.join(CIDProcedimiento)
        consulta = consulta.filter(CIDProcedimiento.seguimiento == request.form["seguimiento"])
    if "usuario_id" in request.form:
        consulta = consulta.join(CIDProcedimiento)
        consulta = consulta.filter(CIDProcedimiento.usuario_id == request.form["usuario_id"])
    registros = consulta.order_by(CIDFormato.id.desc()).offset(start).limit(rows_per_page).all()
    total = consulta.count()
    # Elaborar datos para DataTable
    data = []
    for resultado in registros:
        data.append(
            {
                "detalle": {
                    "id": resultado.id,
                    "url": url_for("cid_formatos.detail", cid_formato_id=resultado.id),
                },
                "cid_procedimiento": {
                    "titulo_procedimiento": resultado.procedimiento.titulo_procedimiento,
                    "url": url_for("cid_procedimientos.detail", cid_procedimiento_id=resultado.procedimiento.id) if current_user.can_view("CID PROCEDIMIENTOS") else "",
                },
                "descripcion": resultado.descripcion,
                "descargar": {
                    "archivo": resultado.archivo,
                    "url": resultado.url,
                },
                "autoridad": resultado.procedimiento.autoridad.clave,
            }
        )
    # Entregar JSON
    return output_datatable_json(draw, total, data)


@cid_formatos.route("/cid_formatos")
def list_active():
    """Listado por defecto de Formatos"""
    # si es administrador, mostrar todos los Formatos
    if current_user.can_admin(MODULO):
        return render_template(
            "cid_formatos/list.jinja2",
            titulo="Todos los Formatos",
            filtros=json.dumps({"estatus": "A"}),
            estatus="A",
        )
    # Consultar los roles del usuario
    current_user_roles = current_user.get_roles()
    # Si es involucrado, mostrar todos los formatos
    return render_template(
        "cid_formatos/list.jinja2",
        filtros=json.dumps({"estatus": "A", "seguimiento": "AUTORIZADO"}),
        titulo="Formatos Autorizados",
        estatus="A",
        show_button_list_owned=ROL_COORDINADOR in current_user_roles or ROL_DIRECTOR_JEFE in current_user_roles or ROL_DUENO_PROCESO in current_user_roles,
        show_button_list_all=ROL_COORDINADOR in current_user_roles,
    )


# List Formatos autorizados
@cid_formatos.route("/cid_formatos/autorizados")
def list_authorized():
    """Listado de Formatos autorizados"""
    current_user_roles = current_user.get_roles()
    return render_template(
        "cid_formatos/list.jinja2",
        filtros=json.dumps({"estatus": "A", "seguimiento": "AUTORIZADO"}),
        titulo="Formatos Autorizados",
        estatus="A",
        show_button_list_owned=current_user.can_admin(MODULO) or ROL_COORDINADOR in current_user_roles or ROL_DIRECTOR_JEFE in current_user_roles or ROL_DUENO_PROCESO in current_user_roles,
        show_button_list_all=current_user.can_admin(MODULO) or ROL_COORDINADOR in current_user_roles,
    )


@cid_formatos.route("/cid_formatos/propios")
def list_owned():
    """Listado de Formatos propios"""
    current_user_roles = current_user.get_roles()  # Si es administrador, coordinador, director o jefe o dueno de proceso, mostrar los procedimientos propios
    if current_user.can_admin(MODULO) or ROL_COORDINADOR in current_user_roles or ROL_DIRECTOR_JEFE in current_user_roles or ROL_DUENO_PROCESO in current_user_roles:
        return render_template(
            "cid_formatos/list.jinja2",
            filtros=json.dumps({"estatus": "A", "usuario_id": current_user.id}),
            titulo="Formatos propios",
            estatus="A",
            show_button_list_owned=True,
            show_button_list_all=current_user.can_admin(MODULO) or ROL_COORDINADOR in current_user_roles,
        )
    # Si no, redirigir a la lista general
    return redirect(url_for("cid_formatos.list_active"))


@cid_formatos.route("/cid_formatos/todos")
def list_all():
    """Listado de Todos los Formatos"""
    current_user_roles = current_user.get_roles()
    # Si es administrador, coordinador, mostrar todos los formatos
    if current_user.can_admin(MODULO) or ROL_COORDINADOR in current_user_roles:
        return render_template(
            "cid_formatos/list.jinja2",
            filtros=json.dumps({"estatus": "A"}),
            titulo="Todos los Formatos",
            estatus="A",
            show_button_list_owned=True,
            show_button_list_all=True,
        )
    # Si no, redirigir a la lista general
    return redirect(url_for("cid_formatos.list_active"))


@cid_formatos.route("/cid_formatos/inactivos")
@permission_required(MODULO, Permiso.MODIFICAR)
def list_inactive():
    """Listado de Formatos propios eliminados"""
    return render_template(
        "cid_formatos/list.jinja2",
        filtros=json.dumps({"estatus": "B", "usuario_id": current_user.id}),
        titulo="Formatos propios eliminados",
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
    form = CIDFormatoForm(CombinedMultiDict((request.files, request.form)))
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
            cid_formato = CIDFormato(
                procedimiento=cid_procedimiento,
                descripcion=descripcion,
            )
            cid_formato.save()
            # Subir el archivo a la nube
            try:
                storage.set_filename(hashed_id=cid_formato.encode_id(), description=descripcion)
                storage.upload(archivo.stream.read())
                cid_formato.archivo = archivo.filename  # Conservar el nombre original
                cid_formato.url = storage.url
                cid_formato.save()
            except NotConfiguredError:
                flash("No se ha configurado el almacenamiento en la nube.", "warning")
            except Exception:
                flash("Error al subir el archivo.", "danger")
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

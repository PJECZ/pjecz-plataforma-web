"""
Usuarios Documentos, vistas
"""

import json
from flask import Blueprint, flash, redirect, render_template, request, url_for, current_app, make_response, abort
from flask_login import current_user, login_required
from werkzeug.datastructures import CombinedMultiDict

from lib.datatables import get_datatable_parameters, output_datatable_json
from lib.safe_string import safe_string, safe_message, safe_curp
from lib.storage import GoogleCloudStorage, NotAllowedExtesionError, UnknownExtesionError, NotConfiguredError
from sqlalchemy import or_
from lib.google_cloud_storage import get_blob_name_from_url, get_file_from_gcs
from lib.exceptions import MyBucketNotFoundError, MyFileNotFoundError, MyNotValidParamError


from plataforma_web.blueprints.bitacoras.models import Bitacora
from plataforma_web.blueprints.modulos.models import Modulo
from plataforma_web.blueprints.permisos.models import Permiso
from plataforma_web.blueprints.usuarios.decorators import permission_required
from plataforma_web.blueprints.usuarios_datos.models import UsuarioDato

from plataforma_web.blueprints.usuarios.models import Usuario
from plataforma_web.blueprints.usuarios_solicitudes.models import UsuarioSolicitud
from plataforma_web.blueprints.usuarios_documentos.models import UsuarioDocumento
from plataforma_web.blueprints.usuarios_datos.forms import (
    UsuarioDatoEditIdentificacionForm,
    UsuarioDatoEditActaNacimientoForm,
    UsuarioDatoEditDomicilioForm,
    UsuarioDatoEditCurpForm,
    UsuarioDatoEditCPFiscalForm,
    UsuarioDatoEditCurriculumForm,
    UsuarioDatoEditEstudiosForm,
    UsuarioDatoEditEsMadreForm,
    UsuarioDatoEditEstadoCivilForm,
    UsuarioDatoEditEstadoCuentaForm,
    UsuarioDatoValidateForm,
)

MODULO = "USUARIOS DATOS"
SUBDIRECTORIO = "usuarios_documentos"

CAMPOS = [
    "IDENTIFICACION",
    "ACTA NACIMIENTO",
    "DOMICILIO",
    "CURP",
    "CP FISCAL",
    "CURRICULUM",
    "ESTUDIOS",
    "ES MADRE",
    "ESTADO CIVIL",
    "ESTADO CUENTA",
    "TELEFONO",
    "EMAIL",
]

usuarios_datos = Blueprint("usuarios_datos", __name__, template_folder="templates")


@usuarios_datos.before_request
@login_required
@permission_required(MODULO, Permiso.VER)
def before_request():
    """Permiso por defecto"""


@usuarios_datos.route("/usuarios_datos/datatable_json", methods=["GET", "POST"])
@permission_required(MODULO, Permiso.ADMINISTRAR)
def datatable_json():
    """DataTable JSON para listado de Usuarios Datos"""
    # Tomar parámetros de Datatables
    draw, start, rows_per_page = get_datatable_parameters()
    # Consultar
    consulta = UsuarioDato.query
    if "estatus" in request.form:
        consulta = consulta.filter_by(estatus=request.form["estatus"])
    else:
        consulta = consulta.filter_by(estatus="A")
    if "nombre" in request.form:
        palabras = safe_string(request.form["nombre"]).split(" ")
        consulta = consulta.join(Usuario)
        for palabra in palabras:
            consulta = consulta.filter(or_(Usuario.nombres.contains(palabra), Usuario.apellido_paterno.contains(palabra), Usuario.apellido_materno.contains(palabra)))
    if "curp" in request.form:
        consulta = consulta.join(Usuario)
        consulta = consulta.filter(Usuario.curp.contains(safe_string(request.form["curp"])))
    if "estado" in request.form and not "campo" in request.form:
        consulta = consulta.filter_by(estado_general=request.form["estado"])
    if "estado" in request.form and "campo" in request.form:
        if request.form["campo"] == "IDENTIFICACION":
            consulta = consulta.filter_by(estado_identificacion=request.form["estado"])
        elif request.form["campo"] == "ACTA NACIMIENTO":
            consulta = consulta.filter_by(estado_acta_nacimiento=request.form["estado"])
        elif request.form["campo"] == "DOMICILIO":
            consulta = consulta.filter_by(estado_domicilio=request.form["estado"])
        elif request.form["campo"] == "CURP":
            consulta = consulta.filter_by(estado_curp=request.form["estado"])
        elif request.form["campo"] == "CP FISCAL":
            consulta = consulta.filter_by(estado_cp_fiscal=request.form["estado"])
        elif request.form["campo"] == "CURRICULUM":
            consulta = consulta.filter_by(estado_curriculum=request.form["estado"])
        elif request.form["campo"] == "ESTUDIOS":
            consulta = consulta.filter_by(estado_estudios=request.form["estado"])
        elif request.form["campo"] == "ES MADRE":
            consulta = consulta.filter_by(estado_es_madre=request.form["estado"])
        elif request.form["campo"] == "ESTADO CIVIL":
            consulta = consulta.filter_by(estado_estado_civil=request.form["estado"])
        elif request.form["campo"] == "ESTADO CUENTA":
            consulta = consulta.filter_by(estado_estado_cuenta=request.form["estado"])
        elif request.form["campo"] == "TELEFONO":
            consulta = consulta.filter_by(estado_telefono=request.form["estado"])
        elif request.form["campo"] == "EMAIL":
            consulta = consulta.filter_by(estado_email=request.form["estado"])
    # Resultado
    registros = consulta.order_by(UsuarioDato.modificado.desc()).offset(start).limit(rows_per_page).all()
    total = consulta.count()
    # Elaborar datos para DataTable
    data = []
    for resultado in registros:
        data.append(
            {
                "detalle": {
                    "id": resultado.id,
                    "url": url_for("usuarios_datos.detail", usuario_dato_id=resultado.id),
                },
                "email": resultado.usuario.email,
                "fecha": resultado.modificado.strftime("%Y-%m-%d %H:%M"),
                "nombre": {
                    "nombre": resultado.usuario.nombre,
                    "url": url_for("usuarios_datos.detail", usuario_dato_id=resultado.id),
                },
                "curp": resultado.usuario.curp,
                "estado": resultado.estado_general,
            }
        )
    # Entregar JSON
    return output_datatable_json(draw, total, data)


@usuarios_datos.route("/usuarios_datos")
@permission_required(MODULO, Permiso.ADMINISTRAR)
def list_active():
    """Listado de Usuarios Datos activos"""
    return render_template(
        "usuarios_datos/list.jinja2",
        filtros=json.dumps({"estatus": "A"}),
        titulo="Documentos Personales",
        estatus="A",
        estados=UsuarioDato.VALIDACIONES,
        campos=CAMPOS,
    )


@usuarios_datos.route("/usuarios_datos/inactivos")
@permission_required(MODULO, Permiso.ADMINISTRAR)
def list_inactive():
    """Listado de Usuarios Datos inactivos"""
    return render_template(
        "usuarios_datos/list.jinja2",
        filtros=json.dumps({"estatus": "B"}),
        titulo="Documentos Personales inactivos",
        estatus="B",
        estados=UsuarioDato.VALIDACIONES,
        campos=CAMPOS,
    )


@usuarios_datos.route("/usuarios_datos/<int:usuario_dato_id>")
def detail(usuario_dato_id):
    """Detalle de un Usuario Datos"""
    usuario_dato = UsuarioDato.query.get_or_404(usuario_dato_id)
    if current_user == usuario_dato.usuario:
        return render_template("usuarios_datos/detail.jinja2", usuario_dato=usuario_dato)
    if current_user.can_admin(MODULO):
        return render_template("usuarios_datos/detail_admin.jinja2", usuario_dato=usuario_dato)
    return redirect(url_for("sistemas.start"))


@usuarios_datos.route("/usuarios_datos/nuevo", methods=["GET", "POST"])
@permission_required(MODULO, Permiso.CREAR)
def new():
    """Nuevo Usuario Datos vacíos o redirección a detalle"""
    # Comprobamos si el usuario es una persona verificando si tiene CURP
    try:
        safe_curp(current_user.curp)
    except ValueError:
        flash("CURP no válida, no puede ingresar a este módulo sin una CURP.", "warning")
        return redirect(url_for("sistemas.start"))
    # Buscar si el usuario ya tiene un registro previo
    usuario_dato = UsuarioDato.query.filter_by(usuario_id=current_user.id).first()
    # Si no cuenta con un registro previo, crear uno nuevo vacío
    if usuario_dato is None:
        usuario_dato = UsuarioDato(usuario=current_user).save()
    # Redirigirlo al detalle
    return redirect(url_for("usuarios_datos.detail", usuario_dato_id=usuario_dato.id))


@usuarios_datos.route("/usuarios_datos/editar/identificacion/<int:usuario_dato_id>", methods=["GET", "POST"])
@permission_required(MODULO, Permiso.MODIFICAR)
def edit_identificacion(usuario_dato_id):
    """Edición de la identificación oficial"""
    usuario_dato = UsuarioDato.query.get_or_404(usuario_dato_id)
    # Validar si el usuario actual es el correcto
    if usuario_dato.usuario_id != current_user.id:
        return redirect(url_for("sistemas.start"))
    # Extraemos el archivo adjunto para previsualizarlo
    usuario_documento = UsuarioDocumento.query.filter_by(id=usuario_dato.adjunto_identificacion_id).first()
    archivo_prev = None
    if usuario_documento and usuario_documento.url.endswith(".pdf"):
        archivo_prev = usuario_documento.url
    # Formulario de edición
    form = UsuarioDatoEditIdentificacionForm(CombinedMultiDict((request.files, request.form)))
    if form.validate_on_submit():
        es_valido = True
        archivo = request.files["archivo"]
        storage = GoogleCloudStorage(
            base_directory=SUBDIRECTORIO,
            bucket_name=current_app.config["CLOUD_STORAGE_DEPOSITO_USUARIOS"],
        )
        try:
            storage.set_content_type(archivo.filename)
        except NotAllowedExtesionError:
            flash("Tipo de archivo no permitido.", "warning")
            es_valido = False
        except UnknownExtesionError:
            flash("Tipo de archivo desconocido.", "warning")
            es_valido = False
        # Validar el tipo de extension
        if archivo.filename.endswith(".pdf"):
            es_valido = True
        else:
            flash("Tipo de archivo no permitido. Solo se permiten *.pdf", "warning")
            es_valido = False
        # Si es válido
        if es_valido:
            # Eliminar el archivo previo si lo hay
            if usuario_documento:
                usuario_documento.delete()
            # Insertar el registro, para obtener el ID
            usuario_documento = UsuarioDocumento(
                descripcion="Identificación Oficial",
            )
            usuario_documento.save()
            # Subir el archivo a la nube
            try:
                storage.set_filename(hashed_id=usuario_documento.encode_id(), description=usuario_documento.descripcion)
                storage.upload(archivo.stream.read())
                usuario_documento.url = storage.url
                usuario_dato.estado_identificacion = "POR VALIDAR"
                usuario_dato.estado_general = actualizar_estado_general(usuario_dato)
                usuario_dato.adjunto_identificacion_id = usuario_documento.id
                usuario_dato.save()
            except NotConfiguredError:
                flash("No se ha configurado el almacenamiento en la nube.", "warning")
                es_valido = False
            except Exception as err:
                flash(f"{err}Error al subir el archivo.", "danger")
                es_valido = False
        if es_valido:
            # mensaje de confirmación de guardado
            flash("Ha modificado su identificación oficial correctamente, espere a que sea validada", "success")
            return redirect(url_for("usuarios_datos.detail", usuario_dato_id=usuario_dato.id))
        else:
            flash("Ha ocurrido un problema y su información no ha sido guardada", "warning")
    # Renderiza la página de edición
    return render_template("usuarios_datos/edit_identificacion.jinja2", form=form, usuario_dato=usuario_dato, archivo=archivo_prev)


@usuarios_datos.route("/usuarios_datos/editar/acta_nacimiento/<int:usuario_dato_id>", methods=["GET", "POST"])
@permission_required(MODULO, Permiso.MODIFICAR)
def edit_acta_nacimiento(usuario_dato_id):
    """Edición del Acta de nacimiento"""
    usuario_dato = UsuarioDato.query.get_or_404(usuario_dato_id)
    # Validar si el usuario actual es el correcto
    if usuario_dato.usuario_id != current_user.id:
        return redirect(url_for("sistemas.start"))
    # Extraemos el archivo adjunto para previsualizarlo
    usuario_documento = UsuarioDocumento.query.filter_by(id=usuario_dato.adjunto_acta_nacimiento_id).first()
    archivo_prev = None
    if usuario_documento and usuario_documento.url.endswith(".pdf"):
        archivo_prev = usuario_documento.url
    # Formulario
    form = UsuarioDatoEditActaNacimientoForm(CombinedMultiDict((request.files, request.form)))
    if form.validate_on_submit():
        archivo = request.files["archivo"]
        # Si no envía cambios en archivo
        if archivo.filename == "":
            # Revisar que ya este cargada una adjunto previamente
            if archivo_prev is not None:
                usuario_dato.estado_acta_nacimiento = "POR VALIDAR"
                usuario_dato.estado_general = actualizar_estado_general(usuario_dato)
                usuario_dato.fecha_nacimiento = form.fecha_nacimiento.data
                usuario_dato.save()
                # Mensaje de resultado positivo
                flash("Ha modificado su Acta de Nacimiento correctamente, espere a que sea validada", "success")
                return redirect(url_for("usuarios_datos.detail", usuario_dato_id=usuario_dato.id))
            else:
                flash("Debe cargar un archivo adjunto.", "warning")
        else:
            es_valido = True
            storage = GoogleCloudStorage(
                base_directory=SUBDIRECTORIO,
                bucket_name=current_app.config["CLOUD_STORAGE_DEPOSITO_USUARIOS"],
            )
            try:
                storage.set_content_type(archivo.filename)
            except NotAllowedExtesionError:
                flash("Tipo de archivo no permitido.", "warning")
                es_valido = False
            except UnknownExtesionError:
                flash("Tipo de archivo desconocido.", "warning")
                es_valido = False
            # Validar el tipo de extension
            if archivo.filename.endswith(".pdf"):
                es_valido = True
            else:
                flash("Tipo de archivo no permitido. Solo se permiten *.pdf", "warning")
                es_valido = False
            # Si es válido
            if es_valido:
                # Eliminar el archivo previo si lo hay
                if usuario_documento:
                    usuario_documento.delete()
                # Insertar el registro, para obtener el ID
                usuario_documento = UsuarioDocumento(
                    descripcion="Acta Nacimiento",
                )
                usuario_documento.save()
                # Subir el archivo a la nube
                try:
                    storage.set_filename(hashed_id=usuario_documento.encode_id(), description=usuario_documento.descripcion)
                    storage.upload(archivo.stream.read())
                    usuario_documento.url = storage.url
                    usuario_dato.estado_acta_nacimiento = "POR VALIDAR"
                    usuario_dato.estado_general = actualizar_estado_general(usuario_dato)
                    usuario_dato.adjunto_acta_nacimiento_id = usuario_documento.id
                    usuario_dato.fecha_nacimiento = form.fecha_nacimiento.data
                    usuario_dato.save()
                except NotConfiguredError:
                    flash("No se ha configurado el almacenamiento en la nube.", "warning")
                    es_valido = False
                except Exception as err:
                    flash(f"{err}Error al subir el archivo.", "danger")
                    es_valido = False
            if es_valido:
                # Mensaje de resultado positivo
                flash("Ha modificado su Acta de Nacimiento correctamente, espere a que sea validada", "success")
                return redirect(url_for("usuarios_datos.detail", usuario_dato_id=usuario_dato.id))
            else:
                flash("Ha ocurrido un problema y su información no ha sido guardada", "warning")
    # Precargar datos anteriores
    form.fecha_nacimiento.data = usuario_dato.fecha_nacimiento
    # Renderiza el formulario de Edición
    return render_template("usuarios_datos/edit_acta_nacimiento.jinja2", form=form, usuario_dato=usuario_dato, archivo=archivo_prev)


@usuarios_datos.route("/usuarios_datos/editar/domicilio/<int:usuario_dato_id>", methods=["GET", "POST"])
@permission_required(MODULO, Permiso.MODIFICAR)
def edit_domicilio(usuario_dato_id):
    """Edición del Acta de nacimiento"""
    usuario_dato = UsuarioDato.query.get_or_404(usuario_dato_id)
    # Validar si el usuario actual es el correcto
    if usuario_dato.usuario_id != current_user.id:
        return redirect(url_for("sistemas.start"))
    # Extraemos el archivo adjunto para previsualizarlo
    usuario_documento = UsuarioDocumento.query.filter_by(id=usuario_dato.adjunto_domicilio_id).first()
    archivo_prev = None
    if usuario_documento and usuario_documento.url.endswith(".pdf"):
        archivo_prev = usuario_documento.url
    # Formulario
    form = UsuarioDatoEditDomicilioForm(CombinedMultiDict((request.files, request.form)))
    if form.validate_on_submit():
        archivo = request.files["archivo"]
        # Si no envía cambios en archivo
        if archivo.filename == "":
            # Revisar que ya este cargada una adjunto previamente
            if archivo_prev is not None:
                usuario_dato.estado_domicilio = "POR VALIDAR"
                usuario_dato.estado_general = actualizar_estado_general(usuario_dato)
                usuario_dato.domicilio_calle = safe_string(form.calle.data)
                usuario_dato.domicilio_numero_ext = safe_string(form.numero_exterior.data)
                usuario_dato.domicilio_numero_int = safe_string(form.numero_interior.data)
                usuario_dato.domicilio_colonia = safe_string(form.colonia.data)
                usuario_dato.domicilio_ciudad = safe_string(form.ciudad.data)
                usuario_dato.domicilio_estado = safe_string(form.estado.data)
                usuario_dato.domicilio_cp = form.codigo_postal.data
                usuario_dato.save()
                # Mensaje de resultado positivo
                flash("Ha modificado su Domicilio correctamente, espere a que sea validada", "success")
                return redirect(url_for("usuarios_datos.detail", usuario_dato_id=usuario_dato.id))
            else:
                flash("Debe cargar un archivo adjunto.", "warning")
        else:
            es_valido = True
            storage = GoogleCloudStorage(
                base_directory=SUBDIRECTORIO,
                bucket_name=current_app.config["CLOUD_STORAGE_DEPOSITO_USUARIOS"],
            )
            try:
                storage.set_content_type(archivo.filename)
            except NotAllowedExtesionError:
                flash("Tipo de archivo no permitido.", "warning")
                es_valido = False
            except UnknownExtesionError:
                flash("Tipo de archivo desconocido.", "warning")
                es_valido = False
            # Validar el tipo de extension
            if archivo.filename.endswith(".pdf"):
                es_valido = True
            else:
                flash("Tipo de archivo no permitido. Solo se permiten *.pdf", "warning")
                es_valido = False
            # Si es válido
            if es_valido:
                # Eliminar el archivo previo si lo hay
                if usuario_documento:
                    usuario_documento.delete()
                # Insertar el registro, para obtener el ID
                usuario_documento = UsuarioDocumento(
                    descripcion="Comprobante Domicilio",
                )
                usuario_documento.save()
                # Subir el archivo a la nube
                try:
                    storage.set_filename(hashed_id=usuario_documento.encode_id(), description=usuario_documento.descripcion)
                    storage.upload(archivo.stream.read())
                    usuario_documento.url = storage.url
                    usuario_dato.estado_domicilio = "POR VALIDAR"
                    usuario_dato.estado_general = actualizar_estado_general(usuario_dato)
                    usuario_dato.adjunto_domicilio_id = usuario_documento.id
                    usuario_dato.domicilio_calle = safe_string(form.calle.data)
                    usuario_dato.domicilio_numero_ext = safe_string(form.numero_exterior.data)
                    usuario_dato.domicilio_numero_int = safe_string(form.numero_interior.data)
                    usuario_dato.domicilio_colonia = safe_string(form.colonia.data)
                    usuario_dato.domicilio_ciudad = safe_string(form.ciudad.data)
                    usuario_dato.domicilio_estado = safe_string(form.estado.data)
                    usuario_dato.domicilio_cp = form.codigo_postal.data
                    usuario_dato.save()
                except NotConfiguredError:
                    flash("No se ha configurado el almacenamiento en la nube.", "warning")
                    es_valido = False
                except Exception as err:
                    flash(f"{err}Error al subir el archivo.", "danger")
                    es_valido = False
            if es_valido:
                # Mensaje de resultado positivo
                flash("Ha modificado su Domicilio correctamente, espere a que sea validada", "success")
                return redirect(url_for("usuarios_datos.detail", usuario_dato_id=usuario_dato.id))
            else:
                flash("Ha ocurrido un problema y su información no ha sido guardada", "warning")
    # Precargar datos anteriores
    form.calle.data = usuario_dato.domicilio_calle
    form.numero_exterior.data = usuario_dato.domicilio_numero_ext
    form.numero_interior.data = usuario_dato.domicilio_numero_int
    form.colonia.data = usuario_dato.domicilio_colonia
    form.ciudad.data = usuario_dato.domicilio_ciudad
    form.estado.data = usuario_dato.domicilio_estado
    form.codigo_postal.data = usuario_dato.domicilio_cp
    # Renderiza el formulario de Edición
    return render_template("usuarios_datos/edit_domicilio.jinja2", form=form, usuario_dato=usuario_dato, archivo=archivo_prev)


@usuarios_datos.route("/usuarios_datos/editar/curp/<int:usuario_dato_id>", methods=["GET", "POST"])
@permission_required(MODULO, Permiso.MODIFICAR)
def edit_curp(usuario_dato_id):
    """Edición del Acta de nacimiento"""
    usuario_dato = UsuarioDato.query.get_or_404(usuario_dato_id)
    # Validar si el usuario actual es el correcto
    if usuario_dato.usuario_id != current_user.id:
        return redirect(url_for("sistemas.start"))
    # Extraemos el archivo adjunto para previsualizarlo
    usuario_documento = UsuarioDocumento.query.filter_by(id=usuario_dato.adjunto_curp_id).first()
    archivo_prev = None
    if usuario_documento and usuario_documento.url.endswith(".pdf"):
        archivo_prev = usuario_documento.url
    # Formulario
    form = UsuarioDatoEditCurpForm(CombinedMultiDict((request.files, request.form)))
    if form.validate_on_submit():
        archivo = request.files["archivo"]
        # Si no envía cambios en archivo
        if archivo.filename == "":
            # Revisar que ya este cargada una adjunto previamente
            if archivo_prev is not None:
                usuario_dato.estado_curp = "POR VALIDAR"
                usuario_dato.estado_general = actualizar_estado_general(usuario_dato)
                usuario_dato.curp = safe_curp(form.curp.data)
                usuario_dato.save()
                # Mensaje de resultado positivo
                flash("Ha modificado su CURP correctamente, espere a que sea validada", "success")
                return redirect(url_for("usuarios_datos.detail", usuario_dato_id=usuario_dato.id))
            else:
                flash("Debe cargar un archivo adjunto.", "warning")
        else:
            es_valido = True
            storage = GoogleCloudStorage(
                base_directory=SUBDIRECTORIO,
                bucket_name=current_app.config["CLOUD_STORAGE_DEPOSITO_USUARIOS"],
            )
            try:
                storage.set_content_type(archivo.filename)
            except NotAllowedExtesionError:
                flash("Tipo de archivo no permitido.", "warning")
                es_valido = False
            except UnknownExtesionError:
                flash("Tipo de archivo desconocido.", "warning")
                es_valido = False
            # Validar el tipo de extension
            if archivo.filename.endswith(".pdf"):
                es_valido = True
            else:
                flash("Tipo de archivo no permitido. Solo se permiten *.pdf", "warning")
                es_valido = False
            # Si es válido
            if es_valido:
                # Eliminar el archivo previo si lo hay
                if usuario_documento:
                    usuario_documento.delete()
                # Insertar el registro, para obtener el ID
                usuario_documento = UsuarioDocumento(
                    descripcion="CURP",
                )
                usuario_documento.save()
                # Subir el archivo a la nube
                try:
                    storage.set_filename(hashed_id=usuario_documento.encode_id(), description=usuario_documento.descripcion)
                    storage.upload(archivo.stream.read())
                    usuario_documento.url = storage.url
                    usuario_dato.estado_curp = "POR VALIDAR"
                    usuario_dato.estado_general = actualizar_estado_general(usuario_dato)
                    usuario_dato.adjunto_curp_id = usuario_documento.id
                    usuario_dato.curp = safe_curp(form.curp.data)
                    usuario_dato.save()
                except NotConfiguredError:
                    flash("No se ha configurado el almacenamiento en la nube.", "warning")
                    es_valido = False
                except Exception as err:
                    flash(f"{err}Error al subir el archivo.", "danger")
                    es_valido = False
            if es_valido:
                # Mensaje de resultado positivo
                flash("Ha modificado su CURP correctamente, espere a que sea validada", "success")
                return redirect(url_for("usuarios_datos.detail", usuario_dato_id=usuario_dato.id))
            else:
                flash("Ha ocurrido un problema y su información no ha sido guardada", "warning")
    # Precargar datos anteriores
    form.curp.data = usuario_dato.curp
    # Renderiza el formulario de Edición
    return render_template("usuarios_datos/edit_curp.jinja2", form=form, usuario_dato=usuario_dato, archivo=archivo_prev)


@usuarios_datos.route("/usuarios_datos/editar/cp_fiscal/<int:usuario_dato_id>", methods=["GET", "POST"])
@permission_required(MODULO, Permiso.MODIFICAR)
def edit_cp_fiscal(usuario_dato_id):
    """Edición del Acta de nacimiento"""
    usuario_dato = UsuarioDato.query.get_or_404(usuario_dato_id)
    # Validar si el usuario actual es el correcto
    if usuario_dato.usuario_id != current_user.id:
        return redirect(url_for("sistemas.start"))
    # Extraemos el archivo adjunto para previsualizarlo
    usuario_documento = UsuarioDocumento.query.filter_by(id=usuario_dato.adjunto_cp_fiscal_id).first()
    archivo_prev = None
    if usuario_documento and usuario_documento.url.endswith(".pdf"):
        archivo_prev = usuario_documento.url
    # Formulario
    form = UsuarioDatoEditCPFiscalForm(CombinedMultiDict((request.files, request.form)))
    if form.validate_on_submit():
        archivo = request.files["archivo"]
        # Si no envía cambios en archivo
        if archivo.filename == "":
            # Revisar que ya este cargada una adjunto previamente
            if archivo_prev is not None:
                usuario_dato.estado_cp_fiscal = "POR VALIDAR"
                usuario_dato.estado_general = actualizar_estado_general(usuario_dato)
                usuario_dato.cp_fiscal = form.cp_fiscal.data
                usuario_dato.save()
                # Mensaje de resultado positivo
                flash("Ha modificado su Código Postal Fiscal correctamente, espere a que sea validada", "success")
                return redirect(url_for("usuarios_datos.detail", usuario_dato_id=usuario_dato.id))
            else:
                flash("Debe cargar un archivo adjunto.", "warning")
        else:
            es_valido = True
            storage = GoogleCloudStorage(
                base_directory=SUBDIRECTORIO,
                bucket_name=current_app.config["CLOUD_STORAGE_DEPOSITO_USUARIOS"],
            )
            try:
                storage.set_content_type(archivo.filename)
            except NotAllowedExtesionError:
                flash("Tipo de archivo no permitido.", "warning")
                es_valido = False
            except UnknownExtesionError:
                flash("Tipo de archivo desconocido.", "warning")
                es_valido = False
            # Validar el tipo de extension
            if archivo.filename.endswith(".pdf"):
                es_valido = True
            else:
                flash("Tipo de archivo no permitido. Solo se permiten *.pdf", "warning")
                es_valido = False
            # Si es válido
            if es_valido:
                # Eliminar el archivo previo si lo hay
                if usuario_documento:
                    usuario_documento.delete()
                # Insertar el registro, para obtener el ID
                usuario_documento = UsuarioDocumento(
                    descripcion="cp_fiscal",
                )
                usuario_documento.save()
                # Subir el archivo a la nube
                try:
                    storage.set_filename(hashed_id=usuario_documento.encode_id(), description=usuario_documento.descripcion)
                    storage.upload(archivo.stream.read())
                    usuario_documento.url = storage.url
                    usuario_dato.estado_cp_fiscal = "POR VALIDAR"
                    usuario_dato.estado_general = actualizar_estado_general(usuario_dato)
                    usuario_dato.adjunto_cp_fiscal_id = usuario_documento.id
                    usuario_dato.cp_fiscal = form.cp_fiscal.data
                    usuario_dato.save()
                except NotConfiguredError:
                    flash("No se ha configurado el almacenamiento en la nube.", "warning")
                    es_valido = False
                except Exception as err:
                    flash(f"{err}Error al subir el archivo.", "danger")
                    es_valido = False
            if es_valido:
                # Mensaje de resultado positivo
                flash("Ha modificado su Código Postal Fiscal correctamente, espere a que sea validada", "success")
                return redirect(url_for("usuarios_datos.detail", usuario_dato_id=usuario_dato.id))
            else:
                flash("Ha ocurrido un problema y su información no ha sido guardada", "warning")
    # Precargar datos anteriores
    form.cp_fiscal.data = usuario_dato.cp_fiscal
    # Renderiza el formulario de Edición
    return render_template("usuarios_datos/edit_cp_fiscal.jinja2", form=form, usuario_dato=usuario_dato, archivo=archivo_prev)


@usuarios_datos.route("/usuarios_datos/editar/curriculum/<int:usuario_dato_id>", methods=["GET", "POST"])
@permission_required(MODULO, Permiso.MODIFICAR)
def edit_curriculum(usuario_dato_id):
    """Edición del estado civil"""
    usuario_dato = UsuarioDato.query.get_or_404(usuario_dato_id)
    # Validar si el usuario actual es el correcto
    if usuario_dato.usuario_id != current_user.id:
        return redirect(url_for("sistemas.start"))
    # Extraemos el archivo adjunto para previsualizarlo
    usuario_documento = UsuarioDocumento.query.filter_by(id=usuario_dato.adjunto_curriculum_id).first()
    archivo_prev = None
    if usuario_documento and usuario_documento.url.endswith(".pdf"):
        archivo_prev = usuario_documento.url
    # Formulario
    form = UsuarioDatoEditCurriculumForm(CombinedMultiDict((request.files, request.form)))
    if form.validate_on_submit():
        es_valido = True
        archivo = request.files["archivo"]
        storage = GoogleCloudStorage(
                base_directory=SUBDIRECTORIO,
                bucket_name=current_app.config["CLOUD_STORAGE_DEPOSITO_USUARIOS"],
            )
        try:
            storage.set_content_type(archivo.filename)
        except NotAllowedExtesionError:
            flash("Tipo de archivo no permitido.", "warning")
            es_valido = False
        except UnknownExtesionError:
            flash("Tipo de archivo desconocido.", "warning")
            es_valido = False
        # Validar el tipo de extension
        if archivo.filename.endswith(".pdf"):
            es_valido = True
        else:
            flash("Tipo de archivo no permitido. Solo se permiten *.pdf", "warning")
            es_valido = False
        # Si es válido
        if es_valido:
            # Eliminar el archivo previo si lo hay
            if usuario_documento:
                usuario_documento.delete()
            # Insertar el registro, para obtener el ID
            usuario_documento = UsuarioDocumento(
                descripcion="Curriculum",
            )
            usuario_documento.save()
            # Subir el archivo a la nube
            try:
                storage.set_filename(hashed_id=usuario_documento.encode_id(), description=usuario_documento.descripcion)
                storage.upload(archivo.stream.read())
                usuario_documento.url = storage.url
                usuario_dato.estado_curriculum = "POR VALIDAR"
                usuario_dato.estado_general = actualizar_estado_general(usuario_dato)
                usuario_dato.adjunto_curriculum_id = usuario_documento.id
                usuario_dato.save()
            except NotConfiguredError:
                flash("No se ha configurado el almacenamiento en la nube.", "warning")
                es_valido = False
            except Exception as err:
                flash(f"{err}Error al subir el archivo.", "danger")
                es_valido = False
        if es_valido:
            # mensaje de confirmación de guardado
            flash("Ha modificado su Curriculum correctamente, espere a que sea validado", "success")
            return redirect(url_for("usuarios_datos.detail", usuario_dato_id=usuario_dato.id))
        else:
            flash("Ha ocurrido un problema y su información no ha sido guardada", "warning")
    # Renderiza la página de edición
    return render_template("usuarios_datos/edit_curriculum.jinja2", form=form, usuario_dato=usuario_dato, archivo=archivo_prev)


@usuarios_datos.route("/usuarios_datos/editar/estudios/<int:usuario_dato_id>", methods=["GET", "POST"])
@permission_required(MODULO, Permiso.MODIFICAR)
def edit_estudios(usuario_dato_id):
    """Edición del Acta de nacimiento"""
    usuario_dato = UsuarioDato.query.get_or_404(usuario_dato_id)
    # Validar si el usuario actual es el correcto
    if usuario_dato.usuario_id != current_user.id:
        return redirect(url_for("sistemas.start"))
    # Extraemos el archivo adjunto para previsualizarlo
    usuario_documento = UsuarioDocumento.query.filter_by(id=usuario_dato.adjunto_estudios_id).first()
    archivo_prev = None
    if usuario_documento and usuario_documento.url.endswith(".pdf"):
        archivo_prev = usuario_documento.url
    # Formulario
    form = UsuarioDatoEditEstudiosForm(CombinedMultiDict((request.files, request.form)))
    if form.validate_on_submit():
        archivo = request.files["archivo"]
        # Si no envía cambios en archivo
        if archivo.filename == "":
            # Revisar que ya este cargada una adjunto previamente
            if archivo_prev is not None:
                usuario_dato.estado_estudios = "POR VALIDAR"
                usuario_dato.estado_general = actualizar_estado_general(usuario_dato)
                usuario_dato.estudios_cedula = safe_string(form.cedula_profesional.data)
                usuario_dato.save()
                # Mensaje de resultado positivo
                flash("Ha modificado su Cédula Profesional correctamente, espere a que sea validada", "success")
                return redirect(url_for("usuarios_datos.detail", usuario_dato_id=usuario_dato.id))
            else:
                flash("Debe cargar un archivo adjunto.", "warning")
        else:
            es_valido = True
            storage = GoogleCloudStorage(
                base_directory=SUBDIRECTORIO,
                bucket_name=current_app.config["CLOUD_STORAGE_DEPOSITO_USUARIOS"],
            )
            try:
                storage.set_content_type(archivo.filename)
            except NotAllowedExtesionError:
                flash("Tipo de archivo no permitido.", "warning")
                es_valido = False
            except UnknownExtesionError:
                flash("Tipo de archivo desconocido.", "warning")
                es_valido = False
            # Validar el tipo de extension
            if archivo.filename.endswith(".pdf"):
                es_valido = True
            else:
                flash("Tipo de archivo no permitido. Solo se permiten *.pdf", "warning")
                es_valido = False
            # Si es válido
            if es_valido:
                # Eliminar el archivo previo si lo hay
                if usuario_documento:
                    usuario_documento.delete()
                # Insertar el registro, para obtener el ID
                usuario_documento = UsuarioDocumento(
                    descripcion="Cedula Profesional",
                )
                usuario_documento.save()
                # Subir el archivo a la nube
                try:
                    storage.set_filename(hashed_id=usuario_documento.encode_id(), description=usuario_documento.descripcion)
                    storage.upload(archivo.stream.read())
                    usuario_documento.url = storage.url
                    usuario_dato.estado_estudios = "POR VALIDAR"
                    usuario_dato.estado_general = actualizar_estado_general(usuario_dato)
                    usuario_dato.adjunto_estudios_id = usuario_documento.id
                    usuario_dato.estudios_cedula = safe_string(form.cedula_profesional.data)
                    usuario_dato.save()
                except NotConfiguredError:
                    flash("No se ha configurado el almacenamiento en la nube.", "warning")
                    es_valido = False
                except Exception as err:
                    flash(f"{err}Error al subir el archivo.", "danger")
                    es_valido = False
            if es_valido:
                # Mensaje de resultado positivo
                flash("Ha modificado su Cédula Profesional correctamente, espere a que sea validada", "success")
                return redirect(url_for("usuarios_datos.detail", usuario_dato_id=usuario_dato.id))
            else:
                flash("Ha ocurrido un problema y su información no ha sido guardada", "warning")
    # Precargar datos anteriores
    form.cedula_profesional.data = usuario_dato.estudios_cedula
    # Renderiza el formulario de Edición
    return render_template("usuarios_datos/edit_estudios.jinja2", form=form, usuario_dato=usuario_dato, archivo=archivo_prev)


@usuarios_datos.route("/usuarios_datos/editar/es_madre/<int:usuario_dato_id>", methods=["GET", "POST"])
@permission_required(MODULO, Permiso.MODIFICAR)
def edit_es_madre(usuario_dato_id):
    """Edición del Acta de nacimiento"""
    usuario_dato = UsuarioDato.query.get_or_404(usuario_dato_id)
    # Validar si el usuario actual es el correcto
    if usuario_dato.usuario_id != current_user.id:
        return redirect(url_for("sistemas.start"))
    # Extraemos el archivo adjunto para previsualizarlo
    usuario_documento = UsuarioDocumento.query.filter_by(id=usuario_dato.adjunto_acta_nacimiento_hijo_id).first()
    archivo_prev = None
    if usuario_documento and usuario_documento.url.endswith(".pdf"):
        archivo_prev = usuario_documento.url
    # Formulario
    form = UsuarioDatoEditEsMadreForm(CombinedMultiDict((request.files, request.form)))
    if form.validate_on_submit():
        archivo = request.files["archivo"]
        # Si no envía cambios en archivo
        if archivo.filename == "":
            # Si ya hay un archivo adjunto previamente
            if archivo_prev is not None:
                if form.es_madre.data == "SI":
                    usuario_dato.estado_es_madre = "POR VALIDAR"
                    usuario_dato.estado_general = actualizar_estado_general(usuario_dato)
                    usuario_dato.es_madre = True
                    usuario_dato.save()
                    # Mensaje de resultado positivo
                    flash("Ha modificado su Condición de Madre correctamente, espere a que sea validada", "success")
                    return redirect(url_for("usuarios_datos.detail", usuario_dato_id=usuario_dato.id))
                elif form.es_madre.data == "NO":
                    # Borrar el archivo previo
                    if usuario_documento:
                        usuario_documento.delete()
                        usuario_dato.adjunto_acta_nacimiento_hijo_id = None
                    usuario_dato.estado_es_madre = "POR VALIDAR"
                    usuario_dato.estado_general = actualizar_estado_general(usuario_dato)
                    usuario_dato.es_madre = False
                    usuario_dato.save()
                    # Mensaje de resultado positivo
                    flash("Ha modificado su Condición de Madre correctamente, espere a que sea validada", "success")
                    return redirect(url_for("usuarios_datos.detail", usuario_dato_id=usuario_dato.id))
            else:
                if form.es_madre.data == "SI":
                    flash("Si indica que sí es madre, debe cargar un archivo adjunto (acta de nacimiento de un hijo).", "warning")
                else:
                    usuario_dato.estado_es_madre = "POR VALIDAR"
                    usuario_dato.estado_general = actualizar_estado_general(usuario_dato)
                    usuario_dato.es_madre = False
                    usuario_dato.save()
                    # Mensaje de resultado positivo
                    flash("Ha modificado su Condición de Madre correctamente, espere a que sea validada", "success")
                    return redirect(url_for("usuarios_datos.detail", usuario_dato_id=usuario_dato.id))
        else:
            es_valido = True
            storage = GoogleCloudStorage(
                base_directory=SUBDIRECTORIO,
                bucket_name=current_app.config["CLOUD_STORAGE_DEPOSITO_USUARIOS"],
            )
            try:
                storage.set_content_type(archivo.filename)
            except NotAllowedExtesionError:
                flash("Tipo de archivo no permitido.", "warning")
                es_valido = False
            except UnknownExtesionError:
                flash("Tipo de archivo desconocido.", "warning")
                es_valido = False
            # Validar el tipo de extension
            if archivo.filename.endswith(".pdf"):
                es_valido = True
            else:
                flash("Tipo de archivo no permitido. Solo se permiten *.pdf", "warning")
                es_valido = False
            # Si es válido
            if es_valido:
                # Eliminar el archivo previo si lo hay
                if usuario_documento:
                    usuario_documento.delete()
                # Insertar el registro, para obtener el ID
                if form.es_madre.data == "SI":
                    usuario_documento = UsuarioDocumento(
                        descripcion="Acta Nacimiento Hijo",
                    )
                    usuario_documento.save()
                    # Subir el archivo a la nube
                    try:
                        storage.set_filename(hashed_id=usuario_documento.encode_id(), description=usuario_documento.descripcion)
                        storage.upload(archivo.stream.read())
                        usuario_documento.url = storage.url
                        usuario_dato.estado_es_madre = "POR VALIDAR"
                        usuario_dato.estado_general = actualizar_estado_general(usuario_dato)
                        usuario_dato.adjunto_acta_nacimiento_hijo_id = usuario_documento.id
                        usuario_dato.es_madre = True
                        usuario_dato.save()
                    except NotConfiguredError:
                        flash("No se ha configurado el almacenamiento en la nube.", "warning")
                        es_valido = False
                    except Exception as err:
                        flash(f"{err}Error al subir el archivo.", "danger")
                        es_valido = False
                elif form.es_madre.data == "NO":
                    usuario_dato.estado_es_madre = "POR VALIDAR"
                    usuario_dato.estado_general = actualizar_estado_general(usuario_dato)
                    usuario_dato.adjunto_acta_nacimiento_hijo_id = None
                    usuario_dato.es_madre = False
                    usuario_dato.save()
            if es_valido:
                # Mensaje de resultado positivo
                flash("Ha modificado su Condición de Madre correctamente, espere a que sea validada", "success")
                return redirect(url_for("usuarios_datos.detail", usuario_dato_id=usuario_dato.id))
            else:
                flash("Ha ocurrido un problema y su información no ha sido guardada", "warning")
    # Precargar datos anteriores
    if usuario_dato.es_madre:
        form.es_madre.data = "SI"
    else:
        form.es_madre.data = "NO"
    # Renderiza el formulario de Edición
    return render_template("usuarios_datos/edit_es_madre.jinja2", form=form, usuario_dato=usuario_dato, archivo=archivo_prev)


@usuarios_datos.route("/usuarios_datos/editar/estado_civil/<int:usuario_dato_id>", methods=["GET", "POST"])
@permission_required(MODULO, Permiso.MODIFICAR)
def edit_estado_civil(usuario_dato_id):
    """Edición del estado civil"""
    usuario_dato = UsuarioDato.query.get_or_404(usuario_dato_id)
    # Validar si el usuario actual es el correcto
    if usuario_dato.usuario_id != current_user.id:
        return redirect(url_for("sistemas.start"))
    # Formulario de Edición
    form = UsuarioDatoEditEstadoCivilForm()
    if form.validate_on_submit():
        usuario_dato.estado_civil = form.estado_civil.data
        usuario_dato.estado_estado_civil = "POR VALIDAR"
        usuario_dato.estado_general = actualizar_estado_general(usuario_dato)
        usuario_dato.save()
        flash("Ha modificado su estado civil correctamente, espere a que sea validado", "success")
        return redirect(url_for("usuarios_datos.detail", usuario_dato_id=usuario_dato.id))
    # Precargar datos anteriores
    form.estado_civil.data = usuario_dato.estado_civil
    return render_template("usuarios_datos/edit_estado_civil.jinja2", form=form, usuario_dato=usuario_dato)


@usuarios_datos.route("/usuarios_datos/editar/estado_cuenta/<int:usuario_dato_id>", methods=["GET", "POST"])
@permission_required(MODULO, Permiso.MODIFICAR)
def edit_estado_cuenta(usuario_dato_id):
    """Edición del estado civil"""
    usuario_dato = UsuarioDato.query.get_or_404(usuario_dato_id)
    # Validar si el usuario actual es el correcto
    if usuario_dato.usuario_id != current_user.id:
        return redirect(url_for("sistemas.start"))
    # Extraemos el archivo adjunto para previsualizarlo
    usuario_documento = UsuarioDocumento.query.filter_by(id=usuario_dato.adjunto_estado_cuenta_id).first()
    archivo_prev = None
    if usuario_documento and usuario_documento.url.endswith(".pdf"):
        archivo_prev = usuario_documento.url
    # Formulario
    form = UsuarioDatoEditEstadoCuentaForm(CombinedMultiDict((request.files, request.form)))
    if form.validate_on_submit():
        es_valido = True
        archivo = request.files["archivo"]
        storage = GoogleCloudStorage(
                base_directory=SUBDIRECTORIO,
                bucket_name=current_app.config["CLOUD_STORAGE_DEPOSITO_USUARIOS"],
            )
        try:
            storage.set_content_type(archivo.filename)
        except NotAllowedExtesionError:
            flash("Tipo de archivo no permitido.", "warning")
            es_valido = False
        except UnknownExtesionError:
            flash("Tipo de archivo desconocido.", "warning")
            es_valido = False
        # Validar el tipo de extension
        if archivo.filename.endswith(".pdf"):
            es_valido = True
        else:
            flash("Tipo de archivo no permitido. Solo se permiten *.pdf", "warning")
            es_valido = False
        # Si es válido
        if es_valido:
            # Eliminar el archivo previo si lo hay
            if usuario_documento:
                usuario_documento.delete()
            # Insertar el registro, para obtener el ID
            usuario_documento = UsuarioDocumento(
                descripcion="Estado Cuenta",
            )
            usuario_documento.save()
            # Subir el archivo a la nube
            try:
                storage.set_filename(hashed_id=usuario_documento.encode_id(), description=usuario_documento.descripcion)
                storage.upload(archivo.stream.read())
                usuario_documento.url = storage.url
                usuario_dato.estado_estado_cuenta = "POR VALIDAR"
                usuario_dato.estado_general = actualizar_estado_general(usuario_dato)
                usuario_dato.adjunto_estado_cuenta_id = usuario_documento.id
                usuario_dato.save()
            except NotConfiguredError:
                flash("No se ha configurado el almacenamiento en la nube.", "warning")
                es_valido = False
            except Exception as err:
                flash(f"{err}Error al subir el archivo.", "danger")
                es_valido = False
        if es_valido:
            # mensaje de confirmación de guardado
            flash("Ha modificado su Estado de Cuenta correctamente, espere a que sea validado", "success")
            return redirect(url_for("usuarios_datos.detail", usuario_dato_id=usuario_dato.id))
        else:
            flash("Ha ocurrido un problema y su información no ha sido guardada", "warning")
    # Renderiza la página de edición
    return render_template("usuarios_datos/edit_estado_cuenta.jinja2", form=form, usuario_dato=usuario_dato, archivo=archivo_prev)


def actualizar_estado_general(usuario_dato: UsuarioDato) -> str:
    """Revisa los estados de los demás campos y coloca el estado general correspondiente"""
    # Revisa el estado de todos los campos
    if (
        usuario_dato.estado_identificacion == "VALIDO"
        and usuario_dato.estado_acta_nacimiento == "VALIDO"
        and usuario_dato.estado_domicilio == "VALIDO"
        and usuario_dato.estado_curp == "VALIDO"
        and usuario_dato.estado_cp_fiscal == "VALIDO"
        and usuario_dato.estado_curriculum == "VALIDO"
        and usuario_dato.estado_estudios == "VALIDO"
        and usuario_dato.estado_es_madre == "VALIDO"
        and usuario_dato.estado_estado_civil == "VALIDO"
        and usuario_dato.estado_estado_cuenta == "VALIDO"
        # and usuario_dato.estado_telefono == "VALIDO"
        # and usuario_dato.estado_email == "VALIDO"
    ):
        return "VALIDO"

    # Si almenos hay un dato no válido, todo se considera no válido
    if usuario_dato.estado_identificacion == "NO VALIDO":
        return "NO VALIDO"
    if usuario_dato.estado_acta_nacimiento == "NO VALIDO":
        return "NO VALIDO"
    if usuario_dato.estado_domicilio == "NO VALIDO":
        return "NO VALIDO"
    if usuario_dato.estado_curp == "NO VALIDO":
        return "NO VALIDO"
    if usuario_dato.estado_cp_fiscal == "NO VALIDO":
        return "NO VALIDO"
    if usuario_dato.estado_curriculum == "NO VALIDO":
        return "NO VALIDO"
    if usuario_dato.estado_estudios == "NO VALIDO":
        return "NO VALIDO"
    if usuario_dato.estado_es_madre == "NO VALIDO":
        return "NO VALIDO"
    if usuario_dato.estado_estado_civil == "NO VALIDO":
        return "NO VALIDO"
    if usuario_dato.estado_estado_cuenta == "NO VALIDO":
        return "NO VALIDO"
    # if usuario_dato.estado_telefono == "NO VALIDO":
    #     return "NO VALIDO"
    # if usuario_dato.estado_email == "NO VALIDO":
    #     return "NO VALIDO"

    # Si almenos sigue habiendo un dato vacío
    if usuario_dato.estado_identificacion == "INCOMPLETO":
        return "INCOMPLETO"
    if usuario_dato.estado_acta_nacimiento == "INCOMPLETO":
        return "INCOMPLETO"
    if usuario_dato.estado_domicilio == "INCOMPLETO":
        return "INCOMPLETO"
    if usuario_dato.estado_curp == "INCOMPLETO":
        return "INCOMPLETO"
    if usuario_dato.estado_cp_fiscal == "INCOMPLETO":
        return "INCOMPLETO"
    if usuario_dato.estado_curriculum == "INCOMPLETO":
        return "INCOMPLETO"
    if usuario_dato.estado_estudios == "INCOMPLETO":
        return "INCOMPLETO"
    if usuario_dato.estado_es_madre == "INCOMPLETO":
        return "INCOMPLETO"
    if usuario_dato.estado_estado_civil == "INCOMPLETO":
        return "INCOMPLETO"
    if usuario_dato.estado_estado_cuenta == "INCOMPLETO":
        return "INCOMPLETO"
    # if usuario_dato.estado_telefono == None:
    #     return None
    # if usuario_dato.estado_email == None:
    #     return None

    return "POR VALIDAR"


@usuarios_datos.route("/usuarios_datos/validar/identificacion/<int:usuario_dato_id>", methods=["GET", "POST"])
@permission_required(MODULO, Permiso.ADMINISTRAR)
def validate_identificacion(usuario_dato_id):
    """Validación de la identificación oficial"""
    usuario_dato = UsuarioDato.query.get_or_404(usuario_dato_id)
    # Extraemos el archivo adjunto para previsualizarlo
    usuario_documento = UsuarioDocumento.query.filter_by(id=usuario_dato.adjunto_identificacion_id).first()
    archivo_prev = None
    if usuario_documento:
        archivo_prev = usuario_documento.url
    # Formulario de validación
    form = UsuarioDatoValidateForm()
    if form.validate_on_submit():
        if form.valido.data:
            usuario_dato.estado_identificacion = "VALIDO"
            usuario_dato.mensaje_identificacion = None
            usuario_dato.estado_general = actualizar_estado_general(usuario_dato)
            usuario_dato.save()
            flash("Ha validado la identificación oficial correctamente", "success")
        elif form.no_valido.data:
            mensaje = safe_message(form.mensaje.data, default_output_str=None)
            if mensaje is None:
                flash("Si rechaza esta información, por favor añada un mensaje dando una explicación", "warning")
                return render_template("usuarios_datos/validate_identificacion.jinja2", form=form, usuario_dato=usuario_dato)
            else:
                usuario_dato.mensaje_identificacion = mensaje
                usuario_dato.estado_identificacion = "NO VALIDO"
                usuario_dato.estado_general = "NO VALIDO"
                usuario_dato.save()
                flash("Ha rechazado la identificación oficial", "success")

        return redirect(url_for("usuarios_datos.detail", usuario_dato_id=usuario_dato.id))
    # Renderiza la página de validación
    return render_template("usuarios_datos/validate_identificacion.jinja2", form=form, usuario_dato=usuario_dato, archivo=archivo_prev)


@usuarios_datos.route("/usuarios_datos/validar/acta_nacimiento/<int:usuario_dato_id>", methods=["GET", "POST"])
@permission_required(MODULO, Permiso.ADMINISTRAR)
def validate_acta_nacimiento(usuario_dato_id):
    """Validación de el acta de nacimiento"""
    usuario_dato = UsuarioDato.query.get_or_404(usuario_dato_id)
    # Extraemos el archivo adjunto para previsualizarlo
    usuario_documento = UsuarioDocumento.query.filter_by(id=usuario_dato.adjunto_acta_nacimiento_id).first()
    archivo_prev = None
    if usuario_documento:
        archivo_prev = usuario_documento.url
    # Formulario de validación
    form = UsuarioDatoValidateForm()
    if form.validate_on_submit():
        if form.valido.data:
            usuario_dato.estado_acta_nacimiento = "VALIDO"
            usuario_dato.mensaje_acta_nacimiento = None
            usuario_dato.estado_general = actualizar_estado_general(usuario_dato)
            usuario_dato.save()
            flash("Ha validado el acta de nacimiento correctamente", "success")
        elif form.no_valido.data:
            mensaje = safe_message(form.mensaje.data, default_output_str=None)
            if mensaje is None:
                flash("Si rechaza esta información, por favor añada un mensaje dando una explicación", "warning")
                return render_template("usuarios_datos/validate_acta_nacimiento.jinja2", form=form, usuario_dato=usuario_dato)
            else:
                usuario_dato.mensaje_acta_nacimiento = mensaje
                usuario_dato.estado_acta_nacimiento = "NO VALIDO"
                usuario_dato.estado_general = "NO VALIDO"
                usuario_dato.save()
                flash("Ha rechazado el acta de nacimiento", "success")

        return redirect(url_for("usuarios_datos.detail", usuario_dato_id=usuario_dato.id))
    # Renderiza la página de validación
    return render_template("usuarios_datos/validate_acta_nacimiento.jinja2", form=form, usuario_dato=usuario_dato, archivo=archivo_prev)


@usuarios_datos.route("/usuarios_datos/validar/domicilio/<int:usuario_dato_id>", methods=["GET", "POST"])
@permission_required(MODULO, Permiso.ADMINISTRAR)
def validate_domicilio(usuario_dato_id):
    """Validación de el acta de nacimiento"""
    usuario_dato = UsuarioDato.query.get_or_404(usuario_dato_id)
    # Extraemos el archivo adjunto para previsualizarlo
    usuario_documento = UsuarioDocumento.query.filter_by(id=usuario_dato.adjunto_domicilio_id).first()
    archivo_prev = None
    if usuario_documento:
        archivo_prev = usuario_documento.url
    # Formulario de validación
    form = UsuarioDatoValidateForm()
    if form.validate_on_submit():
        if form.valido.data:
            usuario_dato.estado_domicilio = "VALIDO"
            usuario_dato.mensaje_domicilio = None
            usuario_dato.estado_general = actualizar_estado_general(usuario_dato)
            usuario_dato.save()
            flash("Ha validado el acta de nacimiento correctamente", "success")
        elif form.no_valido.data:
            mensaje = safe_message(form.mensaje.data, default_output_str=None)
            if mensaje is None:
                flash("Si rechaza esta información, por favor añada un mensaje dando una explicación", "warning")
                return render_template("usuarios_datos/validate_domicilio.jinja2", form=form, usuario_dato=usuario_dato)
            else:
                usuario_dato.mensaje_domicilio = mensaje
                usuario_dato.estado_domicilio = "NO VALIDO"
                usuario_dato.estado_general = "NO VALIDO"
                usuario_dato.save()
                flash("Ha rechazado el acta de nacimiento", "success")

        return redirect(url_for("usuarios_datos.detail", usuario_dato_id=usuario_dato.id))
    # Renderiza la página de validación
    return render_template("usuarios_datos/validate_domicilio.jinja2", form=form, usuario_dato=usuario_dato, archivo=archivo_prev)


@usuarios_datos.route("/usuarios_datos/validar/curp/<int:usuario_dato_id>", methods=["GET", "POST"])
@permission_required(MODULO, Permiso.ADMINISTRAR)
def validate_curp(usuario_dato_id):
    """Validación del CURP"""
    usuario_dato = UsuarioDato.query.get_or_404(usuario_dato_id)
    # Extraemos el archivo adjunto para previsualizarlo
    usuario_documento = UsuarioDocumento.query.filter_by(id=usuario_dato.adjunto_curp_id).first()
    archivo_prev = None
    if usuario_documento:
        archivo_prev = usuario_documento.url
    # Formulario de validación
    form = UsuarioDatoValidateForm()
    if form.validate_on_submit():
        if form.valido.data:
            usuario_dato.estado_curp = "VALIDO"
            usuario_dato.mensaje_curp = None
            usuario_dato.estado_general = actualizar_estado_general(usuario_dato)
            usuario_dato.save()
            flash("Ha validado su CURP correctamente", "success")
        elif form.no_valido.data:
            mensaje = safe_message(form.mensaje.data, default_output_str=None)
            if mensaje is None:
                flash("Si rechaza esta información, por favor añada un mensaje dando una explicación", "warning")
                return render_template("usuarios_datos/validate_curp.jinja2", form=form, usuario_dato=usuario_dato)
            else:
                usuario_dato.mensaje_curp = mensaje
                usuario_dato.estado_curp = "NO VALIDO"
                usuario_dato.estado_general = "NO VALIDO"
                usuario_dato.save()
                flash("Ha rechazado el CURP", "success")

        return redirect(url_for("usuarios_datos.detail", usuario_dato_id=usuario_dato.id))
    # Renderiza la página de validación
    return render_template("usuarios_datos/validate_curp.jinja2", form=form, usuario_dato=usuario_dato, archivo=archivo_prev)


@usuarios_datos.route("/usuarios_datos/validar/cp_fiscal/<int:usuario_dato_id>", methods=["GET", "POST"])
@permission_required(MODULO, Permiso.ADMINISTRAR)
def validate_cp_fiscal(usuario_dato_id):
    """Validación del Código Postal Fiscal"""
    usuario_dato = UsuarioDato.query.get_or_404(usuario_dato_id)
    # Extraemos el archivo adjunto para previsualizarlo
    usuario_documento = UsuarioDocumento.query.filter_by(id=usuario_dato.adjunto_cp_fiscal_id).first()
    archivo_prev = None
    if usuario_documento:
        archivo_prev = usuario_documento.url
    # Formulario de validación
    form = UsuarioDatoValidateForm()
    if form.validate_on_submit():
        if form.valido.data:
            usuario_dato.estado_cp_fiscal = "VALIDO"
            usuario_dato.mensaje_cp_fiscal = None
            usuario_dato.estado_general = actualizar_estado_general(usuario_dato)
            usuario_dato.save()
            flash("Ha validado su Código Postal Fiscal correctamente", "success")
        elif form.no_valido.data:
            mensaje = safe_message(form.mensaje.data, default_output_str=None)
            if mensaje is None:
                flash("Si rechaza esta información, por favor añada un mensaje dando una explicación", "warning")
                return render_template("usuarios_datos/validate_cp_fiscal.jinja2", form=form, usuario_dato=usuario_dato)
            else:
                usuario_dato.mensaje_cp_fiscal = mensaje
                usuario_dato.estado_cp_fiscal = "NO VALIDO"
                usuario_dato.estado_general = "NO VALIDO"
                usuario_dato.save()
                flash("Ha rechazado el Código Postal Fiscal", "success")

        return redirect(url_for("usuarios_datos.detail", usuario_dato_id=usuario_dato.id))
    # Renderiza la página de validación
    return render_template("usuarios_datos/validate_cp_fiscal.jinja2", form=form, usuario_dato=usuario_dato, archivo=archivo_prev)


@usuarios_datos.route("/usuarios_datos/validar/curriculum/<int:usuario_dato_id>", methods=["GET", "POST"])
@permission_required(MODULO, Permiso.ADMINISTRAR)
def validate_curriculum(usuario_dato_id):
    """Validación de la identificación oficial"""
    usuario_dato = UsuarioDato.query.get_or_404(usuario_dato_id)
    # Extraemos el archivo adjunto para previsualizarlo
    usuario_documento = UsuarioDocumento.query.filter_by(id=usuario_dato.adjunto_curriculum_id).first()
    archivo_prev = None
    if usuario_documento:
        archivo_prev = usuario_documento.url
    # Formulario de validación
    form = UsuarioDatoValidateForm()
    if form.validate_on_submit():
        if form.valido.data:
            usuario_dato.estado_curriculum = "VALIDO"
            usuario_dato.mensaje_curriculum = None
            usuario_dato.estado_general = actualizar_estado_general(usuario_dato)
            usuario_dato.save()
            flash("Ha validado el Curriculum correctamente", "success")
        elif form.no_valido.data:
            mensaje = safe_message(form.mensaje.data, default_output_str=None)
            if mensaje is None:
                flash("Si rechaza esta información, por favor añada un mensaje dando una explicación", "warning")
                return render_template("usuarios_datos/validate_curriculum.jinja2", form=form, usuario_dato=usuario_dato)
            else:
                usuario_dato.mensaje_curriculum = mensaje
                usuario_dato.estado_curriculum = "NO VALIDO"
                usuario_dato.estado_general = "NO VALIDO"
                usuario_dato.save()
                flash("Ha rechazado el Curriculum", "success")

        return redirect(url_for("usuarios_datos.detail", usuario_dato_id=usuario_dato.id))
    # Renderiza la página de validación
    return render_template("usuarios_datos/validate_curriculum.jinja2", form=form, usuario_dato=usuario_dato, archivo=archivo_prev)


@usuarios_datos.route("/usuarios_datos/validar/estudios/<int:usuario_dato_id>", methods=["GET", "POST"])
@permission_required(MODULO, Permiso.ADMINISTRAR)
def validate_estudios(usuario_dato_id):
    """Validación del Código Postal Fiscal"""
    usuario_dato = UsuarioDato.query.get_or_404(usuario_dato_id)
    # Extraemos el archivo adjunto para previsualizarlo
    usuario_documento = UsuarioDocumento.query.filter_by(id=usuario_dato.adjunto_estudios_id).first()
    archivo_prev = None
    if usuario_documento:
        archivo_prev = usuario_documento.url
    # Formulario de validación
    form = UsuarioDatoValidateForm()
    if form.validate_on_submit():
        if form.valido.data:
            usuario_dato.estado_estudios = "VALIDO"
            usuario_dato.mensaje_estudios = None
            usuario_dato.estado_general = actualizar_estado_general(usuario_dato)
            usuario_dato.save()
            flash("Ha validado su Cédula Profesional correctamente", "success")
        elif form.no_valido.data:
            mensaje = safe_message(form.mensaje.data, default_output_str=None)
            if mensaje is None:
                flash("Si rechaza esta información, por favor añada un mensaje dando una explicación", "warning")
                return render_template("usuarios_datos/validate_estudios.jinja2", form=form, usuario_dato=usuario_dato)
            else:
                usuario_dato.mensaje_estudios = mensaje
                usuario_dato.estado_estudios = "NO VALIDO"
                usuario_dato.estado_general = "NO VALIDO"
                usuario_dato.save()
                flash("Ha rechazado el Cédula Profesional", "success")

        return redirect(url_for("usuarios_datos.detail", usuario_dato_id=usuario_dato.id))
    # Renderiza la página de validación
    return render_template("usuarios_datos/validate_estudios.jinja2", form=form, usuario_dato=usuario_dato, archivo=archivo_prev)


@usuarios_datos.route("/usuarios_datos/validar/es_madre/<int:usuario_dato_id>", methods=["GET", "POST"])
@permission_required(MODULO, Permiso.ADMINISTRAR)
def validate_es_madre(usuario_dato_id):
    """Validación de la identificación oficial"""
    usuario_dato = UsuarioDato.query.get_or_404(usuario_dato_id)
    # Extraemos el archivo adjunto para previsualizarlo
    usuario_documento = UsuarioDocumento.query.filter_by(id=usuario_dato.adjunto_acta_nacimiento_hijo_id).first()
    archivo_prev = None
    if usuario_documento:
        archivo_prev = usuario_documento.url
    # Formulario de validación
    form = UsuarioDatoValidateForm()
    if form.validate_on_submit():
        if form.valido.data:
            # Revisar genero según su CURP
            if usuario_dato.usuario.curp[10] == "M" or (usuario_dato.usuario.curp[10] == "H" and usuario_dato.es_madre is False):
                usuario_dato.estado_es_madre = "VALIDO"
                usuario_dato.mensaje_es_madre = None
                usuario_dato.estado_general = actualizar_estado_general(usuario_dato)
                usuario_dato.save()
                flash("Ha validado la condición de madre correctamente", "success")
            else:
                flash("Según su género por CURP, esta persona es Hombre, no puede ser madre", "warning")
        elif form.no_valido.data:
            mensaje = safe_message(form.mensaje.data, default_output_str=None)
            if mensaje is None:
                flash("Si rechaza esta información, por favor añada un mensaje dando una explicación", "warning")
                return render_template("usuarios_datos/validate_es_madre.jinja2", form=form, usuario_dato=usuario_dato)
            else:
                usuario_dato.mensaje_es_madre = mensaje
                usuario_dato.estado_es_madre = "NO VALIDO"
                usuario_dato.estado_general = "NO VALIDO"
                usuario_dato.save()
                flash("Ha rechazado la condición de madre oficial", "success")

        return redirect(url_for("usuarios_datos.detail", usuario_dato_id=usuario_dato.id))
    # Identificar el género según su CURP
    if usuario_dato.usuario.curp[10] == "H":
        genero_curp = "HOMBRE, No podría ser madre"
    else:
        genero_curp = "MUJER"
    # Renderiza la página de validación
    return render_template("usuarios_datos/validate_es_madre.jinja2", form=form, usuario_dato=usuario_dato, archivo=archivo_prev, genero_curp=genero_curp)


@usuarios_datos.route("/usuarios_datos/validar/estado_civil/<int:usuario_dato_id>", methods=["GET", "POST"])
@permission_required(MODULO, Permiso.ADMINISTRAR)
def validate_estado_civil(usuario_dato_id):
    """Validación del estado civil"""
    usuario_dato = UsuarioDato.query.get_or_404(usuario_dato_id)
    form = UsuarioDatoValidateForm()
    if form.validate_on_submit():
        if form.valido.data:
            usuario_dato.estado_estado_civil = "VALIDO"
            usuario_dato.mensaje_estado_civil = None
            usuario_dato.estado_general = actualizar_estado_general(usuario_dato)
            usuario_dato.save()
            flash("Ha validado el estado civil correctamente", "success")
        elif form.no_valido.data:
            mensaje = safe_message(form.mensaje.data, default_output_str=None)
            if mensaje is None:
                flash("Si rechaza esta información, por favor añada un mensaje dando una explicación", "warning")
                return render_template("usuarios_datos/validate_estado_civil.jinja2", form=form, usuario_dato=usuario_dato)
            else:
                usuario_dato.mensaje_estado_civil = mensaje
                usuario_dato.estado_estado_civil = "NO VALIDO"
                usuario_dato.estado_general = "NO VALIDO"
                usuario_dato.save()
                flash("Ha rechazado el estado civil", "success")

        return redirect(url_for("usuarios_datos.detail", usuario_dato_id=usuario_dato.id))
    # Renderiza la página de validación
    return render_template("usuarios_datos/validate_estado_civil.jinja2", form=form, usuario_dato=usuario_dato)


@usuarios_datos.route("/usuarios_datos/validar/estado_cuenta/<int:usuario_dato_id>", methods=["GET", "POST"])
@permission_required(MODULO, Permiso.ADMINISTRAR)
def validate_estado_cuenta(usuario_dato_id):
    """Validación de la identificación oficial"""
    usuario_dato = UsuarioDato.query.get_or_404(usuario_dato_id)
    # Extraemos el archivo adjunto para previsualizarlo
    usuario_documento = UsuarioDocumento.query.filter_by(id=usuario_dato.adjunto_estado_cuenta_id).first()
    archivo_prev = None
    if usuario_documento:
        archivo_prev = usuario_documento.url
    # Formulario de validación
    form = UsuarioDatoValidateForm()
    if form.validate_on_submit():
        if form.valido.data:
            usuario_dato.estado_estado_cuenta = "VALIDO"
            usuario_dato.mensaje_estado_cuenta = None
            usuario_dato.estado_general = actualizar_estado_general(usuario_dato)
            usuario_dato.save()
            flash("Ha validado el Estado de Cuenta correctamente", "success")
        elif form.no_valido.data:
            mensaje = safe_message(form.mensaje.data, default_output_str=None)
            if mensaje is None:
                flash("Si rechaza esta información, por favor añada un mensaje dando una explicación", "warning")
                return render_template("usuarios_datos/validate_estado_cuenta.jinja2", form=form, usuario_dato=usuario_dato)
            else:
                usuario_dato.mensaje_estado_cuenta = mensaje
                usuario_dato.estado_estado_cuenta = "NO VALIDO"
                usuario_dato.estado_general = "NO VALIDO"
                usuario_dato.save()
                flash("Ha rechazado el Estado de Cuenta", "success")

        return redirect(url_for("usuarios_datos.detail", usuario_dato_id=usuario_dato.id))
    # Renderiza la página de validación
    return render_template("usuarios_datos/validate_estado_cuenta.jinja2", form=form, usuario_dato=usuario_dato, archivo=archivo_prev)


@usuarios_datos.route("/usuarios_datos/exportar_xlsx")
@permission_required(MODULO, Permiso.ADMINISTRAR)
def exportar_xlsx():
    """Lanzar tarea en el fondo para exportar los Usuarios-Datos a un archivo XLSX"""
    tarea = current_user.launch_task(
        comando="usuarios_datos.tasks.lanzar_exportar_xlsx",
        mensaje="Exportando los Usuarios-Datos a un archivo XLSX...",
    )
    flash("Se ha lanzado esta tarea en el fondo. Esta página se va a recargar en 10 segundos...", "info")
    return redirect(url_for("tareas.detail", tarea_id=tarea.id))


@usuarios_datos.route("/usuarios_datos/<int:usuario_dato_id>/<int:usuario_documento_id>.pdf", methods=["GET", "POST"])
def download_file(usuario_dato_id, usuario_documento_id):
    """Descargar el archivo adjunto"""

    # Consultar usuario_dato, si no existe causar error 404
    usuario_dato = UsuarioDato.query.get_or_404(usuario_dato_id)

    # Consultar usuario_documento, si no existe causar error 404
    archivo = UsuarioDocumento.query.get_or_404(usuario_documento_id)

    # Validar que el archivo tenga el estatus "A"
    if archivo.estatus != "A":
        abort(404)

    # Validar usuario_dato, en el cual el usuario debe ser el mismo que current_user
    if usuario_dato.usuario != current_user and not current_user.can_admin(MODULO):
        flash("Acceso no autorizado", "warning")
        return redirect(url_for("sistemas.start"))

    # Validar usuario_documento, si no tiene URL redirigir a la página de detalle
    if archivo is None or archivo.url == "":
        flash("El archivo NO tiene URL", "warning")
        return redirect(url_for("usuarios_datos.detail", usuario_dato_id=usuario_dato.id))

    # Validar el nombre del archivo, si NO es PDF redirigir a la página de detalle
    if not archivo.url.endswith(".pdf"):
        flash("El archivo NO es un PDF", "warning")
        return redirect(url_for("usuarios_datos.detail", usuario_dato_id=usuario_dato.id))

    # Obtener el contenido del archivo PDF desde Google Cloud Storage
    try:
        descarga_contenido = get_file_from_gcs(
            bucket_name=current_app.config["CLOUD_STORAGE_DEPOSITO_USUARIOS"],
            blob_name=get_blob_name_from_url(archivo.url),
        )
    except (MyBucketNotFoundError, MyFileNotFoundError, MyNotValidParamError) as error:
        flash(str(error), "danger")
        abort(404)

    # Definir el nombre del archivo a descargar
    descarga_nombre = f"{archivo.descripcion}.pdf"

    # Descargar el archivo PDF
    response = make_response(descarga_contenido)
    response.headers["Content-Type"] = "application/pdf"
    response.headers["Content-Disposition"] = f"inline; filename={descarga_nombre}"
    return response

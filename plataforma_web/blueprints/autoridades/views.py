"""
Autoridades, vistas
"""
from datetime import date, datetime, timedelta
from flask import Blueprint, flash, redirect, render_template, url_for
from flask_login import current_user, login_required
import pytz

from lib.safe_string import safe_message
from plataforma_web.blueprints.usuarios.decorators import permission_required

from plataforma_web.blueprints.audiencias.models import Audiencia
from plataforma_web.blueprints.autoridades.models import Autoridad
from plataforma_web.blueprints.autoridades.forms import AutoridadEditForm, AutoridadNewForm
from plataforma_web.blueprints.bitacoras.models import Bitacora
from plataforma_web.blueprints.edictos.models import Edicto
from plataforma_web.blueprints.modulos.models import Modulo
from plataforma_web.blueprints.permisos.models import Permiso
from plataforma_web.blueprints.listas_de_acuerdos.models import ListaDeAcuerdo
from plataforma_web.blueprints.sentencias.models import Sentencia

MODULO = "AUTORIDADES"

autoridades = Blueprint("autoridades", __name__, template_folder="templates")

HOY = date.today()
BREVE_LIMITE_DIAS = 15
BREVE_DESDE_DATETIME = datetime(year=HOY.year, month=HOY.month, day=HOY.day) + timedelta(days=-BREVE_LIMITE_DIAS)
ZONA_HORARIA = pytz.timezone("America/Mexico_City")

TARJETA_SATISFACTORIA = "bg-light"
TARJETA_ADVERTENCIA = "bg-warning"
TARJETA_VACIA = "bg-danger"
TARJETAS_LIMITE_REGISTROS = 5


@autoridades.before_request
@login_required
@permission_required(MODULO, Permiso.VER)
def before_request():
    """Permiso por defecto"""


@autoridades.route("/autoridades")
def list_active():
    """Listado de Autoridades activos"""
    return render_template(
        "autoridades/list.jinja2",
        autoridades=Autoridad.query.filter(Autoridad.estatus == "A").all(),
        titulo="Autoridades",
        estatus="A",
    )


@autoridades.route("/autoridades/inactivos")
@permission_required(MODULO, Permiso.MODIFICAR)
def list_inactive():
    """Listado de Autoridades inactivos"""
    return render_template(
        "autoridades/list.jinja2",
        autoridades=Autoridad.query.filter(Autoridad.estatus == "B").all(),
        titulo="Autoridades inactivas",
        estatus="B",
    )


@autoridades.route("/autoridades/<int:autoridad_id>")
def detail(autoridad_id):
    """Detalle de un Autoridad"""
    autoridad = Autoridad.query.get_or_404(autoridad_id)
    return render_template("autoridades/detail.jinja2", autoridad=autoridad)


@autoridades.route("/autoridades/<int:autoridad_id>/audiencias_json", methods=["GET", "POST"])
def audiencias_json(autoridad_id):
    """Audiencias de una Autoridad en JSON"""
    autoridad = Autoridad.query.get_or_404(autoridad_id)
    audiencias = Audiencia.query.filter(Audiencia.autoridad == autoridad).filter_by(estatus="A")
    # Listado
    listado = []
    desde = datetime.now()  # Desde este momento
    for audiencia in audiencias.filter(Audiencia.tiempo >= desde).order_by(Audiencia.tiempo).limit(TARJETAS_LIMITE_REGISTROS).all():
        listado.append(
            {
                "tiempo": audiencia.tiempo.strftime("%Y-%m-%d %H:%M"),
                "tipo_audiencia": audiencia.tipo_audiencia,
                "url": url_for("audiencias.detail", audiencia_id=audiencia.id),
            }
        )
    # Breve
    estilo = TARJETA_SATISFACTORIA
    total = audiencias.count()
    if total > 0:
        breve = f"Total {total}. "
        if len(listado) > 0:
            breve += "Desde " + desde.strftime("%Y-%m-%d %H:%M") + ". "
        else:
            breve += "No hay eventos en la agenda de hoy."
            estilo = TARJETA_ADVERTENCIA
    else:
        breve = "Nunca ha agendado Audiencias. "
        estilo = TARJETA_VACIA
    # Entregar JSON
    return {
        "titulo": "Agenda de Audiencias",
        "breve": breve,
        "listado": listado,
        "url": url_for("audiencias.list_autoridad_audiencias", autoridad_id=autoridad_id),
        "style": estilo,
    }


@autoridades.route("/autoridades/<int:autoridad_id>/edictos_json", methods=["GET", "POST"])
def edictos_json(autoridad_id):
    """Edictos de una Autoridad en JSON"""
    autoridad = Autoridad.query.get_or_404(autoridad_id)
    edictos = Edicto.query.filter(Edicto.autoridad == autoridad).filter_by(estatus="A")
    # Listado
    listado = []
    for edicto in edictos.order_by(Edicto.creado.desc()).limit(TARJETAS_LIMITE_REGISTROS).all():
        listado.append(
            {
                "expediente": edicto.expediente,
                "descripcion": edicto.descripcion,
                "url": url_for("edictos.detail", edicto_id=edicto.id),
            }
        )
    # Breve
    estilo = TARJETA_SATISFACTORIA
    total = edictos.count()
    if total > 0:
        breve = f"Total {total}. "
        cantidad = edictos.filter(Edicto.creado >= BREVE_DESDE_DATETIME).count()
        if cantidad > 0:
            breve += f"Se subieron {cantidad} en {BREVE_LIMITE_DIAS} días."
        else:
            breve += f"Ninguno en {BREVE_LIMITE_DIAS} días."
            estilo = TARJETA_ADVERTENCIA
    else:
        breve = "Nunca a subido Edictos."
        estilo = TARJETA_VACIA
    # Entregar JSON
    return {
        "titulo": "Edictos",
        "breve": breve,
        "listado": listado,
        "url": url_for("edictos.list_autoridad_edictos", autoridad_id=autoridad_id),
        "style": estilo,
    }


@autoridades.route("/autoridades/<int:autoridad_id>/listas_de_acuerdos_json", methods=["GET", "POST"])
def listas_de_acuerdos_json(autoridad_id):
    """Listas de Acuerdos de una Autoridad en JSON"""
    autoridad = Autoridad.query.get_or_404(autoridad_id)
    listas_de_acuerdos = ListaDeAcuerdo.query.filter(ListaDeAcuerdo.autoridad == autoridad).filter_by(estatus="A")
    # Listado
    listado = []
    for lista_de_acuerdo in listas_de_acuerdos.order_by(ListaDeAcuerdo.creado.desc()).limit(TARJETAS_LIMITE_REGISTROS).all():
        listado.append(
            {
                "fecha": lista_de_acuerdo.fecha.strftime("%Y-%m-%d"),
                "url": url_for("listas_de_acuerdos.detail", lista_de_acuerdo_id=lista_de_acuerdo.id),
            }
        )
    # Breve
    estilo = TARJETA_SATISFACTORIA
    total = listas_de_acuerdos.count()
    if total > 0:
        breve = f"Total {total}. "
    else:
        breve = "Nunca a subido Listas de Acuerdos."
        estilo = TARJETA_VACIA
    # Entregar JSON
    return {
        "titulo": "Listas de Acuerdos",
        "breve": breve,
        "listado": listado,
        "url": url_for("listas_de_acuerdos.list_autoridad_listas_de_acuerdos", autoridad_id=autoridad_id),
        "style": estilo,
    }


@autoridades.route("/autoridades/<int:autoridad_id>/sentencias_json", methods=["GET", "POST"])
def sentencias_json(autoridad_id):
    """Sentencias de una Autoridad en JSON"""
    autoridad = Autoridad.query.get_or_404(autoridad_id)
    sentencias = Sentencia.query.filter(Sentencia.autoridad == autoridad).filter_by(estatus="A")
    # Listado
    listado = []
    for sentencia in sentencias.order_by(Sentencia.creado.desc()).limit(TARJETAS_LIMITE_REGISTROS).all():
        listado.append(
            {
                "sentencia": sentencia.sentencia,
                "materia_tipo_juicio": sentencia.materia_tipo_juicio.descripcion,
                "url": url_for("sentencias.detail", sentencia_id=sentencia.id),
            }
        )
    # Breve
    estilo = TARJETA_SATISFACTORIA
    total = sentencias.count()
    if total > 0:
        breve = f"Total {total}. "
        cantidad = sentencias.filter(Sentencia.creado >= BREVE_DESDE_DATETIME).count()
        if cantidad > 0:
            breve += f"Se subieron {cantidad} en {BREVE_LIMITE_DIAS} días."
        else:
            breve += f"Ninguno en {BREVE_LIMITE_DIAS} días."
            estilo = TARJETA_ADVERTENCIA
    else:
        breve = "Nunca a subido V.P. de Sentencias."
        estilo = TARJETA_VACIA
    # Entregar JSON
    return {
        "titulo": "V.P. de Sentencias",
        "breve": breve,
        "listado": listado,
        "url": url_for("sentencias.list_autoridad_sentencias", autoridad_id=autoridad_id),
        "style": estilo,
    }


@autoridades.route("/autoridades/nuevo", methods=["GET", "POST"])
@permission_required(MODULO, Permiso.CREAR)
def new():
    """Nuevo Autoridad"""
    form = AutoridadNewForm()
    if form.validate_on_submit():
        distrito = form.distrito.data
        descripcion = form.descripcion.data.strip()
        es_jurisdiccional = form.es_jurisdiccional.data
        es_notaria = form.es_notaria.data
        directorio = f"{distrito.nombre}/{descripcion}"
        directorio_listas_de_acuerdos = ""
        directorio_sentencias = ""
        directorio_edictos = ""
        directorio_glosas = ""
        limite_dias_listas_de_acuerdos = 0
        if es_jurisdiccional:
            directorio_edictos = directorio
            directorio_listas_de_acuerdos = directorio
            directorio_sentencias = directorio
            directorio_glosas = directorio
            limite_dias_listas_de_acuerdos = 1
        if es_notaria:
            directorio_edictos = directorio
        autoridad = Autoridad(
            distrito=distrito,
            descripcion=descripcion,
            descripcion_corta=form.descripcion_corta.data.strip(),
            clave=form.clave.data.strip().upper(),
            es_jurisdiccional=es_jurisdiccional,
            es_notaria=es_notaria,
            organo_jurisdiccional=form.organo_jurisdiccional.data,
            materia=form.materia.data,
            audiencia_categoria=form.audiencia_categoria.data,
            directorio_listas_de_acuerdos=directorio_listas_de_acuerdos,
            directorio_sentencias=directorio_sentencias,
            directorio_edictos=directorio_edictos,
            directorio_glosas=directorio_glosas,
            limite_dias_listas_de_acuerdos=limite_dias_listas_de_acuerdos,
        )
        autoridad.save()
        bitacora = Bitacora(
            modulo=Modulo.query.filter_by(nombre=MODULO).first(),
            usuario=current_user,
            descripcion=safe_message(f"Nueva autoridad {autoridad.clave}"),
            url=url_for("autoridades.detail", autoridad_id=autoridad.id),
        )
        bitacora.save()
        flash(bitacora.descripcion, "success")
        return redirect(bitacora.url)
    return render_template("autoridades/new.jinja2", form=form)


@autoridades.route("/autoridades/edicion/<int:autoridad_id>", methods=["GET", "POST"])
@permission_required(MODULO, Permiso.MODIFICAR)
def edit(autoridad_id):
    """Editar Autoridad"""
    autoridad = Autoridad.query.get_or_404(autoridad_id)
    form = AutoridadEditForm()
    if form.validate_on_submit():
        autoridad.distrito = form.distrito.data
        autoridad.descripcion = form.descripcion.data.strip()
        autoridad.descripcion_corta = form.descripcion_corta.data.strip()
        autoridad.clave = form.clave.data.strip().upper()
        autoridad.es_jurisdiccional = form.es_jurisdiccional.data
        autoridad.es_notaria = form.es_notaria.data
        autoridad.organo_jurisdiccional = form.organo_jurisdiccional.data
        autoridad.materia = form.materia.data
        autoridad.audiencia_categoria = form.audiencia_categoria.data
        autoridad.directorio_listas_de_acuerdos = form.directorio_listas_de_acuerdos.data.strip()
        autoridad.directorio_sentencias = form.directorio_sentencias.data.strip()
        autoridad.directorio_edictos = form.directorio_edictos.data.strip()
        autoridad.directorio_glosas = form.directorio_glosas.data.strip()
        autoridad.limite_dias_listas_de_acuerdos = form.limite_dias_listas_de_acuerdos.data
        autoridad.save()
        bitacora = Bitacora(
            modulo=Modulo.query.filter_by(nombre=MODULO).first(),
            usuario=current_user,
            descripcion=safe_message(f"Editada autoridad {autoridad.clave}"),
            url=url_for("autoridades.detail", autoridad_id=autoridad.id),
        )
        bitacora.save()
        flash(bitacora.descripcion, "success")
        return redirect(bitacora.url)
    form.distrito.data = autoridad.distrito
    form.descripcion.data = autoridad.descripcion
    form.descripcion_corta.data = autoridad.descripcion_corta
    form.clave.data = autoridad.clave
    form.es_jurisdiccional.data = autoridad.es_jurisdiccional
    form.es_notaria.data = autoridad.es_notaria
    form.organo_jurisdiccional.data = autoridad.organo_jurisdiccional
    form.materia.data = autoridad.materia
    form.audiencia_categoria.data = autoridad.audiencia_categoria
    form.directorio_listas_de_acuerdos.data = autoridad.directorio_listas_de_acuerdos
    form.directorio_sentencias.data = autoridad.directorio_sentencias
    form.directorio_edictos.data = autoridad.directorio_edictos
    form.directorio_glosas.data = autoridad.directorio_glosas
    form.limite_dias_listas_de_acuerdos.data = autoridad.limite_dias_listas_de_acuerdos
    return render_template("autoridades/edit.jinja2", form=form, autoridad=autoridad)


@autoridades.route("/autoridades/eliminar/<int:autoridad_id>")
@permission_required(MODULO, Permiso.MODIFICAR)
def delete(autoridad_id):
    """Eliminar Autoridad"""
    autoridad = Autoridad.query.get_or_404(autoridad_id)
    if autoridad.estatus == "A":
        autoridad.delete()
        bitacora = Bitacora(
            modulo=Modulo.query.filter_by(nombre=MODULO).first(),
            usuario=current_user,
            descripcion=safe_message(f"Eliminada autoridad {autoridad.clave}"),
            url=url_for("autoridades.detail", autoridad_id=autoridad.id),
        )
        bitacora.save()
        flash(bitacora.descripcion, "success")
        return redirect(bitacora.url)
    return redirect(url_for("autoridades.detail", autoridad_id=autoridad.id))


@autoridades.route("/autoridades/recuperar/<int:autoridad_id>")
@permission_required(MODULO, Permiso.MODIFICAR)
def recover(autoridad_id):
    """Recuperar Autoridad"""
    autoridad = Autoridad.query.get_or_404(autoridad_id)
    if autoridad.estatus == "B":
        autoridad.recover()
        bitacora = Bitacora(
            modulo=Modulo.query.filter_by(nombre=MODULO).first(),
            usuario=current_user,
            descripcion=safe_message(f"Recuperada autoridad {autoridad.clave}"),
            url=url_for("autoridades.detail", autoridad_id=autoridad.id),
        )
        bitacora.save()
        flash(bitacora.descripcion, "success")
        return redirect(bitacora.url)
    return redirect(url_for("autoridades.detail", autoridad_id=autoridad.id))

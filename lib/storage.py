"""
Storage

Subir archivos a Google Storage estandarizando el nombre del archivo y la ruta.

Ejemplo

En una constante defina el directorio en el depósito donde se guardarán los archivos

    SUBDIRECTORIO = "cid_formatos"

Valide la descripción o los textos que formarán parte del nombre del archivo

    # Si viene el formulario
    form = CIDFormatoForm(CombinedMultiDict((request.files, request.form)))
    if form.validate_on_submit():
        es_valido = True
        # Validar la descripción
        descripcion = safe_string(form.descripcion.data)
        if descripcion == "":
            flash("La descripción es requerida.", "warning")
            es_valido = False

Valide el nombre y el tipo de contenido del archivo

        # Validar el archivo
        archivo = request.files["archivo"]
        storage = Storage(SUBDIRECTORIO)
        try:
            storage.set_content_type(archivo.filename)
        except NotAllowedExtesionError:
            flash("Tipo de archivo no permitido.", "warning")
            es_valido = False
        except UnknownExtesionError:
            flash("Tipo de archivo desconocido.", "warning")
            es_valido = False

Al definir la instancia de Storage...

- Si no proporciona la fecha con upload_date, la fecha por defecto es la de hoy
- Si no proporciona un listado de extensiones permitidas, se admitirán todas las programadas

Guarde el registro en la base de datos para poder obtener el ID hasheado

        # Si es válido
        if es_valido:
            # Insertar el registro, para obtener el ID
            cid_formato = CIDFormato(
                procedimiento=cid_procedimiento,
                descripcion=descripcion,
            )
            cid_formato.save()

Defina el nombre guardado en el depósito y suba

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

Tenga en cuenta que...

- Tendrá el formato YYYY-MM-DD-description-hashed_id.extension
- La ruta del archivo en el depósito quedará de la forma /base_directory/year/month/filename
- Si la descripción es texto vacío se usará SIN-DESCRIPCION
- Si el hashed_id es texto vacio el formato será YYYY-MM-DD-description.extension
- Si la descripción tiene más de 64 caracteres será recortada a esa longitud; puede cambiar este máximo pasando max_length
- Puede guardar en la base de datos el nombre que se le dio al archivo en el depósito con registro.archivo = storage.filename

"""
import datetime
import re
from datetime import datetime, date
from pathlib import Path
from unidecode import unidecode

from flask import current_app
from google.cloud import storage
from werkzeug.utils import secure_filename


class NotAllowedExtesionError(Exception):
    """Exception raised when the extension is not allowed"""


class UnknownExtesionError(Exception):
    """Exception raised when the extension is unknown"""


class NoneFilenameError(Exception):
    """Exception raised when the filename is None"""


class NotConfiguredError(Exception):
    """Exception raised when a environment variable is not configured"""


class Storage:
    """Storage"""

    EXTENSIONS_MIME_TYPES = {
        "docx": "application/msword",
        "pdf": "application/pdf",
        "xls": "xapplication/vnd.ms-excel",
        "jpg": "image/jpeg",
        "png": "image/png",
    }

    def __init__(self, base_directory: str, upload_date: date = None, allowed_extensions: list = None):
        """Storage constructor"""
        self.base_directory = base_directory
        if upload_date is None:
            self.upload_date = datetime.now()
        else:
            self.upload_date = upload_date
        if allowed_extensions is None:
            self.allowed_extensions = self.EXTENSIONS_MIME_TYPES.keys()
        else:
            self.allowed_extensions = allowed_extensions
        self.extension = None
        self.filename = None
        self.url = None
        self.content_type = None

    def set_content_type(self, original_filename: str):
        """Set content type from original filename, casuses an error on wrong extension"""
        self.extension = None
        self.filename = None
        self.url = None
        self.content_type = None
        original_filename = secure_filename(original_filename)
        if "." not in original_filename:
            raise NotAllowedExtesionError
        extension = original_filename.rsplit(".", 1)[1].lower()
        if extension not in self.allowed_extensions:
            raise NotAllowedExtesionError
        try:
            self.content_type = self.EXTENSIONS_MIME_TYPES[extension]
        except KeyError as error:
            raise UnknownExtesionError from error
        self.extension = extension
        return self.extension

    def set_filename(self, hashed_id: str = "", description: str = "", max_length: int = 64):
        """Filename standarize, returns the filename"""
        self.filename = None
        if self.extension is None:
            raise UnknownExtesionError
        description = re.sub(r"[^a-zA-Z0-9()-]+", " ", unidecode(description)).upper()
        if len(description) > max_length:
            description = description[:max_length]
        description = re.sub(r"\s+", " ", description).strip()
        if description == "":
            description = "SIN-DESCRIPCION"
        upload_date_str = self.upload_date.strftime("%Y-%m-%d")
        if hashed_id == "":
            self.filename = f"{upload_date_str}-{description}.{self.extension}"
        else:
            self.filename = f"{upload_date_str}-{description}-{hashed_id}.{self.extension}"
        return self.filename

    def upload(self, data):
        """Storage upload to Google Storage, returns the public URL"""
        self.url = None
        if self.filename is None:
            raise NoneFilenameError
        if self.content_type is None:
            raise UnknownExtesionError
        year_str = self.upload_date.strftime("%Y")
        month_str = self.upload_date.strftime("%m")
        path_str = str(Path(self.base_directory, year_str, month_str, self.filename))
        try:
            bucket_name = current_app.config["CLOUD_STORAGE_DEPOSITO"]
        except KeyError as error:
            raise NotConfiguredError from error
        storage_client = storage.Client()
        bucket = storage_client.bucket(bucket_name)
        blob = bucket.blob(path_str)
        blob.upload_from_string(data, self.content_type)
        self.url = blob.public_url
        return self.url

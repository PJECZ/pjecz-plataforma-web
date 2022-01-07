"""
Storage

Subir archivos a Google Storage estandarizando el nombre del archivo y la ruta.

En una constante defina el directorio en el depósito donde se guardarán los archivos

    SUBDIRECTORIO = "cid_formatos"

Guarde el registro en la base de datos para poder obtener el ID hasheado

    registro.descripcion = "Esto es una descripción"
    registro.save()

Inicialice una instancia de la clase Storage

    storage = Storage(SUBDIRECTORIO)

Tenga en cuenta que...

- Si no proporciona la fecha con upload_date, la fecha por defecto es la de hoy
- Si no proporciona el tipo de contenido con content_type, el tipo por defecto es application/pdf

Defina el nombre del archivo con el que sera guadado en el depósito

    storage.set_filename(registro.encode_id(), registro.descripcion)

Tenga en cuenta que...

- Tendrá el formato YYYY-MM-DD-description-hashed_id.extension
- Si la descripción es texto vacío se usará SIN-DESCRIPCION
- Si el hashed_id es texto vacio el formato será YYYY-MM-DD-description.extension
- Si la descripción tiene más de 64 caracteres será recortada a esa longitud; puede cambiar este máximo pasando max_length

Tome el archivo que viene en el formulario

    archivo = request.files["archivo"]

Suba el archivo al depósito

    if storage.upload(archivo.stream.read(), directorio_base) is not None:
        registro.archivo = secure_filename(archivo.filename)
        registro.url = storage.url
        registro.save()

Note que:

- La ruta del archivo en el depósito quedará de la forma /base_directory/year/month/filename
- Puede guardar en la base de datos el nombre que se le dio al archivo en el depósito con registro.archivo = storage.filename

"""
import datetime
import re
from datetime import datetime, date
from pathlib import Path
from unidecode import unidecode

from flask import current_app
from google.cloud import storage


class Storage:
    """Storage"""

    MIME_TYPES_EXTENSIONS = {
        "application/msword": "docx",
        "application/pdf": "pdf",
        "application/vnd.ms-excel": "xlsx",
        "image/jpeg": "jpg",
        "image/png": "png",
    }

    def __init__(self, base_directory: str, upload_date: date = None, content_type: str = "application/pdf"):
        """Storage constructor"""
        self.base_directory = base_directory
        if upload_date is None:
            self.upload_date = datetime.now()
        else:
            self.upload_date = upload_date
        if content_type in self.MIME_TYPES_EXTENSIONS:
            self.content_type = content_type
        else:
            self.content_type = "application/pdf"
        self.filename = None
        self.url = None

    def set_filename(self, hashed_id: str = "", description: str = "", max_length: int = 64):
        """Filename standarize YYYY-MM-DD-description-hashed_id.extension"""
        description = re.sub(r"[^a-zA-Z0-9()-]+", " ", unidecode(description)).upper()
        if len(description) > max_length:
            description = description[:max_length]
        description = re.sub(r"\s+", " ", description).strip()
        if description == "":
            description = "SIN-DESCRIPCION"
        upload_date_str = self.upload_date.strftime("%Y-%m-%d")
        extension = self.MIME_TYPES_EXTENSIONS[self.content_type]
        if hashed_id == "":
            self.filename = f"{upload_date_str}-{description}.{extension}"
        else:
            self.filename = f"{upload_date_str}-{description}-{hashed_id}.{extension}"
        return self.filename

    def set_path(self):
        """Path standarize /base_directory/year/month/filename"""
        if self.filename is None:
            return None
        upload_year_str = self.upload_date.strftime("%Y")
        upload_month_str = self.upload_date.strftime("%m")
        return str(Path(self.base_directory, upload_year_str, upload_month_str, self.filename))

    def upload(self, data):
        """Storage upload to Google Storage, returns the public URL"""
        self.url = None
        if self.filename is None:
            return None
        try:
            bucket_name = current_app.config["CLOUD_STORAGE_DEPOSITO"]
        except KeyError:
            return None
        storage_client = storage.Client()
        bucket = storage_client.bucket(bucket_name)
        blob = bucket.blob(self.set_path())
        blob.upload_from_string(data, self.content_type)
        self.url = blob.public_url
        return self.url

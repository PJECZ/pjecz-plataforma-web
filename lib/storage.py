"""
Storage

Sirve para subir archivos a Google Storage estandarizando el nombre del archivo y la ruta.

storage = Storage(hash_id, descripcion)
archivo = storage.filename()
url = storage.upload(datos, directorio_base)

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

    def __init__(self, hashed_id: str, description: str, upload_date: date = None, content_type: str = "application/pdf"):
        self.hashed_id = hashed_id
        self.description = description
        if upload_date is None:
            self.upload_date = datetime.now()
        else:
            self.upload_date = upload_date
        if content_type in self.MIME_TYPES_EXTENSIONS:
            self.content_type = content_type
        else:
            self.content_type = "application/pdf"

    def filename(self, length: int = 24):
        """Filename standarize YYYY-MM-DD-description-hashed_id.extension"""
        upload_date_str = self.upload_date.strftime("%Y-%m-%d")
        description_valid = re.sub(r"[^a-zA-Z0-9()-]+", " ", unidecode(self.description)).upper()
        description_clean = re.sub(r"\s+", " ", description_valid).strip()
        if description_clean == "":
            description_clean = "SIN-DESCRIPCION"
        elif len(description_clean) > length:
            description_clean = description_clean[:length]
        try:
            extension = self.MIME_TYPES_EXTENSIONS[self.content_type]
        except KeyError:
            extension = "pdf"
        return f"{upload_date_str}-{description_clean}-{self.hashed_id}.{extension}"

    def path(self, base_directory: str):
        """Path standarize /base_directory/year/month/filename"""
        if self.upload_date is None:
            upload_date = datetime.now()
        upload_year_str = upload_date.strftime("%Y")
        upload_month_str = upload_date.strftime("%m")
        return str(Path(base_directory, upload_year_str, upload_month_str, self.filename()))

    def upload(self, data, base_directory: str):
        """Storage upload to Google Storage, returns the public URL"""
        storage_client = storage.Client()
        try:
            bucket_name = current_app.config["CLOUD_STORAGE_DEPOSITO"]
        except KeyError:
            return ""
        bucket = storage_client.bucket(bucket_name)
        blob = bucket.blob(self.path(base_directory))
        blob.upload_from_string(data, self.content_type)
        return blob.public_url

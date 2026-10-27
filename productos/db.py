import django.conf
from pymongo import MongoClient


if not django.conf.settings.MONGO_URI:
    raise RuntimeError(
        "Falta configurar MONGO_URI en el archivo .env"
    )


cliente = MongoClient(
    django.conf.settings.MONGO_URI,
    serverSelectionTimeoutMS=5000
)

db = cliente[django.conf.settings.MONGO_DB]

coleccion_productos = db["productos"]

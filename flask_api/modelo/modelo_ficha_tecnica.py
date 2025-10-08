# flask_api/modelo/modelo_ficha_tecnica.py
from bson import ObjectId
from flask import current_app
from datetime import datetime, timezone

def get_fichas_collection():
    return current_app.mongo.db.fichas_tecnicas

def _now_utc():
    return datetime.now(timezone.utc)

def guardar_ficha(ficha_doc):

    col = get_fichas_collection()
    ficha_doc["createdAt"] = _now_utc()
    ficha_doc["updatedAt"] = _now_utc()
    if ficha_doc.get("user_id"):
        ficha_doc["user_id"] = ObjectId(ficha_doc["user_id"])
    if ficha_doc.get("prenda_id"):
        ficha_doc["prenda_id"] = ObjectId(ficha_doc["prenda_id"])
    res = col.insert_one(ficha_doc)
    return str(res.inserted_id)

def buscar_ficha(ficha_id: str):
    doc = get_fichas_collection().find_one({"_id": ObjectId(ficha_id)})
    return _serialize(doc) if doc else None

def listar_fichas(user_id: str = None):
    query = {}
    if user_id:
            query["user_id"] = ObjectId(user_id)
    fichas = list(get_fichas_collection().find(query).sort("createdAt", -1))
    return [_serialize(f) for f in fichas]

def eliminar_ficha(ficha_id: str):
    res = get_fichas_collection().delete_one({"_id": ObjectId(ficha_id)})
    return res.deleted_count > 0

def _serialize(doc):
    doc["_id"] = str(doc["_id"])
    if "prenda_id" in doc:
        doc["prenda_id"] = str(doc["prenda_id"])
    if "user_id" in doc:
        doc["user_id"] = str(doc["user_id"])
    if "createdAt" in doc and doc["createdAt"]:
        doc["createdAt"] = doc["createdAt"].isoformat()
    if "updatedAt" in doc and doc["updatedAt"]:
        doc["updatedAt"] = doc["updatedAt"].isoformat()
    return doc
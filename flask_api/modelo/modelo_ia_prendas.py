
from bson import ObjectId
from flask import current_app

def guardar_prenda(doc):
    prendas = current_app.mongo.db.prendas
    result = prendas.insert_one(doc)
    return str(result.inserted_id)

def listar_prendas(user_id):
    prendas_collection = current_app.mongo.db.prendas
    prendas = list(prendas_collection.find({"user_id": ObjectId(user_id)}))

    for prenda in prendas:
        prenda["_id"] = str(prenda["_id"])
        prenda["user_id"] = str(prenda["user_id"])
        prenda["imageUrl"] = prenda.get("imageUrl", None)

    return prendas

# flask_api/modelo/modelo_camiseta_ia.py
from bson import ObjectId
from flask import current_app

def guardar_camiseta(doc):

    camisetas = current_app.mongo.db.camisetasIA

    # Asegurar que user_id esté en formato ObjectId
    if isinstance(doc.get("user_id"), str):
        try:
            doc["user_id"] = ObjectId(doc["user_id"])
        except Exception:
            pass

    result = camisetas.insert_one(doc)
    return str(result.inserted_id)


def listar_camisetas(user_id):

    camisetas = current_app.mongo.db.camisetasIA
    docs = list(camisetas.find({"user_id": ObjectId(user_id)}))

    for d in docs:
        d["_id"] = str(d["_id"])
        d["user_id"] = str(d["user_id"])
        # Asegurar que atributos siempre sea dict
        if "atributos" not in d:
            d["atributos"] = {}
    return docs

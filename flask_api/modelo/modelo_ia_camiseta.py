# flask_api/modelo/modelo_ia_camiseta.py
from bson import ObjectId
from flask import current_app

def guardar_camiseta(doc: dict) -> str:
    col = current_app.mongo.db.camisetasIA  # colección separada
    result = col.insert_one(doc)
    return str(result.inserted_id)

def listar_camisetas_db(user_id: str) -> list:
    col = current_app.mongo.db.camisetasIA
    docs = list(col.find({"user_id": ObjectId(user_id)}))
    for d in docs:
        d["_id"] = str(d["_id"])
        d["user_id"] = str(d["user_id"])
    return docs

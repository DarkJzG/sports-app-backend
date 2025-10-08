# flask_api/modelo/modelo_ia_texturas.py
from flask import current_app
from bson import ObjectId

def guardar_textura(doc):
    """Guarda una textura generada en la colección 'texturas'."""
    texturas = current_app.mongo.db.texturas
    result = texturas.insert_one(doc)
    return str(result.inserted_id)

def listar_texturas(user_id):
    """Lista todas las texturas generadas por un usuario."""
    texturas_collection = current_app.mongo.db.texturas
    texturas = list(texturas_collection.find({"user_id": ObjectId(user_id)}))

    for tex in texturas:
        tex["_id"] = str(tex["_id"])
        tex["user_id"] = str(tex["user_id"])
        tex["color_promedio"] = tex.get("color_promedio", "#FFFFFF")

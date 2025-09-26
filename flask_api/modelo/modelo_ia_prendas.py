# flask_api/modelo/modelo_ia_prendas.py
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
        prenda["costo"] = prenda.get("costo", None)
        prenda["precio_venta"] = prenda.get("precio_venta", None)   # ✅ añadir
        prenda["precio_mayor"] = prenda.get("precio_mayor", None)   # ✅ añadir
        prenda["ficha_tecnica"] = prenda.get("ficha_tecnica", {})

    return prendas


def buscar_prenda(prenda_id):
    prendas = current_app.mongo.db.prendas
    doc = prendas.find_one({"_id": ObjectId(prenda_id)})
    if not doc:
        return None
    doc["_id"] = str(doc["_id"])
    doc["user_id"] = str(doc["user_id"])
    doc["costo"] = doc.get("costo", None)             # ✅ asegurar costo
    doc["precio_venta"] = doc.get("precio_venta", None) # ✅ asegurar precio_venta
    doc["precio_mayor"] = doc.get("precio_mayor", None) # ✅ asegurar precio_mayor
    doc["ficha_tecnica"] = doc.get("ficha_tecnica", {})
    return doc


def eliminar_prenda(prenda_id):
    prendas = current_app.mongo.db.prendas
    result = prendas.delete_one({"_id": ObjectId(prenda_id)})
    return result.deleted_count > 0

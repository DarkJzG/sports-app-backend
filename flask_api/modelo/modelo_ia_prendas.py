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
        prenda["precio_venta"] = prenda.get("precio_venta", None)  
        prenda["precio_mayor"] = prenda.get("precio_mayor", None)
        prenda["ficha_id"] = str(prenda.get("ficha_id")) if prenda.get("ficha_id") else None


    return prendas


def buscar_prenda(prenda_id):
    prendas = current_app.mongo.db.prendas
    doc = prendas.find_one({"_id": ObjectId(prenda_id)})
    if not doc:
        return None
    doc["_id"] = str(doc["_id"])
    doc["user_id"] = str(doc["user_id"])
    doc["costo"] = doc.get("costo", None)             
    doc["precio_venta"] = doc.get("precio_venta", None) 
    doc["precio_mayor"] = doc.get("precio_mayor", None) 
    doc["ficha_id"] = str(doc["ficha_id"]) if doc.get("ficha_id") else None

    return doc


def eliminar_prenda(prenda_id):
    prendas = current_app.mongo.db.prendas
    result = prendas.delete_one({"_id": ObjectId(prenda_id)})
    return result.deleted_count > 0

def get_prendas_collection():
   
    return current_app.mongo.db.prendas

# flask_api/modelo/modelo_3d_prenda.py
from datetime import datetime
from bson import ObjectId
from flask import current_app

def guardar_prenda_3d(data):
    """Guarda el diseño 3D personalizado de una prenda en MongoDB."""
    import json
    
    # Conversión segura de cadenas JSON a sus estructuras correspondientes
    if isinstance(data.get("colors"), str):
        try: data["colors"] = json.loads(data["colors"])
        except: data["colors"] = {}
    if isinstance(data.get("textures"), str):
        try: data["textures"] = json.loads(data["textures"])
        except: data["textures"] = {}
    if isinstance(data.get("decals"), str):
        try: data["decals"] = json.loads(data["decals"])
        except: data["decals"] = []
    if isinstance(data.get("textDecals"), str):
        try: data["textDecals"] = json.loads(data["textDecals"])
        except: data["textDecals"] = []
    
    db = current_app.mongo.db
    coleccion = db["prendas_3d"]

    registro = {
        "user_id": ObjectId(data["user_id"]),
        "categoria": data.get("categoria", "camiseta"),
        "modelo": data.get("modelo"),
        "design_id": data.get("design_id"),
        "colors": data.get("colors", {}),
        "textures": data.get("textures", {}),
        "decals": data.get("decals", []),
        "textDecals": data.get("textDecals", []),
        "render_final": data.get("render_final"),
        "fecha_creacion": datetime.utcnow(),
        "fecha_actualizacion": datetime.utcnow(),
    }

    resultado = coleccion.insert_one(registro)
    return str(resultado.inserted_id)


def listar_prendas_3d(user_id):
    """Obtiene todos los diseños 3D de un usuario."""
    db = current_app.mongo.db
    coleccion = db["prendas_3d"]

    prendas = list(coleccion.find({"user_id": ObjectId(user_id)}).sort("fecha_creacion", -1))
    for p in prendas:
        p["_id"] = str(p["_id"])
        p["user_id"] = str(p["user_id"])
    return prendas


def obtener_prenda_3d(prenda_id):
    """Devuelve los datos de un diseño específico."""
    db = current_app.mongo.db
    coleccion = db["prendas_3d"]

    prenda = coleccion.find_one({"_id": ObjectId(prenda_id)})
    if prenda:
        prenda["_id"] = str(prenda["_id"])
        prenda["user_id"] = str(prenda["user_id"])
    return prenda

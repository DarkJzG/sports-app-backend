# flask_api/controlador/control_catg_tela.py
from flask import jsonify, request
from flask_api.modelo.modelo_catg_tela import get_catg_tela_collection
from bson import ObjectId
from datetime import datetime

# Crear categoría de tela
def crear_catg_tela():
    data = request.get_json()
    nombre = data.get("nombre")
    abreviatura = data.get("abreviatura")
    descripcion = data.get("descripcion")

    if not nombre or not abreviatura or not descripcion:
        return jsonify({"ok": False, "msg": "Nombre, abreviatura y descripción son obligatorios"}), 400

    col = get_catg_tela_collection()

    # Validar duplicados por abreviatura
    if col.find_one({"abreviatura": abreviatura.upper()}):
        return jsonify({"ok": False, "msg": "Ya existe una categoría con esa abreviatura"}), 400

    nueva_cat = {
        "nombre": nombre,
        "abreviatura": abreviatura.upper(),
        "descripcion": descripcion,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }

    col.insert_one(nueva_cat)
    nueva_cat["_id"] = str(nueva_cat["_id"])
    return jsonify({"ok": True, "msg": "Categoría de tela creada", "categoria": nueva_cat})


# Listar categorías
def listar_catg_telas():
    col = get_catg_tela_collection()
    lista = list(col.find({}))
    for c in lista:
        c["_id"] = str(c["_id"])
    return jsonify(lista)


# Obtener una categoría
def obtener_catg_tela(id):
    col = get_catg_tela_collection()
    cat = col.find_one({"_id": ObjectId(id)})
    if not cat:
        return jsonify({"ok": False, "msg": "Categoría no encontrada"}), 404
    cat["_id"] = str(cat["_id"])
    return jsonify(cat)


# Actualizar categoría
def actualizar_catg_tela(id):
    data = request.get_json()
    update_fields = {}

    if "nombre" in data:
        update_fields["nombre"] = data["nombre"]
    if "abreviatura" in data:
        update_fields["abreviatura"] = data["abreviatura"].upper()
    if "descripcion" in data:
        update_fields["descripcion"] = data["descripcion"]

    update_fields["updated_at"] = datetime.utcnow()

    col = get_catg_tela_collection()
    col.update_one({"_id": ObjectId(id)}, {"$set": update_fields})
    return jsonify({"ok": True, "msg": "Categoría actualizada"})


# Eliminar categoría
def eliminar_catg_tela(id):
    col = get_catg_tela_collection()
    result = col.delete_one({"_id": ObjectId(id)})
    if result.deleted_count:
        return jsonify({"ok": True, "msg": "Categoría eliminada"})
    else:
        return jsonify({"ok": False, "msg": "Categoría no encontrada"}), 404

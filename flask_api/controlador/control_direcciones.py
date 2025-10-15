from flask import jsonify
from bson import ObjectId
from flask_api.modelo.modelo_usuario import get_direcciones_collection

def agregar_direccion(user_id: str, data: dict):
    col = get_direcciones_collection()
    data["user_id"] = ObjectId(user_id)
    data["es_predeterminada"] = data.get("es_predeterminada", False)
    res = col.insert_one(data)
    if res.inserted_id:
        return jsonify({"ok": True, "msg": "Dirección agregada", "id": str(res.inserted_id)}), 201
    return jsonify({"ok": False, "msg": "Error al agregar dirección"}), 400


def listar_direcciones(user_id: str):
    col = get_direcciones_collection()
    direcciones = list(col.find({"user_id": ObjectId(user_id)}))
    for d in direcciones:
        d["_id"] = str(d["_id"])
        d["user_id"] = str(d["user_id"])
    return jsonify({"ok": True, "direcciones": direcciones}), 200


def eliminar_direccion(dir_id: str):
    col = get_direcciones_collection()
    res = col.delete_one({"_id": ObjectId(dir_id)})
    if res.deleted_count == 1:
        return jsonify({"ok": True, "msg": "Dirección eliminada"}), 200
    return jsonify({"ok": False, "msg": "No se encontró la dirección"}), 404

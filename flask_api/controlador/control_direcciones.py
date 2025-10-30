from flask import jsonify
from bson import ObjectId
from flask_api.modelo.modelo_usuario import get_direcciones_collection

def agregar_direccion(user_id: str, data: dict):
    col = get_direcciones_collection()
    data["user_id"] = ObjectId(user_id)
    es_predeterminada = data.get("es_predeterminada", False)    
    
    count = col.count_documents({"user_id": ObjectId(user_id)})
    if count >= 3:
        return jsonify({"ok": False, "msg": "Máximo 3 direcciones, elimina una para agregar otra"}), 400
        
    if es_predeterminada:
        col.update_many(
            {"user_id": ObjectId(user_id), "es_predeterminada": True},
            {"$set": {"es_predeterminada": False}}
        )
    elif count == 0:
        data["es_predeterminada"] = True

    res = col.insert_one(data)
    if res.inserted_id:
        return jsonify({"ok": True, "msg": "Dirección agregada", "id": str(res.inserted_id)}), 201
    return jsonify({"ok": False, "msg": "Error al agregar dirección"}), 400

def actualizar_direcciones(user_id: str, dir_id: str, data: dict):
    col = get_direcciones_collection()

    update_data={k: v for k, v in data.items() if k not in ["_id", "user_id"]}
    es_predeterminada= update_data.get("es_predeterminada", False)
    
    if es_predeterminada:
        col.update_many(
            {"user_id": ObjectId(user_id), "es_predeterminada": True},
            {"$set": {"es_predeterminada": False}}
        )
    
    res = col.update_one(
        {"_id": ObjectId(dir_id), "user_id": ObjectId(user_id)},
        {"$set": update_data}
    )

    if res.matched_count == 0:
        return jsonify({"ok": False, "msg": "No se encontró la dirección"}), 404
    if res.modified_count == 1:
        return jsonify({"ok": True, "msg": "Dirección actualizada"}), 200
    return jsonify({"ok": False, "msg": "Sin Cambios"}), 200

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

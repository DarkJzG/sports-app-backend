# flask_api/controlador/control_usuario.py
from flask import jsonify
from bson import ObjectId
from flask_api.modelo.modelo_usuario import get_users_collection

def actualizar_perfil(user_id: str, data: dict):
    col = get_users_collection()
    update = {
        "nombre": data.get("nombre"),
        "apellido": data.get("apellido"),
        "cedula": data.get("cedula"),

    }
    # limpiar None
    update = {k: v for k, v in update.items() if v is not None}

    res = col.update_one({"_id": ObjectId(user_id)}, {"$set": update})
    if res.modified_count == 1:
        return jsonify({"ok": True, "msg": "Perfil actualizado"}), 200
    return jsonify({"ok": False, "msg": "No se actualizó"}), 400

from flask import jsonify, current_app
from flask_api.modelo.modelo_prendas_ia import ModeloPrendasIA
from bson.objectid import ObjectId

def listar_prendas(user_id=None):
    prendas = ModeloPrendasIA.obtener_todas(user_id)
    for p in prendas:
        p["_id"] = str(p["_id"])
    return jsonify({"ok": True, "prendas": prendas})


def obtener_prenda(prenda_id):
    prenda = ModeloPrendasIA.obtener_por_id(prenda_id)
    if prenda:
        prenda["_id"] = str(prenda["_id"])
        return jsonify({"ok": True, "prenda": prenda})
    return jsonify({"ok": False, "msg": "Prenda no encontrada"}), 404

def eliminar_prenda(prenda_id):
    try:
        ModeloPrendasIA.eliminar_prenda(prenda_id)
        return jsonify({"ok": True, "msg": "Prenda eliminada"})
    except Exception as e:
        return jsonify({"ok": False, "msg": str(e)})

def actualizar_prenda(prenda_id, data):
    try:
        ModeloPrendasIA.actualizar_prenda(prenda_id, data)
        return jsonify({"ok": True, "msg": "Prenda actualizada"})
    except Exception as e:
        return jsonify({"ok": False, "msg": str(e)})

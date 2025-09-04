from flask import jsonify
from flask_api.modelo.modelo_carrito import ModeloCarrito
from bson.json_util import dumps
from bson.objectid import ObjectId

def agregar_al_carrito(data):
    try:
        data["precio"] = float(data.get("precio", 0))
        data["cantidad"] = int(data.get("cantidad", 1))
        result = ModeloCarrito.agregar_carrito(data)
        return jsonify({"ok": True, "msg": "Producto añadido al carrito", "id": str(result.inserted_id)})
    except Exception as e:
        return jsonify({"ok": False, "msg": str(e)})

def obtener_carrito_usuario(user_id):
    try:
        productos = ModeloCarrito.obtener_carrito_usuario(user_id)
        return jsonify({"ok": True, "carrito": productos})
    except Exception as e:
        return jsonify({"ok": False, "msg": str(e)})
    



def obtener_item_carrito(item_id):
    print("🔍 Recibí item_id:", item_id)
    item = ModeloCarrito.obtener_item_por_id(item_id)
    if item:
        item["_id"] = str(item["_id"])  # 👈 Asegúrate de convertirlo a string
        return jsonify({"ok": True, "item": item})
    return jsonify({"ok": False, "msg": "Item no encontrado"}), 404





def eliminar_item_carrito(item_id):
    try:
        ModeloCarrito.eliminar_item_carrito(item_id)
        return jsonify({"ok": True, "msg": "Item eliminado del carrito"})
    except Exception as e:
        return jsonify({"ok": False, "msg": str(e)})

def vaciar_carrito_usuario(user_id):
    try:
        ModeloCarrito.vaciar_carrito_usuario(user_id)
        return jsonify({"ok": True, "msg": "Carrito vaciado"})
    except Exception as e:
        return jsonify({"ok": False, "msg": str(e)})

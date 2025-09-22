# flask_api/controlador/control_carrito.py
from flask import current_app, jsonify
from flask_api.modelo.modelo_carrito import ModeloCarrito
from bson.objectid import ObjectId

def agregar_al_carrito(data):
    """
    data: {
      userId, productoId, nombre, categoria_nombre, tela_nombre,
      color, talla, cantidad, precio_unitario, precio, imagen_url, estado
    }
    """
    try:
        cantidad = int(data.get("cantidad", 1))
        precio_unitario = float(data.get("precio_unitario", 0))
        precio = float(data.get("precio", 0))

        # Redondear a 2 decimales
        precio_unitario = round(precio_unitario, 2)
        precio = round(precio, 2)

        item = {
            "userId": data.get("userId"),
            "productoId": ObjectId(data["productoId"]) if data.get("productoId") else None,
            "nombre": data.get("nombre"),
            "categoria_nombre": data.get("categoria_nombre"),
            "tela_nombre": data.get("tela_nombre"),
            "color": data.get("color"),  # dict completo
            "talla": data.get("talla"),
            "cantidad": cantidad,
            "precio_unitario": precio_unitario,
            "precio": precio,
            "imagen_url": data.get("imagen_url"),
            "estado": data.get("estado", "pendiente"),
        }

        result = ModeloCarrito.agregar_carrito(item)
        return jsonify({
            "ok": True,
            "msg": "Producto añadido al carrito",
            "id": str(result.inserted_id)
        })

    except Exception as e:
        return jsonify({"ok": False, "msg": str(e)}), 500

def obtener_carrito_usuario(user_id):
    try:
        productos = ModeloCarrito.obtener_carrito_usuario(user_id)
        # Convertir ObjectId a string
        for p in productos:
            p["_id"] = str(p["_id"])
            if isinstance(p.get("productoId"), ObjectId):
                p["productoId"] = str(p["productoId"])
        return jsonify({"ok": True, "carrito": productos})
    except Exception as e:
        return jsonify({"ok": False, "msg": str(e)}), 500


def obtener_item_carrito(item_id):
    try:
        item = ModeloCarrito.obtener_item_por_id(item_id)
        if item:
            item["_id"] = str(item["_id"])
            if isinstance(item.get("productoId"), ObjectId):
                item["productoId"] = str(item["productoId"])
            return jsonify({"ok": True, "item": item})
        return jsonify({"ok": False, "msg": "Item no encontrado"}), 404
    except Exception as e:
        return jsonify({"ok": False, "msg": str(e)}), 500


def eliminar_item_carrito(item_id):
    try:
        ModeloCarrito.eliminar_item_carrito(item_id)
        return jsonify({"ok": True, "msg": "Item eliminado del carrito"})
    except Exception as e:
        return jsonify({"ok": False, "msg": str(e)}), 500


def vaciar_carrito_usuario(user_id):
    try:
        ModeloCarrito.vaciar_carrito_usuario(user_id)
        return jsonify({"ok": True, "msg": "Carrito vaciado"})
    except Exception as e:
        return jsonify({"ok": False, "msg": str(e)}), 500

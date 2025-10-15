# flask_api/rutas/ruta_carrito.py
from flask import Blueprint, request
from flask_api.controlador import control_carrito


carrito_bp = Blueprint("carrito", __name__, url_prefix="/carrito")

@carrito_bp.route("/add", methods=["POST"])
def add_carrito():
    data = request.json
    return control_carrito.agregar_al_carrito(data)

@carrito_bp.route("/<user_id>", methods=["GET"])
def get_carrito(user_id):
    return control_carrito.obtener_carrito_usuario(user_id)

@carrito_bp.route("/detalle/<item_id>", methods=["GET"])
def get_item_carrito(item_id):
    return control_carrito.obtener_item_carrito(item_id)

@carrito_bp.route("/delete/<item_id>", methods=["DELETE"])
def delete_item_carrito(item_id):
    return control_carrito.eliminar_item_carrito(item_id)

@carrito_bp.route("/vaciar/<user_id>", methods=["DELETE"])
def vaciar_carrito(user_id):
    return control_carrito.vaciar_carrito_usuario(user_id)

# -------------------------------
# Contador de productos en carrito
@carrito_bp.route("/count/<user_id>", methods=["GET", "OPTIONS"])
def contar_items_carrito(user_id):
    try:
        from flask import jsonify, current_app
        count = ModeloCarrito.contar_items_carrito(user_id)
        return jsonify({"ok": True, "count": count})
    except Exception as e:
        return jsonify({"ok": False, "msg": str(e)}), 500

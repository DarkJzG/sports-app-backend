# flask_api/ruta/ruta_pedido_ficha.py
from flask import Blueprint, jsonify
from flask_api.controlador.control_pedido_ficha import generar_ficha_tecnica_pedido

ruta_pedido_ficha = Blueprint("pedido_ficha", __name__, url_prefix="/pedido/ficha")

@ruta_pedido_ficha.route("/generar/<pedido_id>", methods=["POST"])
def generar_ficha_pedido(pedido_id):
    """
    Genera y sube a Cloudinary la ficha técnica consolidada de prendas IA.
    """
    try:
        result = generar_ficha_tecnica_pedido(pedido_id)
        return jsonify(result), (200 if result.get("ok") else 400)
    except Exception as e:
        return jsonify({"ok": False, "msg": str(e)}), 500

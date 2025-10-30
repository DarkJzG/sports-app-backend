# flask_api/rutas/ruta_factura.py
from flask import Blueprint, jsonify, current_app
from flask_api.controlador.control_factura import generar_factura_pdf, obtener_factura

factura_bp = Blueprint("factura", __name__, url_prefix="/factura")


@factura_bp.route("/generar/<pedido_id>", methods=["POST"])
def generar_factura_route(pedido_id):
    """
    Genera una factura PDF para un pedido.
    """
    try:
        success, resultado = generar_factura_pdf(pedido_id)
        
        if not success:
            return jsonify({"ok": False, "msg": resultado}), 400
        
        return jsonify({
            "ok": True,
            "msg": "Factura generada exitosamente",
            "facturaUrl": resultado
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Error en ruta generar factura: {str(e)}")
        return jsonify({"ok": False, "msg": str(e)}), 500


@factura_bp.route("/obtener/<pedido_id>", methods=["GET"])
def obtener_factura_route(pedido_id):
    """
    Obtiene la URL de la factura de un pedido.
    """
    return obtener_factura(pedido_id)

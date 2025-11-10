# flask_api/rutas/ruta_prendas_huggingface.py
from flask import Blueprint, request, jsonify
from flask_api.controlador.control_prendas_huggingface import generar_prenda_huggingface

ruta_prendas_hf = Blueprint("ruta_prendas_hf", __name__)


@ruta_prendas_hf.route("/api/ia/generar_prenda_hf", methods=["POST"])
def generar_prenda_hf():
    try:
        # Obtener datos del request
        data = request.get_json()
        
        if not data:
            return jsonify({
                "ok": False,
                "error": "No se recibieron datos en el request"
            }), 400
        
        # Extraer parámetros
        user_id = data.get("userId")
        categoria_id = data.get("categoria_id")
        
        # Validar categoria_id
        if not categoria_id:
            return jsonify({
                "ok": False,
                "error": "El campo 'categoria_id' es requerido"
            }), 400
        
        # Llamar al controlador unificado
        result = generar_prenda_huggingface(categoria_id, data, user_id)
        
        # Retornar resultado exitoso
        return jsonify({
            "ok": True,
            **result
        }), 200
        
    except Exception as e:
        print(f"\n❌ ERROR EN ENDPOINT /api/ia/generar_prenda_hf")
        print(f"❌ Detalle del error: {str(e)}\n")
        return jsonify({
            "ok": False,
            "error": str(e)
        }), 500


# Endpoints específicos para retrocompatibilidad
@ruta_prendas_hf.route("/api/ia/generar_camiseta_hf", methods=["POST"])
def generar_camiseta_hf():
    data = request.get_json()
    if not data.get("categoria_id"):
        data["categoria_id"] = "camiseta_ia_v3"
    request._cached_json = data
    return generar_prenda_hf()


@ruta_prendas_hf.route("/api/ia/generar_pantalon_hf", methods=["POST"])
def generar_pantalon_hf():
    data = request.get_json()
    if not data.get("categoria_id"):
        data["categoria_id"] = "pantalon_ia_v1"
    request._cached_json = data
    return generar_prenda_hf()


@ruta_prendas_hf.route("/api/ia/generar_chompa_hf", methods=["POST"])
def generar_chompa_hf():
    data = request.get_json()
    if not data.get("categoria_id"):
        data["categoria_id"] = "chompa_ia_v1"
    request._cached_json = data
    return generar_prenda_hf()


@ruta_prendas_hf.route("/api/ia/generar_pantaloneta_hf", methods=["POST"])
def generar_pantaloneta_hf():
    data = request.get_json()
    if not data.get("categoria_id"):
        data["categoria_id"] = "pantaloneta_ia_v1"
    request._cached_json = data
    return generar_prenda_hf()

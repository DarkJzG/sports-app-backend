# flask_api/rutas/ruta_ia_camiseta.py
from flask import Blueprint, request, jsonify, current_app
from bson import ObjectId
from bson.errors import InvalidId

from flask_api.controlador.control_ia_camiseta import (
    generar_camiseta_batch,
    guardar_seleccion,
    generar_pdf_ficha,
    listar_camisetas
)

ruta_ia_camiseta = Blueprint("ruta_ia_camiseta", __name__)

def _validar_objectid(user_id: str):
    try:
        ObjectId(user_id)
        return True
    except (InvalidId, TypeError):
        return False

# Generar N imágenes para elegir
@ruta_ia_camiseta.route("/api/ia/camiseta/generar", methods=["POST"])
def generar():
    data = request.get_json() or {}
    user_id = data.get("userId")
    atributos = data.get("atributos", {})
    batch = int(data.get("batch_size", 4))

    if not user_id or not _validar_objectid(user_id):
        return jsonify({"ok": False, "error": "userId inválido"}), 400

    try:
        result = generar_camiseta_batch(atributos, batch)
        # También devolvemos ficha+costo de referencia (con los atributos elegidos)
        ficha = {
            "Tipo": "camiseta",
            "Estilo": atributos.get("estilo", ""),
            "Color principal": atributos.get("color1", ""),
            "Patrón": atributos.get("patron", "") or "Sin patrón",
            "Color del patrón": atributos.get("colorPatron", "") or "-",
            "Cuello": atributos.get("cuello", ""),
            "Manga": atributos.get("manga", "")
        }
        # costo relativo (mismo que en el controlador)
        from flask_api.controlador.control_ia_camiseta import calcular_costo_camiseta
        costo = calcular_costo_camiseta(atributos)

        return jsonify({
            "ok": True,
            "images": result["images"],   # lista base64
            "prompt": result["prompt"],
            "ficha_tecnica": ficha,
            "costo": costo
        }), 200
    except Exception as e:
        current_app.logger.error(f"❌ Error al generar: {e}")
        return jsonify({"ok": False, "error": str(e)}), 500

# Guardar la que elige el usuario
@ruta_ia_camiseta.route("/api/ia/camiseta/guardar", methods=["POST"])
def guardar():
    data = request.get_json() or {}
    user_id = data.get("userId")
    prompt = data.get("prompt") or ""
    atributos = data.get("atributos", {})
    image_b64 = data.get("image")    # base64 (sin encabezado)

    if not user_id or not _validar_objectid(user_id):
        return jsonify({"ok": False, "error": "userId inválido"}), 400
    if not image_b64:
        return jsonify({"ok": False, "error": "Falta image (base64)"}), 400

    try:
        result = guardar_seleccion(user_id, prompt, atributos, image_b64)
        return jsonify({"ok": True, **result}), 200
    except Exception as e:
        current_app.logger.error(f"❌ Error al guardar: {e}")
        return jsonify({"ok": False, "error": str(e)}), 500

# PDF con ficha técnica
@ruta_ia_camiseta.route("/api/ia/camiseta/ficha_pdf", methods=["POST"])
def ficha_pdf():
    data = request.get_json() or {}
    ficha = data.get("ficha", {})
    imagen_b64 = data.get("imagen")
    image_url = data.get("imageUrl")

    try:
        from flask_api.controlador.control_ia_camiseta import generar_pdf_ficha
        pdf_b64 = generar_pdf_ficha(ficha, imagen_b64, image_url)
        return jsonify({"ok": True, "pdf_base64": pdf_b64}), 200
    except Exception as e:
        current_app.logger.error(f"❌ Error PDF: {e}")
        return jsonify({"ok": False, "error": str(e)}), 500

# Listar camisetas guardadas por usuario
@ruta_ia_camiseta.route("/api/ia/camiseta/listar", methods=["GET"])
def listar():
    user_id = request.args.get("user_id")
    if not user_id or not _validar_objectid(user_id):
        return jsonify({"ok": False, "error": "userId inválido"}), 400
    try:
        docs = listar_camisetas(user_id)
        return jsonify({"ok": True, "camisetas": docs}), 200
    except Exception as e:
        current_app.logger.error(f"❌ Error listando: {e}")
        return jsonify({"ok": False, "error": str(e)}), 500

# Debug STABLE_URL actual
@ruta_ia_camiseta.route("/api/ia/camiseta/check", methods=["GET"])
def check():
    return jsonify({"stable_url": current_app.config.get("STABLE_URL")})

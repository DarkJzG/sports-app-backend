from flask import Blueprint, request, jsonify
from flask_api.controlador.control_ia_texturas_huggingface import generar_textura_hf

ruta_ia_texturas_hf = Blueprint("ruta_ia_texturas_hf", __name__)

@ruta_ia_texturas_hf.route("/api/ia/generar_textura_hf", methods=["POST"])
def generar_textura_hf_route():
    data = request.get_json()
    # Recibes: tipo, colores, direccion, custom, etc. 👇
    tipo = data.get("tipo")  # 'lineas', 'moteado', etc.
    colores = data.get("colores", [])  # ['blue','white']
    direccion = data.get("direccion", None)
    custom = data.get("custom", "")
    zona = data.get("zona", "torso")
    user_id = data.get("userId", "anon")
    # Construir el dict con todos los parámetros posibles
    attr = {
        "tipo": tipo or "moteado",
        "colores": colores,
    }
    if direccion:
        attr["direccion"] = direccion
    if custom:
        attr["custom"] = custom
    # Ahora se pasan todos los parámetros al builder
    result = generar_textura_hf(attr, user_id, zona)
    if "error" in result:
        return jsonify(result), 500
    return jsonify(result), 200

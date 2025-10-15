# flask_api/rutas/ruta_3d_prenda.py
from flask import Blueprint, request, jsonify
from flask_api.controlador.control_3d_prenda import (
    guardar_diseno_prenda_3d,
    listar_disenos_usuario,
    obtener_diseno_detalle,
)
from flask import send_file
from flask_api.controlador.control_ficha_tecnica import generar_ficha_tecnica_3d
from flask_api.controlador.control_3d_prenda import obtener_diseno_detalle
import io
import json

ruta_3d_prenda = Blueprint("ruta_3d_prenda", __name__)

@ruta_3d_prenda.route("/api/3d/prenda/guardar", methods=["POST"])
def guardar_prenda_3d():
    try:
        data = request.form.to_dict()
        for campo in ["colors", "textures", "decals", "textDecals"]:
            if campo in data:
                try:
                    data[campo] = json.loads(data[campo])
                except Exception as e:
                    print(f"⚠️ Error parseando {campo}:", e)
                    data[campo] = {} if campo in ["colors", "textures"] else []
        archivo = request.files.get("file")

        print("🔎 Datos recibidos en guardar_prenda_3d():")
        print(json.dumps({k: str(v)[:100] for k, v in data.items()}, indent=2))

        resultado = guardar_diseno_prenda_3d(data, archivo)
        return jsonify(resultado), 201

    except Exception as e:
        import traceback
        print("❌ Error general en /api/3d/prenda/guardar:")
        traceback.print_exc()  # 🔥 Muestra la traza completa
        return jsonify({"error": str(e)}), 400



@ruta_3d_prenda.route("/api/3d/prenda/listar", methods=["GET"])
def listar_prendas_3d():
    """Lista todos los diseños 3D guardados por un usuario."""
    user_id = request.args.get("user_id")
    try:
        prendas = listar_disenos_usuario(user_id)
        return jsonify({"prendas": prendas}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400


@ruta_3d_prenda.route("/api/3d/prenda/<string:prenda_id>", methods=["GET"])
def obtener_prenda_detalle(prenda_id):
    """Devuelve todos los datos de una prenda 3D"""
    from bson import ObjectId
    from flask import current_app

    try:
        db = current_app.mongo.db
        prenda = db["prendas_3d"].find_one({"_id": ObjectId(prenda_id)})
        if not prenda:
            return jsonify({"error": "Prenda no encontrada"}), 404

        # Convertir ObjectId a string
        prenda["_id"] = str(prenda["_id"])
        if "user_id" in prenda:
            prenda["user_id"] = str(prenda["user_id"])

        return jsonify(prenda), 200

    except Exception as e:
        print("❌ Error al obtener prenda 3D:", e)
        return jsonify({"error": str(e)}), 500


@ruta_3d_prenda.route("/api/3d/prenda/eliminar/<string:prenda_id>", methods=["DELETE"])
def eliminar_prenda_3d(prenda_id):
    """Elimina una prenda 3D guardada por el usuario."""
    from bson import ObjectId
    from flask import current_app

    try:
        db = current_app.mongo.db
        result = db["prendas_3d"].delete_one({"_id": ObjectId(prenda_id)})

        if result.deleted_count == 1:
            return jsonify({"ok": True, "msg": "Prenda eliminada correctamente"}), 200
        else:
            return jsonify({"ok": False, "msg": "Prenda no encontrada"}), 404

    except Exception as e:
        print("❌ Error eliminando prenda 3D:", e)
        return jsonify({"ok": False, "error": str(e)}), 500


@ruta_3d_prenda.route("/ficha/<string:prenda_id>", methods=["GET"])
def ficha_tecnica_3d(prenda_id):
    """
    Genera y devuelve la ficha técnica PDF del diseño 3D.
    """
    try:
        prenda_data = obtener_diseno_detalle(prenda_id)
        if not prenda_data:
            return jsonify({"error": "Prenda no encontrada"}), 404

        pdf_bytes = generar_ficha_tecnica_3d(prenda_data)
        return send_file(
            io.BytesIO(pdf_bytes),
            as_attachment=True,
            download_name=f"FichaTecnica_{prenda_data.get('modelo','prenda')}.pdf",
            mimetype="application/pdf"
        )
    except Exception as e:
        return jsonify({"error": str(e)}), 400
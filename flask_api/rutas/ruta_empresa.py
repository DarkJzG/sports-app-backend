# flask_api/rutas/ruta_empresa.py
import cloudinary.uploader
from flask import Blueprint, request, jsonify, current_app
from flask_api.controlador.control_empresa import (
    obtener_info_empresa,
    actualizar_info_empresa,
    actualizar_imagen_empresa
)


empresa_bp = Blueprint("empresa", __name__, url_prefix="/empresa")


@empresa_bp.route("/", methods=["GET"])
def obtener_empresa_route():
    """
    Obtiene la información de la empresa.
    Ruta pública para que cualquiera pueda ver los datos básicos.
    """
    return obtener_info_empresa()


@empresa_bp.route("/actualizar", methods=["PUT"])
def actualizar_empresa_route():
    """
    Actualiza la información general de la empresa.
    Solo accesible por admin.
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({"ok": False, "msg": "No se enviaron datos"}), 400
        
        return actualizar_info_empresa(data)
        
    except Exception as e:
        current_app.logger.error(f"Error en ruta actualizar empresa: {str(e)}")
        return jsonify({"ok": False, "msg": str(e)}), 500


@empresa_bp.route("/imagen/<campo>", methods=["POST"])
def subir_imagen_route(campo):
    """
    Sube una imagen de la empresa a Cloudinary.
    Campos válidos: logo, banner, favicon, imagenPdf
    """
    try:
        if 'imagen' not in request.files:
            return jsonify({"ok": False, "msg": "No se envió ninguna imagen"}), 400
        
        file = request.files['imagen']
        
        if file.filename == '':
            return jsonify({"ok": False, "msg": "Archivo sin nombre"}), 400
        
        # Validar tipo de archivo
        if not file.content_type.startswith('image/'):
            return jsonify({"ok": False, "msg": "El archivo debe ser una imagen"}), 400
        
        # Definir carpetas según el tipo de imagen
        carpetas = {
            "logo": "empresa/logos",
            "banner": "empresa/banners",
            "favicon": "empresa/favicons",
            "imagenPdf": "empresa/imagenes_pdf"
        }
        
        if campo not in carpetas:
            return jsonify({"ok": False, "msg": "Campo de imagen inválido"}), 400
        
        # Subir a Cloudinary
        upload_result = cloudinary.uploader.upload(
            file,
            folder=carpetas[campo],
            resource_type="image"
        )
        
        imagen_url = upload_result['secure_url']
        current_app.logger.info(f"Imagen {campo} subida a Cloudinary: {imagen_url}")
        
        # Actualizar en la base de datos
        return actualizar_imagen_empresa(campo, imagen_url)
        
    except Exception as e:
        current_app.logger.error(f"Error al subir imagen: {str(e)}")
        return jsonify({"ok": False, "msg": str(e)}), 500

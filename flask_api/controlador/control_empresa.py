# flask_api/controlador/control_empresa.py
from flask import jsonify, current_app
from flask_api.modelo.modelo_empresa import (
    obtener_empresa,
    actualizar_empresa,
    subir_imagen_empresa
)


def obtener_info_empresa():
    """
    Obtiene la información de la empresa.
    """
    try:
        empresa = obtener_empresa()
        
        if not empresa:
            return jsonify({"ok": False, "msg": "No se pudo obtener información de la empresa"}), 500
        
        return jsonify({
            "ok": True,
            "empresa": empresa
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Error al obtener empresa: {str(e)}")
        return jsonify({"ok": False, "msg": str(e)}), 500


def actualizar_info_empresa(data: dict):
    """
    Actualiza la información de la empresa.
    """
    try:
        empresa_actualizada = actualizar_empresa(data)
        
        if not empresa_actualizada:
            return jsonify({"ok": False, "msg": "No se pudo actualizar la información"}), 500
        
        return jsonify({
            "ok": True,
            "msg": "Información actualizada exitosamente",
            "empresa": empresa_actualizada
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Error al actualizar empresa: {str(e)}")
        return jsonify({"ok": False, "msg": str(e)}), 500


def actualizar_imagen_empresa(campo: str, url: str):
    """
    Actualiza una imagen específica de la empresa.
    """
    try:
        empresa_actualizada = subir_imagen_empresa(campo, url)
        
        if not empresa_actualizada:
            return jsonify({"ok": False, "msg": "No se pudo actualizar la imagen"}), 500
        
        return jsonify({
            "ok": True,
            "msg": f"Imagen {campo} actualizada exitosamente",
            "empresa": empresa_actualizada
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Error al actualizar imagen: {str(e)}")
        return jsonify({"ok": False, "msg": str(e)}), 500

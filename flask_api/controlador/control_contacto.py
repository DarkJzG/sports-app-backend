# flask_api/controlador/control_contacto.py
from flask import request, jsonify
from flask_api.funciones.enviar_correo import enviar_correo_contacto

def procesar_contacto():
    data = request.get_json() or {}
    nombre = data.get("nombre", "").strip()
    email = data.get("email", "").strip()
    asunto = data.get("asunto", "").strip()
    mensaje = data.get("mensaje", "").strip()

    if not nombre or not email or not asunto or not mensaje:
        return jsonify({"ok": False, "msg": "Todos los campos son obligatorios"}), 400

    try:
        enviar_correo_contacto(nombre, email, asunto, mensaje)
        return jsonify({"ok": True, "msg": "Mensaje enviado correctamente"})
    except Exception as e:
        print("Error enviando correo de contacto:", e)
        return jsonify({"ok": False, "msg": "Error al enviar el mensaje"}), 500

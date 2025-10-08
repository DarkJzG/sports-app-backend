# routes/logos_3d.py
from flask import Blueprint, request, jsonify, current_app
from bson import ObjectId
from datetime import datetime
import cloudinary.uploader

ruta_3d_logos = Blueprint("ruta_3d_logos", __name__)

def to_object_id(s):
    try:
        return ObjectId(s)
    except Exception:
        return None

@ruta_3d_logos.route("/api/3d/logos/subir", methods=["POST"])
def subir_logo():
    """
    Sube un logo a Cloudinary y guarda metadatos en Mongo.
    Espera multipart/form-data con:
      - file: imagen
      - user_id: id del usuario (string de ObjectId)
    """
    user_id = request.form.get("user_id")
    file = request.files.get("file")

    if not user_id or not file:
        return jsonify({"ok": False, "error": "user_id y file son obligatorios"}), 400

    oid = to_object_id(user_id)
    if not oid:
        return jsonify({"ok": False, "error": "user_id inválido"}), 400

    # Seguridad básica: solo imágenes
    if not file.mimetype or not file.mimetype.startswith("image/"):
        return jsonify({"ok": False, "error": "El archivo debe ser una imagen"}), 400

    folder = f"logos3d/{user_id}"  # organiza por usuario en Cloudinary

    try:
        up = cloudinary.uploader.upload(
            file,
            folder=folder,
            resource_type="image",
            use_filename=True,
            unique_filename=True,
            overwrite=False,
        )
    except Exception as e:
        current_app.logger.exception("Error subiendo a Cloudinary: %s", e)
        return jsonify({"ok": False, "error": "Error al subir a Cloudinary"}), 502

    # Documento Mongo
    doc = {
        "user_id": oid,
        "url": up.get("secure_url"),
        "public_id": up.get("public_id"),
        "format": up.get("format"),
        "bytes": up.get("bytes"),
        "width": up.get("width"),
        "height": up.get("height"),
        "version": up.get("version"),
        "folder": up.get("folder"),
        "created_at": datetime.utcnow(),
    }

    db = current_app.mongo.db
    inserted = db.logos_usuarios.insert_one(doc)
    doc["_id"] = str(inserted.inserted_id)
    doc["user_id"] = str(doc["user_id"])

    return jsonify({"ok": True, "logo": doc}), 201


@ruta_3d_logos.route("/api/3d/logos/listar", methods=["GET"])
def listar_logos():
    """
    Lista logos del usuario autenticado (por query ?user_id=...).
    """
    user_id = request.args.get("user_id")
    oid = to_object_id(user_id) if user_id else None
    if not oid:
        return jsonify({"ok": False, "error": "user_id requerido"}), 400

    db = current_app.mongo.db
    cur = db.logos_usuarios.find({"user_id": oid}).sort("created_at", -1)
    out = []
    for l in cur:
        l["_id"] = str(l["_id"])
        l["user_id"] = str(l["user_id"])
        out.append(l)

    return jsonify({"ok": True, "logos": out})


@ruta_3d_logos.route("/api/3d/logos/eliminar/<logo_id>", methods=["DELETE"])
def eliminar_logo(logo_id):
    """
    Elimina un logo del usuario: borra en Cloudinary y en MongoDB.
    """
    try:
        _id = ObjectId(logo_id)
    except Exception:
        return jsonify({"ok": False, "error": "logo_id inválido"}), 400

    db = current_app.mongo.db
    doc = db.logos_usuarios.find_one({"_id": _id})
    if not doc:
        return jsonify({"ok": False, "error": "No existe"}), 404

    # 🔹 Borrar de Cloudinary si tiene public_id
    public_id = doc.get("public_id")
    try:
        if public_id:
            cloudinary.uploader.destroy(public_id, resource_type="image")
        else:
            # fallback si no tiene public_id registrado
            url = doc.get("url")
            if url:
                # extrae el nombre del archivo sin extensión
                name = url.split("/")[-1].split(".")[0]
                cloudinary.uploader.destroy(f"logos3d/{name}", resource_type="image")
    except Exception as e:
        current_app.logger.warning("⚠️ No se pudo eliminar de Cloudinary: %s", e)

    # 🔹 Borrar registro de MongoDB
    db.logos_usuarios.delete_one({"_id": _id})

    return jsonify({"ok": True, "msg": "Logo eliminado correctamente"}), 200

# flask_api/controlador/control_3d_prenda.py
import io, json, base64
from datetime import datetime
from bson import ObjectId
from werkzeug.utils import secure_filename
from flask import current_app, request
import cloudinary.uploader
from flask_api.modelo.modelo_3d_prenda import guardar_prenda_3d, listar_prendas_3d, obtener_prenda_3d
from flask_api.controlador.control_ficha_tecnica import generar_ficha_tecnica_3d
from flask_api.controlador.generar_plano_sublimacion import subir_plano_sublimacion
import os


def extraer_dataurl_png(data_url):
    """Convierte un dataURL base64 (data:image/png;base64,...) en bytes binarios PNG."""
    if not data_url.startswith("data:image/png;base64,"):
        raise ValueError("Formato de imagen inválido para sublimación")
    return base64.b64decode(data_url.split(",")[1])


def listar_disenos_usuario(user_id):
    return listar_prendas_3d(user_id)


def obtener_diseno_detalle(prenda_id):
    return obtener_prenda_3d(prenda_id)


def guardar_diseno_prenda_3d(data, archivo):
    print("🧾 Datos recibidos:", list(data.keys()))
    print("📦 Archivos recibidos:", list(request.files.keys()))

    renders = {}
    for key in ["render_frente", "render_espalda", "render_lado_izq", "render_lado_der"]:
        file = request.files.get(key)
        if file:
            upload = cloudinary.uploader.upload(
                file,
                folder="disenos3d/renders",
                public_id=f"{data.get('modelo')}_{key}",
                resource_type="image"
            )
            renders[key] = upload["secure_url"]

    data["renders"] = renders


    if not data.get("user_id"):
        raise ValueError("Falta el user_id")

    # ==============================
    # 2️⃣ Limpieza de datos y tipos
    for campo in ["colors", "textures", "decals", "textDecals"]:
        if isinstance(data.get(campo), str):
            try:
                data[campo] = json.loads(data[campo])
            except Exception:
                data[campo] = {} if campo in ["colors", "textures"] else []
    
    # Parsear UV resolution si está presente
    if isinstance(data.get("uv_resolution"), str):
        try:
            data["uv_resolution"] = json.loads(data["uv_resolution"])
        except:
            data["uv_resolution"] = None
            
    if isinstance(data.get("uv_resolution"), list):
        data["uv_resolution"] = [int(x) for x in data["uv_resolution"]]


    # Asegurar que decals tengan solo URLs
    decals = data.get("decals", [])
    for d in decals:
        if not d.get("url"):
            d["url"] = None
        if isinstance(d.get("texture"), (dict, list)):
            d.pop("texture", None)
    data["decals"] = decals

    # ==============================
    # 3️⃣ Guardar diseño en MongoDB
    # ==============================
    prenda_id = guardar_prenda_3d(data)
    data["_id"] = prenda_id
    print(f"✅ Diseño guardado en MongoDB con ID {prenda_id}")

    # ==============================
    # 4️⃣ Generar ficha técnica PDF
    # ==============================
    ficha_url = None
    try:
        pdf_bytes = generar_ficha_tecnica_3d(data)
        pdf_io = io.BytesIO(pdf_bytes)
        upload_pdf = cloudinary.uploader.upload(
            pdf_io,
            folder="fichas3d",
            public_id=secure_filename(data.get("modelo", f"ficha_{prenda_id}")),
            resource_type="raw",
            format="pdf"
        )
        ficha_url = upload_pdf.get("secure_url")
        print(f"📄 Ficha técnica PDF subida: {ficha_url}")
    except Exception as e:
        print("⚠️ Error generando ficha 3D:", e)

    # ==============================
    # 5️⃣ Generar y subir plano de sublimación 2D (desde máscara)
    # ==============================
    db = current_app.mongo.db
    try:
        mask_dir = os.path.join(os.path.dirname(__file__), "..", "static", "prendas3d")
        design_id = data.get("design_id", "base")

        mask_filename = f"mask_{design_id}_rgb.png" if design_id == "base" else f"{design_id}_rgb.png"
        mask_path = os.path.abspath(os.path.join(mask_dir, mask_filename))

        print(f"Buscando máscara en: {mask_path}")

        plano_url = subir_plano_sublimacion(data, mask_path)
        print(f"🧵 Plantilla plana subida: {plano_url}")
        db["prendas_3d"].update_one(
            {"_id": ObjectId(prenda_id)},
            {"$set": {"plano_sublimacion_url": plano_url}}
        )
    except Exception as e:
        print("⚠️ Error generando plano de sublimación:", e)

    # ==============================
    # 6️⃣ Actualizar registro con URL PDF
    # ==============================
    db["prendas_3d"].update_one(
        {"_id": ObjectId(prenda_id)},
        {"$set": {
            "ficha_pdf_url": ficha_url,
            "fecha_actualizacion": datetime.utcnow()
        }}
    )

    return {
        "ok": True,
        "mensaje": "Diseño 3D guardado correctamente",
        "id": str(prenda_id),
        "ficha_pdf_url": ficha_url
    }

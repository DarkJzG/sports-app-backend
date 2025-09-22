# flask_api/controlador/control_ia_texturas.py
import base64, io, requests
import cloudinary.uploader
from bson import ObjectId
from flask import current_app
from flask_api.modelo.modelo_ia_texturas import guardar_textura

STABLE_URL = "http://127.0.0.1:7860"
NEGATIVE_PROMPT = "person, human, logo, text, letters, watermark"

# flask_api/controlador/control_ia_texturas.py

def generar_textura(prompt_textura: str, user_id: str, side: str):
    payload = {
        "prompt": prompt_textura,
        "negative_prompt": NEGATIVE_PROMPT,
        "steps": 26,
        "width": 512,
        "height": 512,
    }

    try:
        response = requests.post(f"{STABLE_URL}/sdapi/v1/txt2img", json=payload, timeout=120)
        response.raise_for_status()
        r = response.json()
        image_base64 = r["images"][0]
    except Exception as e:
        print("❌ Error Stable Diffusion:", e)
        return {"error": f"Error al generar textura en Stable Diffusion: {str(e)}"}

    try:
        # Subir a Cloudinary
        image_data = base64.b64decode(image_base64)
        image_file = io.BytesIO(image_data)
        upload_result = cloudinary.uploader.upload(image_file, folder="texturasIA")
        image_url = upload_result.get("secure_url")
    except Exception as e:
        print("❌ Error Cloudinary:", e)
        return {"error": f"Error subiendo a Cloudinary: {str(e)}"}

    if not image_url:
        return {"error": "No se obtuvo URL de Cloudinary"}

    # Guardar en Mongo
    try:
        doc = {
            "user_id": ObjectId(user_id) if user_id != "anon" else None,
            "side": side,
            "prompt": prompt_textura,
            "imageUrl": image_url,
            "estado": "generado",
        }
        inserted_id = guardar_textura(doc)
    except Exception as e:
        print("❌ Error guardando en Mongo:", e)
        return {"error": f"Error guardando en Mongo: {str(e)}"}

    return {
        "id": inserted_id,
        "side": side,
        "user_id": user_id,
        "imageUrl": image_url,
        "prompt": prompt_textura
    }

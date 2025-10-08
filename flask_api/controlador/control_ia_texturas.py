# flask_api/controlador/control_ia_texturas.py
import base64, io, requests, os
import cloudinary.uploader
from bson import ObjectId
from flask import current_app
from flask_api.modelo.modelo_ia_texturas import guardar_textura
from PIL import Image
import numpy as np

# 🔹 Leer URL desde .env
STABLE_URL = os.getenv("STABLE_URL", "http://127.0.0.1:7860").strip()
NEGATIVE_PROMPT = "person, human, logo, text, letters, watermark"

def extraer_color_promedio(image_bytes: bytes) -> str:
    
    try:
        img = Image.open(io.BytesIO(image_bytes)).convert("RGB")
        img = img.resize((64, 64))  # optimiza cálculo
        arr = np.array(img)
        r, g, b = np.mean(arr[:, :, 0]), np.mean(arr[:, :, 1]), np.mean(arr[:, :, 2])
        return "#{:02x}{:02x}{:02x}".format(int(r), int(g), int(b))
    except Exception as e:
        print("⚠️ Error al calcular color promedio:", e)
        return "#FFFFFF"

def generar_textura(prompt_textura: str, user_id: str, zona: str):
    
    payload = {
       "prompt": prompt_textura,
        "negative_prompt": NEGATIVE_PROMPT,
        "steps": 30,
        "sampler_name": "DPM++ 2M",
        "cfg_scale": 7.5,
        "width": 1024,
        "height": 1024
    }

    try:
        response = requests.post(f"{STABLE_URL}/sdapi/v1/txt2img", json=payload, timeout=120)
        response.raise_for_status()
        data = response.json()
        image_base64 = data["images"][0]
    except Exception as e:
        print("❌ Error Stable Diffusion:", e)
        return {"error": f"Error al generar textura en Stable Diffusion: {str(e)}"}

    # 🔹 Decodificar imagen
    try:
        image_bytes = base64.b64decode(image_base64)
    except Exception as e:
        print("❌ Error al decodificar base64:", e)
        return {"error": "Error al decodificar la imagen generada"}

    # 🟢 Extraer color promedio
    dominant_color = extraer_color_promedio(image_bytes)

    # 🔹 Subir a Cloudinary
    try:
        image_file = io.BytesIO(image_bytes)
        upload_result = cloudinary.uploader.upload(image_file, folder="texturasIA")
        image_url = upload_result.get("secure_url")
    except Exception as e:
        print("❌ Error Cloudinary:", e)
        return {"error": f"Error subiendo a Cloudinary: {str(e)}"}

    if not image_url:
        return {"error": "No se obtuvo URL de Cloudinary"}

    # 🔹 Guardar en MongoDB
    try:
        doc = {
            "user_id": ObjectId(user_id) if user_id != "anon" else None,
            "zona": zona,
            "prompt": prompt_textura,
            "imageUrl": image_url,
            "color_promedio": dominant_color,
            "estado": "generado",
        }
        inserted_id = guardar_textura(doc)
    except Exception as e:
        print("❌ Error guardando en Mongo:", e)
        return {"error": f"Error guardando en Mongo: {str(e)}"}

    return {
        "id": inserted_id,
        "zona": zona,
        "user_id": user_id,
        "imageUrl": image_url,
        "prompt": prompt_textura,
        "color_promedio": dominant_color,
    }

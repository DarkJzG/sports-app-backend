import io, os, cloudinary.uploader
from bson import ObjectId
from flask import current_app
from flask_api.modelo.modelo_ia_texturas import guardar_textura
from PIL import Image
import numpy as np
from huggingface_hub import InferenceClient
from flask_api.controlador.prompts_texturas import build_prompt_textura

NEGATIVE_PROMPT = "person, human, logo, text, letters, watermark"

def extraer_color_promedio(image_bytes: bytes) -> str:
    try:
        img = Image.open(io.BytesIO(image_bytes)).convert("RGB")
        img = img.resize((64, 64))
        arr = np.array(img)
        r, g, b = np.mean(arr[:, :, 0]), np.mean(arr[:, :, 1]), np.mean(arr[:, :, 2])
        return "#{:02x}{:02x}{:02x}".format(int(r), int(g), int(b))
    except Exception as e:
        print("ya nError al calcular color promedio:", e)
        return "#FFFFFF"

def generar_textura_hf(attr: dict, user_id: str, zona: str):
    hf_token = os.environ.get("HF_TOKEN") or current_app.config.get("HF_TOKEN")
    client = InferenceClient(provider="auto", api_key=hf_token)
    model_name = "black-forest-labs/FLUX.1-schnell"

    prompt_textura = build_prompt_textura(attr)
    try:
        image = client.text_to_image(
            prompt_textura,
            model=model_name,
        )
        print("✅ Imagen generada con HF")
    except Exception as e:
        print("❌ Error Hugging Face:", e)
        return {"error": f"Error al generar textura con HF: {str(e)}"}

    try:
        image_bytes = io.BytesIO()
        image.save(image_bytes, format='PNG')
        image_bytes.seek(0)
        image_data = image_bytes.getvalue()
    except Exception as e:
        print("❌ Error al convertir imagen a bytes:", e)
        return {"error": "Error al convertir la imagen generada"}

    dominant_color = extraer_color_promedio(image_data)
    try:
        image_file = io.BytesIO(image_data)
        upload_result = cloudinary.uploader.upload(image_file, folder="texturasIA")
        image_url = upload_result.get("secure_url")
    except Exception as e:
        print("❌ Error Cloudinary:", e)
        return {"error": f"Error subiendo a Cloudinary: {str(e)}"}
    if not image_url:
        return {"error": "No se obtuvo URL de Cloudinary"}

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

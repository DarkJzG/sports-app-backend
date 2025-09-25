import os
import base64
import requests
import cloudinary.uploader
from flask import jsonify, current_app
from flask_api.modelo.modelo_camiseta_ia import guardar_camiseta

NEGATIVO = (
    "cuerpo, humano, hombre, mujer, maniquí, brazos, manos, dedos, caras, modelo, extremidades, texto, logotipos"
)

def construir_prompt_es(atributos: dict) -> str:
    estilo = atributos.get("estilo", "deportiva")
    color1 = atributos.get("color1", "negra")
    patron = atributos.get("patron", "")
    color_patron = atributos.get("colorPatron", "")
    cuello = atributos.get("cuello", "")
    manga = atributos.get("manga", "")


    partes = [
        f"Vista frontal centrada, maqueta de alta calidad de una camiseta {estilo} de color {color1}"
    ]

    if patron and color_patron:
        partes.append(f"con patrón de {patron.lower()} en color {color_patron}")
    if cuello:
        partes.append(f"con cuello {cuello.lower()}")
    if manga:
        partes.append(f"con mangas {manga.lower()}")


    partes.extend([
        "iluminación de estudio",
        "fondo blanco liso",
        "enfoque nítido",
        "sin texto",
        "sin logotipos",
        "solo la camiseta"
    ])

    return ", ".join(partes)


def generar_camiseta_ia(atributos: dict, user_id: str):
    prompt = construir_prompt_es(atributos)

    payload = {
        "prompt": prompt,
        "negative_prompt": NEGATIVO,
        "steps": 28,
        "sampler_name": "DPM++ 2M Karras",
        "width": 512,
        "height": 512,
        "cfg_scale": 7,
        "batch_size": 4   
    }

    try:
        stable_url = os.getenv("STABLE_URL")
        endpoint = f"{stable_url}/sdapi/v1/txt2img"
        current_app.logger.info(f"📡 Enviando prompt a {endpoint}: {prompt}")

        r = requests.post(endpoint, json=payload, timeout=120)
        r.raise_for_status()
        result = r.json()

        if "images" not in result or not result["images"]:
            return {"ok": False, "msg": "No se generaron imágenes"}

        # Devuelvo todas las imágenes en base64
        return {
            "ok": True,
            "images": result["images"],
            "prompt": prompt,
            "userId": user_id
        }

    except Exception as e:
        current_app.logger.error(f"❌ Error al generar camiseta: {e}")
        return {"ok": False, "msg": str(e)}


def guardar_camiseta_seleccionada(user_id: str, prompt: str, image_base64: str, atributos: dict):
    """Guarda en Cloudinary y Mongo la camiseta elegida"""
    try:
        upload_result = cloudinary.uploader.upload(
            f"data:image/png;base64,{image_base64}",
            folder="camisetasIA"
        )
        url = upload_result["secure_url"]

        doc = {
            "user_id": user_id,
            "prompt": prompt,
            "imageUrl": url,
            "atributos": atributos   # 👈 guardamos como dict
        }
        camis_id = guardar_camiseta(doc)

        return {"ok": True, "id": camis_id, "url": url}
    except Exception as e:
        return {"ok": False, "msg": str(e)}


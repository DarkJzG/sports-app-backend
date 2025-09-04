# flask_api/rutas/ruta_ai_stabledf.py
import base64, io, time
from PIL import Image
from flask import Blueprint, current_app, request, jsonify
import requests

ruta_stable = Blueprint("ruta_stable", __name__)

# Prompt básico con alta calidad
def build_prompt_stable(data: dict):
    categoria = data.get("categoria", "camiseta")
    estilo = data.get("estilo", "deportivo")
    tela = data.get("tela", "poliéster")
    color_principal = data.get("color_principal", "blanco")
    color_secundario = data.get("color_secundario", "ninguno")
    patron = data.get("patron", "liso")
    
    prompt = (
        f"High-quality, photorealistic front view of a {estilo} {categoria}, "
        f"made of {tela}, primary color {color_principal}, "
        f"{'with secondary color ' + color_secundario if color_secundario != 'ninguno' else ''}, "
        f"pattern: {patron}, studio lighting, plain white background, realistic fabric texture, sharp focus, "
        "no humans, no logos, only the garment."
    )
    negative = "text, watermark, human, mannequin, logo, blurry, deformed"
    
    return prompt, negative

# Endpoint Health
@ruta_stable.route("/api/stable/health", methods=["GET"])
def stable_health():
    return jsonify({"ok": True, "msg": "Ruta Stable Diffusion activa"})

# Generación de imágenes
@ruta_stable.route("/api/stable/generar", methods=["POST"])
def generar_stable():
    data = request.get_json(force=True) or {}
    prompt, negative = build_prompt_stable(data)
    
    num_imgs = int(data.get("num_imgs", 3))
    width = int(data.get("width", 768))
    height = int(data.get("height", 768))
    steps = int(data.get("steps", 28))
    cfg_s = float(data.get("guidance_scale", 7.5))
    
    # Aquí usamos un backend SD local o API
    SD_API_URL = current_app.config.get("STABLE_API_URL", "http://127.0.0.1:7860/sdapi/v1/txt2img")
    
    payload = {
        "prompt": prompt,
        "negative_prompt": negative,
        "width": width,
        "height": height,
        "sampler_name": "Euler a",
        "steps": steps,
        "cfg_scale": cfg_s,
        "n_iter": 1,
        "batch_size": num_imgs
    }
    
    try:
        res = requests.post(SD_API_URL, json=payload, timeout=120)
        res.raise_for_status()
        json_resp = res.json()
        
        images_b64 = []
        for im_str in json_resp.get("images", []):
            images_b64.append(f"data:image/png;base64,{im_str}")
        
        return jsonify({
            "ok": True,
            "images_base64": images_b64,
            "meta": {
                "descripcion": prompt,
                "width": width,
                "height": height
            }
        })
        
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 500

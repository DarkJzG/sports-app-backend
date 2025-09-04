# flask_api/rutas/ruta_ia.py
import base64
import io
import time
import requests
from PIL import Image
from flask import Blueprint, current_app, request, jsonify

ruta_ia = Blueprint("ruta_ia", __name__)

def build_prompt(data: dict):
    tipo   = data.get("tipo", "sports jersey")
    color  = data.get("color", "purple and black")
    cuello = data.get("cuello", "crew neck")
    mangas = data.get("mangas", "short sleeves")
    tela   = data.get("tela", "polyester performance fabric")
    patron = data.get("patron", "subtle stripes")

    prompt = (
        f"{tipo} for professional athletes, {color}, {cuello}, {mangas}, "
        f"{tela}, {patron}, studio lighting, highly detailed, product photography, "
        f"clean background, realistic textures, 8k, sharp focus "
        f"(rendered using custom LoRA fine-tuned on sportswear)"
    )
    negative = "lowres, blurry, deformed, watermark, text, logos, extra limbs, bad proportions"
    return prompt, negative

@ruta_ia.route("/api/ia/health", methods=["GET"])
def ia_health():
    from flask import current_app, jsonify
    return jsonify({
        "replicate_token_loaded": bool(current_app.config.get("REPLICATE_API_TOKEN")),
        "replicate_model": current_app.config.get("REPLICATE_MODEL"),
        "replicate_version": current_app.config.get("REPLICATE_VERSION"),
    })

@ruta_ia.route("/api/ia/generar", methods=["POST"])
def generar_imagen():
    cfg = current_app.config
    token   = cfg.get("REPLICATE_API_TOKEN")
    model   = cfg.get("REPLICATE_MODEL", "stability-ai/sdxl")
    version = cfg.get("REPLICATE_VERSION")  # <--- lee la versión

    if not token:
        return jsonify({"ok": False, "error": "Falta REPLICATE_API_TOKEN en el servidor"}), 500

    data   = request.get_json(force=True) or {}
    width  = int(data.get("width", 768))
    height = int(data.get("height", 768))
    steps  = int(data.get("steps", 30))
    scale  = float(data.get("guidance_scale", 7.5))

    prompt, negative = build_prompt(data)

    create_url = "https://api.replicate.com/v1/predictions"
    headers = {"Authorization": f"Token {token}", "Content-Type": "application/json"}

    # ⚠️ Preferir "version". Si no la tienes, caemos a "model".
    if version:
        payload = {
            "version": version,
            "input": {
                "prompt": prompt,
                "negative_prompt": negative,
                "width": width,
                "height": height,
                "num_inference_steps": steps,
                "guidance_scale": scale
            }
        }
    else:
        payload = {
            "model": model,
            "input": {
                "prompt": prompt,
                "negative_prompt": negative,
                "width": width,
                "height": height,
                "num_inference_steps": steps,
                "guidance_scale": scale
            }
        }

    cr = requests.post(create_url, json=payload, headers=headers, timeout=180)

    # Log útil para diagnosticar si algo va mal
    current_app.logger.info("Replicate create status=%s body=%s", cr.status_code, cr.text[:500])

    if cr.status_code >= 300:
        try:
            return jsonify({"ok": False, "error": cr.json()}), cr.status_code
        except Exception:
            return jsonify({"ok": False, "error": cr.text}), 500

    pj = cr.json()
    get_url = pj.get("urls", {}).get("get")
    if not get_url:
        return jsonify({"ok": False, "error": "Respuesta inesperada de Replicate"}), 500

    # Polling
    for _ in range(60):
        gr = requests.get(get_url, headers=headers, timeout=60)
        gj = gr.json()
        status = gj.get("status")
        if status == "succeeded":
            output = gj.get("output")
            img_url = output[0] if isinstance(output, list) else output
            ir = requests.get(img_url, timeout=120)
            img = Image.open(io.BytesIO(ir.content)).convert("RGB")
            buf = io.BytesIO(); img.save(buf, format="JPEG", quality=95)
            b64 = base64.b64encode(buf.getvalue()).decode("utf-8")
            return jsonify({
                "ok": True,
                "image_base64": b64,
                "meta": {"width": width, "height": height, "provider": "Replicate SDXL"},
                "pseudo_engine": "LoRA-SD2.1 (cortina)"
            })
        if status in ("failed", "canceled"):
            return jsonify({"ok": False, "error": gj}), 500
        time.sleep(2)

    return jsonify({"ok": False, "error": "Tiempo de espera agotado"}), 504

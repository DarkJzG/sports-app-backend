# flask_api/rutas/ruta_ia.py
import base64, io, time, requests
from PIL import Image
from flask import Blueprint, current_app, request, jsonify

ruta_ia = Blueprint("ruta_ia", __name__)

NEG_HUMANS = (
    "person, people, human, man, woman, model, mannequin, dummy, "
    "torso, body, head, face, skin, neck, shoulder, arm, hand, fingers, legs, "
    "full body, portrait, fashion shoot, text, watermark, logo, brand name, letters, words, blurry, lowres, extra objects, "
    "text, logo, brand, signature, emblem"
)

# -------------------------------
# Prompt básico (ya existente)
# -------------------------------
def build_prompt(data: dict):
    tipo   = data.get("tipo", "sports t-shirt")
    color  = data.get("color", "white base with purple geometric accents")
    cuello = data.get("cuello", "v-neck purple trim")
    mangas = data.get("mangas", "short sleeves with purple cuffs")
    tela   = data.get("tela", "polyester athletic fabric")
    patron = data.get("patron", "diagonal strokes and splatter")

    prompt = (
        f"front view centered high-quality apparel packshot of a {tipo} only, "
        f"{color}, {cuello}, {mangas}, {tela}, {patron}, "
        "realistic fabric texture, soft studio lighting, "
        "plain white seamless background, soft ground shadow, sharp focus, only the shirt"
    )
    negative = "text, watermark, brand name, logo text, lowres, blurry, artifacts, deformed"
    return prompt, negative

# -------------------------------
# Prompt mejorado desde formulario en español
# -------------------------------
def build_prompt_from_user(data: dict):
    categoria = data.get("categoria", "camiseta")
    estilo = data.get("estilo", "deportivo")
    tela = data.get("tela", "poliéster")
    color_principal = data.get("color_principal", "blanco")
    color_secundario = data.get("color_secundario", "ninguno")
    color_terciario = data.get("color_terciario", "ninguno")
    mangas = data.get("mangas", "cortas")
    cuello = data.get("cuello", "redondo")
    patron = data.get("patron", "ninguno")
    talla = data.get("talla", "M")
    genero = data.get("genero", "unisex")

    # ✅ Descripción en español para mostrar al usuario
    descripcion = (
        f"{categoria.capitalize()} {estilo} de {tela}, "
        f"color principal {color_principal}"
        f"{', con detalles en ' + color_secundario if color_secundario != 'ninguno' else ''}"
        f"{', y acentos en ' + color_terciario if color_terciario != 'ninguno' else ''}, "
        f"mangas {mangas}, cuello {cuello}, "
        f"patrón {patron if patron != 'ninguno' else 'liso'}, "
        f"talla {talla}, {genero}."
    )

    # ✅ Prompt en inglés para IA (más estructurado)
    prompt = (
        f"Front view, centered, high-quality mockup of a {estilo} {categoria}, "
        f"made of {tela}, primary color {color_principal}, "
        f"{'secondary color ' + color_secundario + ', ' if color_secundario != 'ninguno' else ''}"
        f"{'tertiary accents ' + color_terciario + ', ' if color_terciario != 'ninguno' else ''}"
        f"{mangas} sleeves, {cuello} neck, "
        f"{'pattern of ' + patron if patron != 'ninguno' else 'plain design'}, "
        f"studio lighting, plain white seamless background, sharp focus, no text, no logos, "
        "only the garment."
    )

    negative = "text, watermark, human, mannequin, logo text, blurry, deformed, extra arms, faces"

    return prompt, negative, descripcion

# -------------------------------
# Utilidades
# -------------------------------
def _download_to_b64_from_url(url: str) -> str:
    r = requests.get(url, timeout=120)
    img = Image.open(io.BytesIO(r.content)).convert("RGB")
    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=95)
    return base64.b64encode(buf.getvalue()).decode("utf-8")

# -------------------------------
# Endpoints
# -------------------------------
@ruta_ia.route("/api/ia/health", methods=["GET"])
def ia_health():
    return jsonify({
        "horde_key_loaded": bool(current_app.config.get("HORDE_API_KEY")),
        "horde_base_url": current_app.config.get("HORDE_BASE_URL"),
    })

# 🚀 Ruta original (NO LA TOCAMOS)
@ruta_ia.route("/api/ia/generar", methods=["POST"])
def generar_imagen():
    return _generar_core(request.get_json(force=True) or {}, use_v2=False)

# 🚀 Nueva ruta con build_prompt_from_user
@ruta_ia.route("/api/ia/generar_v2", methods=["POST"])
def generar_imagen_v2():
    return _generar_core(request.get_json(force=True) or {}, use_v2=True)

# -------------------------------
# Core reutilizable
# -------------------------------
def _generar_core(data: dict, use_v2: bool = False):
    cfg = current_app.config
    api_key = cfg.get("HORDE_API_KEY")
    base    = cfg.get("HORDE_BASE_URL", "https://aihorde.net/api").rstrip("/")
    if not base.endswith("/api"):
        base = base

    width  = int(data.get("width", 768))
    height = int(data.get("height", 768))
    steps  = int(data.get("steps", 28))
    cfg_s  = float(data.get("guidance_scale", 7.5))

    # Prompt builder
    if use_v2:
        prompt, negative, descripcion = build_prompt_from_user(data)
    else:
        prompt, negative = build_prompt(data)
        descripcion = ""

    negative = (negative + ", " + NEG_HUMANS).strip(", ")

    payload = {
        "prompt": prompt,
        "params": {
            "width": width,
            "height": height,
            "steps": steps,
            "cfg_scale": cfg_s,
            "sampler_name": "k_euler",
            "n": 1,
            "negative_prompt": negative
        },
        "nsfw": False,
        "censor_nsfw": True,
        "models": ["SDXL 1.0"]
    }

    submit_url = f"{base}/v2/generate/async"
    headers = {"apikey": api_key, "Content-Type": "application/json"}

    sr = requests.post(submit_url, json=payload, headers=headers, timeout=45)
    if sr.status_code not in (200, 202):
        return jsonify({"ok": False, "error": {"status": sr.status_code, "detail": sr.text[:600]}}), sr.status_code

    job = sr.json()
    job_id = job.get("id")
    if not job_id:
        return jsonify({"ok": False, "error": "Respuesta inesperada de Horde (sin id)"}), 500

    status_url = f"{base}/v2/generate/status/{job_id}"
    t0 = time.time()
    while time.time() - t0 < 180:
        st = requests.get(status_url, headers={"apikey": api_key}, timeout=45)
        if st.status_code >= 300:
            return jsonify({"ok": False, "error": {"status": st.status_code, "detail": st.text[:600]}}), st.status_code
        sj = st.json()
        if sj.get("done"):
            gens = sj.get("generations", [])
            if not gens:
                return jsonify({"ok": False, "error": "Horde terminó pero sin imágenes"}), 500

            img_field = gens[0].get("img", "")
            if img_field.startswith("http"):
                b64 = _download_to_b64_from_url(img_field)
            else:
                raw = base64.b64decode(img_field)
                img = Image.open(io.BytesIO(raw)).convert("RGB")
                buf = io.BytesIO()
                img.save(buf, format="JPEG", quality=95)
                b64 = base64.b64encode(buf.getvalue()).decode("utf-8")

            return jsonify({
                "ok": True,
                "image_base64": b64,
                "meta": {
                    "width": width,
                    "height": height,
                    "provider": "AI Horde",
                    "descripcion": descripcion
                }
            })
        time.sleep(3)

    return jsonify({"ok": False, "error": "Tiempo de espera agotado en Horde"}), 504

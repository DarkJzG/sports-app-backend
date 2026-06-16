# flask_api/controlador/control_camiseta_ia_v3.py
import base64, io, requests, cloudinary.uploader
from flask import current_app
from googletrans import Translator
from bson import ObjectId

from flask_api.modelo.modelo_ia_prendas import guardar_prenda
from flask_api.controlador.prompts import build_prompt_v3, descripcion_es_v3

NEGATIVE_PROMPT = (
    "people, human, mannequin, arms, hands, fingers, faces, background, text, watermark, blurry"
)

translator = Translator()



# Traducción de atributos
def traducir_texto(texto: str) -> str:
    try:
        if not texto:
            return ""
        return translator.translate(texto, src="es", dest="en").text
    except Exception:
        return texto


def traducir_atributos(atributos: dict) -> dict:
    traducidos = {}
    for k, v in atributos.items():
        if k == "cuello" and isinstance(v, str):
            # Si el cuello es "Polo", no traducir
            if v.strip().lower() == "polo":
                traducidos[k] = "Polo"
            else:
                traducidos[k] = traducir_texto(v)
        elif isinstance(v, str):
            traducidos[k] = traducir_texto(v)
        elif isinstance(v, list):
            traducidos[k] = [
                traducir_texto(item) if isinstance(item, str) else item
                for item in v
            ]
        else:
            traducidos[k] = v
    return traducidos

# ===============================
# 💰 Cálculo simple de costo
# ===============================
def calcular_costo_produccion(atributos: dict) -> dict:
    if atributos.get("tela") == "Algodón":
        costo_material = 3
    elif atributos.get("tela") == "Poliéster":
        costo_material = 2
    else:
        costo_material = 2.5

    costo_mano_obra = 0.7
    costo_insumos = 0.8
    costo_diseno = 1.5

    total = round(costo_material + costo_mano_obra + costo_insumos + costo_diseno, 2)
    precio_venta = round(total * 1.5, 2)
    precio_mayor = round(total * 1.2, 2)

    return {
        "material": costo_material,
        "mano_obra": costo_mano_obra,
        "insumos": costo_insumos,
        "diseno": costo_diseno,
        "total": total,
        "precio_venta": precio_venta,
        "precio_mayor": precio_mayor,
    }



# ===============================
# 🧠 Generador IA principal
# ===============================
def generar_camiseta_v3(categoria_id, atributos_es, user_id):
    """
    Genera la imagen IA y guarda la prenda base (sin ficha técnica ni PDF).
    Los datos llegan en español → se traducen al inglés → se genera prompt inglés.
    """
    STABLE_URL = current_app.config.get("STABLE_URL", "http://127.0.0.1:7860")

    print("\n==============================")
    print("🚀 INICIO generar_camiseta_v3")
    print("==============================")

    # 1️⃣ Datos recibidos
    print("📥 Atributos recibidos (ES):", atributos_es)

    # 2️⃣ Traducción al inglés
    atributos_en = traducir_atributos(atributos_es)
    print("\n🌐 Atributos traducidos (EN):", atributos_en)

    # 3️⃣ Construcción de prompt y descripción
    print("\n🧩 Entrando a build_prompt_v3 con:", atributos_en)
    prompt_en = build_prompt_v3(atributos_en)
    print("🟣 Prompt generado:\n", prompt_en, "\n")

    descripcion_es = descripcion_es_v3(atributos_es)
    print("🟢 Descripción generada (ES):", descripcion_es)

    # 4️⃣ Generar imagen IA
    payload = {
        "prompt": prompt_en,
        "negative_prompt": NEGATIVE_PROMPT,
        "width": 512,
        "height": 512,
        "sampler_name": "DPM++ 2M",
        "steps": 30,
        "cfg_scale": 7,
        "seed": -1,
    }

    try:
        print("\n📡 Enviando solicitud a Stable Diffusion...")
        response = requests.post(f"{STABLE_URL}/sdapi/v1/txt2img", json=payload)
        response.raise_for_status()
        data = response.json()
        img_base64 = data["images"][0]
        print("✅ Imagen IA generada correctamente")
    except Exception as e:
        print("❌ Error al generar la imagen:", e)
        print("❌ Prompt generado (error):", prompt_en)
        raise

    # 5️⃣ Subir a Cloudinary
    print("\n☁️ Subiendo imagen a Cloudinary...")
    image_bytes = io.BytesIO(base64.b64decode(img_base64))
    cloud = cloudinary.uploader.upload(image_bytes, folder="Camiseta_V3")
    image_url = cloud.get("secure_url")
    print("✅ Imagen subida:", image_url)

    # 6️⃣ Calcular costo
    costo = calcular_costo_produccion(atributos_es)
    print("\n💰 Costo de producción calculado:", costo)

    # 7️⃣ Asociar usuario
    try:
        user_obj_id = ObjectId(user_id) if user_id else None
    except Exception:
        user_obj_id = None

    # 8️⃣ Documento a guardar
    doc = {
        "user_id": user_obj_id,
        "categoria_prd": categoria_id,
        "descripcion": descripcion_es,
        "atributos_es": atributos_es,
        "atributos_en": atributos_en,
        "prompt_en": prompt_en,
        "imageUrl": image_url,
        "costo": costo,
        "estado": "generado",
    }

    print("\n🗂️ Documento a guardar en MongoDB:")
    for k, v in doc.items():
        print(f"   - {k}: {v if not isinstance(v, dict) else '[dict con datos]'}")

    guardar_prenda(doc)

    print("\n✅ Prenda guardada exitosamente")
    print("==============================\n")

    return {
        "imageUrl": image_url,
        "prompt": prompt_en,
        "descripcion": descripcion_es,
        "costo": costo,
    }

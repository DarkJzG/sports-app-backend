# flask_api/controlador/control_pantalon_ia_v1.py
import base64, io, requests, cloudinary.uploader
from flask import current_app
from googletrans import Translator
from bson import ObjectId

from flask_api.modelo.modelo_ia_prendas import guardar_prenda
from flask_api.controlador.prompts_pantalon import build_prompt_pantalon_v1, descripcion_pantalon_es_v1

NEGATIVE_PROMPT = (
    "people, human, mannequin, legs, feet, torso, arms, faces, background, text, watermark, blurry, "
    "deformed, distorted, low quality, wrinkled fabric"
)

translator = Translator()


def traducir_texto(texto: str) -> str:
    """Traduce un texto de español a inglés"""
    try:
        if not texto:
            return ""
        return translator.translate(texto, src="es", dest="en").text
    except Exception:
        return texto


def traducir_atributos(atributos: dict) -> dict:
    """Traduce todos los atributos de español a inglés"""
    traducidos = {}
    for k, v in atributos.items():
        if isinstance(v, str):
            traducidos[k] = traducir_texto(v)
        elif isinstance(v, list):
            traducidos[k] = [
                traducir_texto(item) if isinstance(item, str) else item
                for item in v
            ]
        else:
            traducidos[k] = v
    return traducidos


def calcular_costo_produccion_pantalon(atributos: dict) -> dict:
    """Calcula el costo de producción de un pantalón"""
    # Costo base según la tela
    if atributos.get("tela") == "Algodón":
        costo_material = 4.5
    elif atributos.get("tela") == "Poliéster":
        costo_material = 3.5
    elif atributos.get("tela") == "Fleece":
        costo_material = 5.5
    else:
        costo_material = 4.0
    
    # Ajuste por tipo de corte
    if atributos.get("tipoCorte") == "jogger":
        costo_material += 0.5  # El rib en tobillo aumenta el costo
    
    # Ajuste por bolsillos con zipper
    if atributos.get("bolsillos") == "laterales_zip":
        costo_material += 0.8
    
    # Ajuste por complejidad del diseño
    camino = atributos.get("caminoSeleccionado", "solido")
    if camino == "paneles":
        costo_diseno = 1.8  # Costura de paneles
    elif camino == "sublimacion":
        area = atributos.get("areaDisenoIA", "completo")
        if area == "completo":
            costo_diseno = 3.5  # Sublimación completa
        else:
            costo_diseno = 2.5  # Sublimación parcial
    else:
        costo_diseno = 1.2  # Diseño simple
    
    costo_mano_obra = 1.2
    costo_insumos = 1.0
    
    total = round(costo_material + costo_mano_obra + costo_insumos + costo_diseno, 2)
    precio_venta = round(total * 1.55, 2)  # Margen del 55%
    precio_mayor = round(total * 1.25, 2)  # Margen del 25%
    
    return {
        "material": costo_material,
        "mano_obra": costo_mano_obra,
        "insumos": costo_insumos,
        "diseno": costo_diseno,
        "total": total,
        "precio_venta": precio_venta,
        "precio_mayor": precio_mayor,
    }


def generar_pantalon_v1(categoria_id, atributos_es, user_id):
    """
    Genera la imagen IA de un pantalón y guarda la prenda en la base de datos.
    """
    STABLE_URL = current_app.config.get("STABLE_URL", "http://127.0.0.1:7860")
    
    print("\n==============================")
    print("👖 INICIO generar_pantalon_v1")
    print("==============================")
    
    # 1️⃣ Datos recibidos
    print("📥 Atributos recibidos (ES):", atributos_es)
    
    # 2️⃣ Traducción al inglés
    atributos_en = traducir_atributos(atributos_es)
    print("\n🌐 Atributos traducidos (EN):", atributos_en)
    
    # 3️⃣ Construcción de prompt y descripción
    print("\n🧩 Entrando a build_prompt_pantalon_v1 con:", atributos_en)
    prompt_en = build_prompt_pantalon_v1(atributos_en)
    print("🟣 Prompt generado:\n", prompt_en, "\n")
    
    descripcion_es = descripcion_pantalon_es_v1(atributos_es)
    print("🟢 Descripción generada (ES):", descripcion_es)
    
    # 4️⃣ Generar imagen IA
    payload = {
        "prompt": prompt_en,
        "negative_prompt": NEGATIVE_PROMPT,
        "width": 512,
        "height": 768,  # Formato más alto para pantalones
        "sampler_name": "DPM++ 2M",
        "steps": 35,
        "cfg_scale": 7.5,
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
    cloud = cloudinary.uploader.upload(image_bytes, folder="Pantalon_V1")
    image_url = cloud.get("secure_url")
    print("✅ Imagen subida:", image_url)
    
    # 6️⃣ Calcular costo
    costo = calcular_costo_produccion_pantalon(atributos_es)
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
        "tipo_prenda": "pantalon",
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
    
    print("\n✅ Pantalón guardado exitosamente")
    print("==============================\n")
    
    return {
        "imageUrl": image_url,
        "prompt": prompt_en,
        "descripcion": descripcion_es,
        "costo": costo,
    }

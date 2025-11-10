# flask_api/controlador/control_conjunto_externo_ia_v1.py
import base64, io, requests, cloudinary.uploader
from flask import current_app
from googletrans import Translator
from bson import ObjectId

from flask_api.modelo.modelo_ia_prendas import guardar_prenda
from flask_api.controlador.prompts_conjunto_externo import build_prompts_conjunto_externo_v1, descripcion_conjunto_externo_es_v1

NEGATIVE_PROMPT = (
    "people, human, mannequin, arms, hands, fingers, legs, feet, faces, background, text, watermark, blurry, "
    "deformed, distorted, low quality"
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


def calcular_costo_produccion_conjunto(atributos: dict) -> dict:
    """Calcula el costo de producción de un conjunto deportivo externo"""
    # Costo base según la tela
    if atributos.get("tela") == "Algodón":
        costo_material = 8.5  # Chaqueta + Pantalón
    elif atributos.get("tela") == "Poliéster":
        costo_material = 6.5
    elif atributos.get("tela") == "Fleece":
        costo_material = 11.0
    else:
        costo_material = 7.5
    
    # Ajuste por complejidad del diseño
    camino = atributos.get("caminoSeleccionado", "solido_coordinado")
    if camino == "bloques_coordinados":
        costo_diseno = 3.5  # Costura de bloques en ambas piezas
    elif camino == "sublimado_ia":
        area = atributos.get("areaSublimacion", "completo_ambas")
        if area == "completo_ambas":
            costo_diseno = 7.0  # Sublimación completa en ambas piezas
        else:
            costo_diseno = 5.0  # Sublimación híbrida
    else:
        costo_diseno = 2.5  # Diseño simple coordinado
    
    costo_mano_obra = 2.5
    costo_insumos = 2.0
    
    total = round(costo_material + costo_mano_obra + costo_insumos + costo_diseno, 2)
    precio_venta = round(total * 1.65, 2)  # Margen del 65%
    precio_mayor = round(total * 1.35, 2)  # Margen del 35%
    
    return {
        "material": costo_material,
        "mano_obra": costo_mano_obra,
        "insumos": costo_insumos,
        "diseno": costo_diseno,
        "total": total,
        "precio_venta": precio_venta,
        "precio_mayor": precio_mayor,
    }


def generar_conjunto_externo_v1(categoria_id, atributos_es, user_id):
    """
    Genera las imágenes IA de un conjunto deportivo externo (chaqueta + pantalón)
    y guarda el conjunto en la base de datos.
    """
    STABLE_URL = current_app.config.get("STABLE_URL", "http://127.0.0.1:7860")
    
    print("\n==============================")
    print("🧥👖 INICIO generar_conjunto_externo_v1")
    print("==============================")
    
    # 1️⃣ Datos recibidos
    print("📥 Atributos recibidos (ES):", atributos_es)
    
    # 2️⃣ Traducción al inglés
    atributos_en = traducir_atributos(atributos_es)
    print("\n🌐 Atributos traducidos (EN):", atributos_en)
    
    # 3️⃣ Construcción de ambos prompts y descripción
    print("\n🧩 Entrando a build_prompts_conjunto_externo_v1 con:", atributos_en)
    prompt_chaqueta_en, prompt_pantalon_en = build_prompts_conjunto_externo_v1(atributos_en)
    print("🟣 Prompt chaqueta generado:\n", prompt_chaqueta_en, "\n")
    print("🟣 Prompt pantalón generado:\n", prompt_pantalon_en, "\n")
    
    descripcion_es = descripcion_conjunto_externo_es_v1(atributos_es)
    print("🟢 Descripción generada (ES):", descripcion_es)
    
    # 4️⃣ Generar imagen de la CHAQUETA
    payload_chaqueta = {
        "prompt": prompt_chaqueta_en,
        "negative_prompt": NEGATIVE_PROMPT,
        "width": 512,
        "height": 512,
        "sampler_name": "DPM++ 2M",
        "steps": 35,
        "cfg_scale": 7.5,
        "seed": -1,
    }
    
    try:
        print("\n📡 Enviando solicitud para CHAQUETA a Stable Diffusion...")
        response_chaqueta = requests.post(f"{STABLE_URL}/sdapi/v1/txt2img", json=payload_chaqueta)
        response_chaqueta.raise_for_status()
        data_chaqueta = response_chaqueta.json()
        img_base64_chaqueta = data_chaqueta["images"][0]
        print("✅ Imagen CHAQUETA generada correctamente")
    except Exception as e:
        print("❌ Error al generar la imagen de la chaqueta:", e)
        raise
    
    # 5️⃣ Generar imagen del PANTALÓN
    payload_pantalon = {
        "prompt": prompt_pantalon_en,
        "negative_prompt": NEGATIVE_PROMPT,
        "width": 512,
        "height": 768,  # Más alto para pantalones
        "sampler_name": "DPM++ 2M",
        "steps": 35,
        "cfg_scale": 7.5,
        "seed": -1,
    }
    
    try:
        print("\n📡 Enviando solicitud para PANTALÓN a Stable Diffusion...")
        response_pantalon = requests.post(f"{STABLE_URL}/sdapi/v1/txt2img", json=payload_pantalon)
        response_pantalon.raise_for_status()
        data_pantalon = response_pantalon.json()
        img_base64_pantalon = data_pantalon["images"][0]
        print("✅ Imagen PANTALÓN generada correctamente")
    except Exception as e:
        print("❌ Error al generar la imagen del pantalón:", e)
        raise
    
    # 6️⃣ Subir CHAQUETA a Cloudinary
    print("\n☁️ Subiendo imagen CHAQUETA a Cloudinary...")
    image_bytes_chaqueta = io.BytesIO(base64.b64decode(img_base64_chaqueta))
    cloud_chaqueta = cloudinary.uploader.upload(image_bytes_chaqueta, folder="Conjunto_Externo_V1/Chaquetas")
    image_url_chaqueta = cloud_chaqueta.get("secure_url")
    print("✅ Imagen chaqueta subida:", image_url_chaqueta)
    
    # 7️⃣ Subir PANTALÓN a Cloudinary
    print("\n☁️ Subiendo imagen PANTALÓN a Cloudinary...")
    image_bytes_pantalon = io.BytesIO(base64.b64decode(img_base64_pantalon))
    cloud_pantalon = cloudinary.uploader.upload(image_bytes_pantalon, folder="Conjunto_Externo_V1/Pantalones")
    image_url_pantalon = cloud_pantalon.get("secure_url")
    print("✅ Imagen pantalón subida:", image_url_pantalon)
    
    # 8️⃣ Calcular costo
    costo = calcular_costo_produccion_conjunto(atributos_es)
    print("\n💰 Costo de producción calculado:", costo)
    
    # 9️⃣ Asociar usuario
    try:
        user_obj_id = ObjectId(user_id) if user_id else None
    except Exception:
        user_obj_id = None
    
    # 🔟 Documento a guardar
    doc = {
        "user_id": user_obj_id,
        "categoria_prd": categoria_id,
        "tipo_prenda": "conjunto_externo",
        "descripcion": descripcion_es,
        "atributos_es": atributos_es,
        "atributos_en": atributos_en,
        "prompt_chaqueta_en": prompt_chaqueta_en,
        "prompt_pantalon_en": prompt_pantalon_en,
        "imageUrlChaqueta": image_url_chaqueta,
        "imageUrlPantalon": image_url_pantalon,
        "costo": costo,
        "estado": "generado",
    }
    
    print("\n🗂️ Documento a guardar en MongoDB:")
    for k, v in doc.items():
        print(f"   - {k}: {v if not isinstance(v, dict) else '[dict con datos]'}")
    
    guardar_prenda(doc)
    
    print("\n✅ Conjunto externo guardado exitosamente")
    print("==============================\n")
    
    return {
        "imageUrlChaqueta": image_url_chaqueta,
        "imageUrlPantalon": image_url_pantalon,
        "promptChaqueta": prompt_chaqueta_en,
        "promptPantalon": prompt_pantalon_en,
        "descripcion": descripcion_es,
        "costo": costo,
    }

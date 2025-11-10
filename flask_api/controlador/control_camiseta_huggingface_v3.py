# flask_api/controlador/control_camiseta_huggingface_v3.py
import io, cloudinary.uploader
from flask import current_app
from flask_api.modelo.modelo_ia_prendas import guardar_prenda
from flask_api.controlador.prompts import build_prompt_v3, descripcion_es_v3
from flask_api.controlador.control_camiseta_ia_v3 import traducir_atributos, calcular_costo_produccion
from bson import ObjectId
from huggingface_hub import InferenceClient
import os

def generar_camiseta_huggingface_v3(categoria_id, atributos_es, user_id):
    """
    Genera la imagen usando Hugging Face Inference API.
    Mantiene la misma estructura que Gemini y Stable Diffusion.
    """
    print("\n==============================")
    print("🚀 INICIO generar_camiseta_huggingface_v3")
    print("==============================")
    
    # 1️⃣ Traducir atributos al inglés
    print("📥 Atributos recibidos (ES):", atributos_es)
    atributos_en = traducir_atributos(atributos_es)
    print("\n🌐 Atributos traducidos (EN):", atributos_en)
    
    # 2️⃣ Generar prompt y descripción
    print("\n🧩 Generando prompt con build_prompt_v3...")
    prompt_en = build_prompt_v3(atributos_en)
    print("🟣 Prompt generado:\n", prompt_en)
    
    descripcion = descripcion_es_v3(atributos_es)
    print("🟢 Descripción generada (ES):", descripcion)
    
    # 3️⃣ Mejorar prompt para generación de prendas deportivas
    prompt_mejorado = (
        f"{prompt_en}, "
        "professional product photography, white background, "
        "high quality, detailed fabric texture, sportswear design, "
        "realistic lighting, 4k resolution, no people, no mannequin, "
        "catalog style, hyper-detailed"
    )
    print("\n🎨 Prompt mejorado para HF:", prompt_mejorado)
    
    # 4️⃣ Inicializar cliente de Hugging Face
    hf_token = os.environ.get("HF_TOKEN") or current_app.config.get("HF_TOKEN")
    if not hf_token:
        raise Exception("HF_TOKEN no configurado en variables de entorno")
    
    client = InferenceClient(
        provider="auto",
        api_key=hf_token
    )
    
    # 5️⃣ Generar imagen con Hugging Face
    try:
        print("\n📡 Enviando solicitud a Hugging Face API...")
        image = client.text_to_image(
            prompt_mejorado,
            model="black-forest-labs/FLUX.1-schnell"  # Modelo rápido y gratuito
        )
        print("✅ Imagen generada exitosamente con Hugging Face")
        
    except Exception as e:
        print(f"❌ Error al generar imagen con Hugging Face: {e}")
        print(f"❌ Prompt usado: {prompt_mejorado}")
        raise Exception(f"Error en Hugging Face API: {str(e)}")
    
    # 6️⃣ Convertir PIL Image a bytes
    print("\n🔄 Convirtiendo imagen a bytes...")
    image_bytes = io.BytesIO()
    image.save(image_bytes, format='PNG')
    image_bytes.seek(0)
    
    # 7️⃣ Subir a Cloudinary
    print("\n☁️ Subiendo imagen a Cloudinary...")
    cloud = cloudinary.uploader.upload(
        image_bytes, 
        folder="Camiseta_HuggingFace_V3"
    )
    image_url = cloud.get("secure_url")
    print("✅ Imagen subida:", image_url)
    
    # 8️⃣ Calcular costos
    costo = calcular_costo_produccion(atributos_es)
    print("\n💰 Costo calculado:", costo)
    
    # 9️⃣ Preparar usuario
    user_obj_id = ObjectId(user_id) if user_id else None
    
    # 🔟 Documento a guardar
    doc = {
        "user_id": user_obj_id,
        "categoria_prd": categoria_id,
        "descripcion": descripcion,
        "atributos_es": atributos_es,
        "atributos_en": atributos_en,
        "prompt_en": prompt_en,
        "imageUrl": image_url,
        "costo": costo,
        "modelo": "Hugging Face FLUX.1-schnell",
        "estado": "generado",
    }
    
    print("\n💾 Guardando prenda en MongoDB...")
    guardar_prenda(doc)
    print("✅ Prenda guardada exitosamente")
    print("==============================\n")
    
    return {
        "imageUrl": image_url,
        "prompt": prompt_en,
        "descripcion": descripcion,
        "costo": costo
    }

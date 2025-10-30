# flask_api/controlador/control_camiseta_gemini_v3.py
import io, base64, cloudinary.uploader, google.generativeai as genai
from flask import current_app
from flask_api.modelo.modelo_ia_prendas import guardar_prenda
from flask_api.controlador.prompts import build_prompt_v3, descripcion_es_v3
from flask_api.controlador.control_camiseta_ia_v3 import traducir_atributos, calcular_costo_produccion
from bson import ObjectId
from google.api_core.exceptions import ResourceExhausted


def generar_camiseta_gemini_v3(categoria_id, atributos_es, user_id):
    atributos_en = traducir_atributos(atributos_es)
    prompt_en = build_prompt_v3(atributos_en)
    descripcion = descripcion_es_v3(atributos_es)

    # Llamada a Gemini
    model = genai.GenerativeModel("gemini-2.5-flash-image")
    try:
            # 3. Llamada a la API de Google (Punto de fallo probable)
            response = model.generate_content(contents=[prompt_en]) 
            
            # Verificar si la respuesta fue bloqueada
            if not response.candidates:
                raise Exception("La API de Gemini bloqueó la respuesta o no pudo generar la imagen.")
                
    except ResourceExhausted:
            # Captura específica para el error 429 de cuota excedida
            error_msg = "Se ha excedido la cuota de uso de la API de Gemini. Intenta de nuevo más tarde."
            print(f"❌ ERROR: {error_msg}")
  
            return {"error": error_msg}, 429 
                                           

    except Exception as e:
        # Otros errores de la API (problemas de prompt, autenticación, etc.)
        error_msg = f"Error crítico no esperado al generar imagen con Gemini: {str(e)}"
        print(f"❌ ERROR CRÍTICO al llamar a la API de Gemini: {e}")
        raise

    image_url = None

    print("\n☁️ Subiendo imagen a Cloudinary...")
    for part in response.candidates[0].content.parts:
        if part.inline_data is not None:
            
            # 1. Obtener los bytes de la imagen
            image_data = part.inline_data.data 
            
            # 2. Crear el objeto BytesIO
            image_bytes = io.BytesIO(image_data)
            
            # 3. Subir a Cloudinary
            cloud = cloudinary.uploader.upload(image_bytes, folder="Camiseta_Gemini_V3")
            image_url = cloud.get("secure_url")
            print("✅ Imagen subida:", image_url)
            break
    if not image_url:
        raise Exception("Fallo al obtener los datos de la imagen generada por Gemini.")

    costo = calcular_costo_produccion(atributos_es)
    user_obj_id = ObjectId(user_id) if user_id else None

    doc = {
        "user_id": user_obj_id,
        "categoria_prd": categoria_id,
        "descripcion": descripcion,
        "atributos_es": atributos_es,
        "atributos_en": atributos_en,
        "prompt_en": prompt_en,
        "imageUrl": image_url,
        "costo": costo,
        "modelo": "Gemini Imagen 2.5",
        "estado": "generado",
    }
    
    print("💾 Guardando prenda en MongoDB...")
    guardar_prenda(doc)
    print("✅ Prenda guardada exitosamente")

    return {"imageUrl": image_url, "prompt": prompt_en, "descripcion": descripcion, "costo": costo}

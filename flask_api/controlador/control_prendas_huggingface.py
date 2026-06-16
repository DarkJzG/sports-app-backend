# flask_api/controlador/control_prendas_huggingface.py
import io, cloudinary.uploader, base64
from flask import current_app
from flask_api.modelo.modelo_ia_prendas import guardar_prenda, get_prendas_collection
from flask_api.controlador.control_camiseta_ia_v3 import traducir_atributos
from bson import ObjectId
from huggingface_hub import InferenceClient
import os

# Importar los builders de prompts de cada prenda
from flask_api.controlador.prompts import build_prompt_v3, descripcion_es_v3
from flask_api.controlador.prompts_pantalon import build_prompt_pantalon_v1, descripcion_pantalon_es_v1
from flask_api.controlador.prompts_chompa import build_prompt_chompa_v1, descripcion_chompa_es_v1
from flask_api.controlador.prompts_pantaloneta import build_prompt_pantaloneta_v1, descripcion_pantaloneta_es_v1
from flask_api.controlador.control_ficha_tecnica import construir_ficha_tecnica_detallada, generar_ficha_tecnica_prueba
from flask_api.modelo.modelo_ficha_tecnica import guardar_ficha, get_fichas_collection


def calcular_costo_prenda(atributos: dict, tipo_prenda: str) -> dict:
    """
    Calcula el costo de producción según el tipo de prenda y sus atributos.
    
    Args:
        atributos: Diccionario con los atributos de la prenda (en español)
        tipo_prenda: Tipo de prenda ("camiseta", "chompa", "pantalon", "pantaloneta")
    
    Returns:
        dict: Costos desglosados y precios de venta
    """
    tela = atributos.get("tela", "").lower()
    costo_diseno = 1.50  # Fijo para todas las prendas
    
    # Configuración de costos por tipo de prenda
    if tipo_prenda == "camiseta":
        # Camiseta: Algodón=3, Poliéster=2.75, Alg/Pol=2.50
        if "algodón" in tela or "algodon" in tela:
            costo_material = 3.0
        elif "poliéster" in tela or "poliester" in tela:
            costo_material = 2.75
        elif "alg/pol" in tela or "algodón/poliéster" in tela:
            costo_material = 2.50
        else:
            costo_material = 2.75  # Default poliéster
        
        costo_mano_obra = 0.70
        costo_insumos = 0.65
    
    elif tipo_prenda == "chompa":
        # Chompa: Algodón=8, Poliéster=9, Alg/Pol=6, Impermeable=5
        if "algodón" in tela or "algodon" in tela:
            costo_material = 8.0
        elif "poliéster" in tela or "poliester" in tela:
            costo_material = 9.0
        elif "mezcla" in tela or "mezcla" in tela:
            costo_material = 6.0
        elif "impermeable" in tela:
            costo_material = 5.0
        else:
            costo_material = 8.0  # Default algodón
        
        costo_mano_obra = 4.0
        costo_insumos = 1.25
    
    elif tipo_prenda == "pantalon":
        # Pantalón: Algodón=6, Poliéster=7, Alg/Pol=5, Impermeable=4
        if "algodón" in tela or "algodon" in tela:
            costo_material = 6.0
        elif "poliéster" in tela or "poliester" in tela:
            costo_material = 7.0
        elif "mezcla" in tela or "mezcla" in tela:
            costo_material = 5.0
        elif "impermeable" in tela:
            costo_material = 4.0
        else:
            costo_material = 6.0  # Default algodón
        
        costo_mano_obra = 2.0
        costo_insumos = 1.50
    
    elif tipo_prenda == "pantaloneta":
        # Pantaloneta: Algodón=5, Poliéster=6, Alg/Pol=4, Impermeable=3
        if "algodón" in tela or "algodon" in tela:
            costo_material = 3.50
        elif "poliéster" in tela or "poliester" in tela:
            costo_material = 3.0
        elif "mezcla" in tela or "mezcla" in tela:
            costo_material = 3.0
        elif "impermeable" in tela:
            costo_material = 3.0
        else:
            costo_material = 3.50  # Default algodón
        
        costo_mano_obra = 0.50
        costo_insumos = 1.0
    
    else:
        # Prenda genérica (fallback)
        costo_material = 3.0
        costo_mano_obra = 1.0
        costo_insumos = 1.0
    
    # Cálculos finales
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


def generar_prenda_huggingface(categoria_id, atributos_es, user_id, solo_prompt=False):
    # 1️⃣ Detectar tipo de prenda desde categoria_id
    tipo_prenda = "prenda"
    builder_prompt = None
    builder_descripcion = None
    
    if "camiseta" in categoria_id.lower():
        tipo_prenda = "camiseta"
        builder_prompt = build_prompt_v3
        builder_descripcion = descripcion_es_v3
    elif "pantalon" in categoria_id.lower() and "pantaloneta" not in categoria_id.lower():
        tipo_prenda = "pantalon"
        builder_prompt = build_prompt_pantalon_v1
        builder_descripcion = descripcion_pantalon_es_v1
    elif "chompa" in categoria_id.lower():
        tipo_prenda = "chompa"
        builder_prompt = build_prompt_chompa_v1
        builder_descripcion = descripcion_chompa_es_v1
    elif "pantaloneta" in categoria_id.lower():
        tipo_prenda = "pantaloneta"
        builder_prompt = build_prompt_pantaloneta_v1
        builder_descripcion = descripcion_pantaloneta_es_v1
    else:
        # Por defecto usar camiseta si no se detecta
        tipo_prenda = "prenda"
        builder_prompt = build_prompt_v3
        builder_descripcion = descripcion_es_v3
    
    print(f"\n{'='*50}")
    print(f"🚀 INICIO generar_{tipo_prenda}_huggingface")
    print(f"{'='*50}")
    print(f"📋 Categoría ID: {categoria_id}")
    print(f"🏷️  Tipo de prenda detectado: {tipo_prenda}")
    
    # 2️⃣ Mostrar atributos recibidos
    print(f"\n📥 Atributos recibidos (ES):")
    for key, value in atributos_es.items():
        if key not in ['userId']:  # No mostrar el userId en el log detallado
            print(f"   - {key}: {value}")
    
    # 3️⃣ Traducir atributos al inglés
    print("\n🌐 Traduciendo atributos al inglés...")
    atributos_en = traducir_atributos(atributos_es)
    print("✅ Atributos traducidos correctamente")
    
    # 4️⃣ Generar prompt usando el builder correspondiente
    print(f"\n🧩 Generando prompt con builder de {tipo_prenda}...")
    try:
        prompt_en = builder_prompt(atributos_en)
        print("✅ Prompt generado exitosamente")
        print(f"🟣 Prompt completo:\n{prompt_en}\n")
    except Exception as e:
        print(f"❌ Error al generar prompt: {e}")
        raise Exception(f"Error generando prompt para {tipo_prenda}: {str(e)}")
    
    # 5️⃣ Generar descripción en español
    print(f"🟢 Generando descripción en español...")
    try:
        descripcion = builder_descripcion(atributos_es)
        print(f"✅ Descripción: {descripcion}")
    except Exception as e:
        print(f"❌ Error al generar descripción: {e}")
        descripcion = f"{tipo_prenda.capitalize()} deportiva personalizada"

        # 🔍 Modo prueba: solo ver prompt y descripción, sin llamar a Hugging Face
    if solo_prompt:
        print("\n🧪 MODO SOLO_PROMPT ACTIVADO (no se llama a Hugging Face ni Cloudinary)")
        return {
            "prompt": prompt_en,
            "descripcion": descripcion,
            "atributos_en": atributos_en,
            "tipo_prenda": tipo_prenda,
        }

    
    # 6️⃣ Inicializar cliente de Hugging Face
    print("\n🔑 Inicializando cliente de Hugging Face...")
    hf_token = os.environ.get("HF_TOKEN") or current_app.config.get("HF_TOKEN")
    if not hf_token:
        raise Exception("❌ HF_TOKEN no configurado en variables de entorno")
    
    client = InferenceClient(provider="auto", api_key=hf_token)
    print("✅ Cliente inicializado correctamente")
    
    # 7️⃣ Generar imagen con Hugging Face (SIN prompt mejorado)
    try:
        print("\n📡 Enviando solicitud a Hugging Face API...")
        print("⏳ Generando imagen (esto puede tomar 10-30 segundos)...")
        
        image = client.text_to_image(
            prompt_en,  
            model="black-forest-labs/FLUX.1-schnell"
        )
        
        print("✅ Imagen generada exitosamente con Hugging Face")
        
    except Exception as e:
        print(f"❌ Error al generar imagen con Hugging Face API: {e}")
        print(f"❌ Prompt que causó el error: {prompt_en}")
        raise Exception(f"Error en Hugging Face API: {str(e)}")
    
    # 8️⃣ Convertir PIL Image a bytes
    print("\n🔄 Convirtiendo imagen a formato bytes...")
    try:
        image_bytes = io.BytesIO()
        image.save(image_bytes, format='PNG')
        image_bytes.seek(0)
        print("✅ Imagen convertida correctamente")
    except Exception as e:
        print(f"❌ Error al convertir imagen: {e}")
        raise Exception(f"Error convirtiendo imagen: {str(e)}")
    
    # 9️⃣ Subir a Cloudinary
    print("\n☁️ Subiendo imagen a Cloudinary...")
    try:
        folder_name = f"{tipo_prenda.capitalize()}_HuggingFace"
        cloud = cloudinary.uploader.upload(
            image_bytes, 
            folder=folder_name,
            resource_type="image"
        )
        image_url = cloud.get("secure_url")
        print(f"✅ Imagen subida exitosamente")
        print(f"🔗 URL: {image_url}")
    except Exception as e:
        print(f"❌ Error al subir a Cloudinary: {e}")
        raise Exception(f"Error subiendo imagen a Cloudinary: {str(e)}")
    
    # 🔟 Calcular costos de producción específicos por tipo de prenda
    print(f"\n💰 Calculando costos de producción para {tipo_prenda}...")
    costo = calcular_costo_prenda(atributos_es, tipo_prenda)
    print(f"✅ Costos calculados:")
    print(f"   - Material: ${costo['material']}")
    print(f"   - Mano de obra: ${costo['mano_obra']}")
    print(f"   - Insumos: ${costo['insumos']}")
    print(f"   - Diseño: ${costo['diseno']}")
    print(f"   - Total producción: ${costo['total']}")
    print(f"   - Precio venta sugerido: ${costo['precio_venta']}")
    print(f"   - Precio mayorista: ${costo['precio_mayor']}")
    
    # 1️⃣1️⃣ Preparar ObjectId del usuario
    try:
        user_obj_id = ObjectId(user_id) if user_id else None
    except Exception as e:
        print(f"⚠️ Warning: No se pudo convertir user_id a ObjectId: {e}")
        user_obj_id = None
    
    # 1️⃣2️⃣ Crear documento para MongoDB
    doc = {
        "user_id": user_obj_id,
        "categoria_prd": categoria_id,
        "tipo_prenda": tipo_prenda,
        "descripcion": descripcion,
        "atributos_es": atributos_es,
        "atributos_en": atributos_en,
        "prompt_en": prompt_en,
        "imageUrl": image_url,
        "costo": costo,
        "estado": "generado",
    }
    
    # 1️⃣3️⃣ Guardar en MongoDB
    print("\n💾 Guardando prenda en MongoDB...")
    prenda_id = None
    try:
        prenda_id = guardar_prenda(doc)  # ✅ Que esta función retorne el _id como string
        print(f"✅ {tipo_prenda.capitalize()} guardada exitosamente en la base de datos con ID {prenda_id}")
    except Exception as e:
        print(f"❌ Error al guardar en MongoDB: {e}")

    # 1️⃣4️⃣ Generar y guardar ficha técnica INDIVIDUAL
    ficha_id = None
    ficha_pdf_url = None
    try:
        if prenda_id:
            # Construir URLs de imágenes para la ficha
            image_urls = {
                "delantera": image_url,   # para ahora usamos la misma
                "posterior": None,
                "acabado": image_url,
            }

            ficha = construir_ficha_tecnica_detallada(
                categoria_prd=tipo_prenda,
                atributos=atributos_es,
                image_urls=image_urls
            )

            # Añadir costo y talla si aplica (talla viene cuando el usuario escoja, aquí solo costo base)
            ficha["costo"] = costo
            ficha["descripcion"] = descripcion

            ficha_doc = {
                "user_id": str(user_id) if user_id else None,
                "prenda_id": prenda_id,
                "ficha": ficha,
            }

            ficha_id = guardar_ficha(ficha_doc)
            print(f"📄 Ficha técnica guardada en fichas_tecnicas con ID {ficha_id}")

            # Opcional: generar PDF base64 y subirlo a Cloudinary
            try:
                pdf_b64 = generar_ficha_tecnica_prueba(ficha)
                pdf_bytes = io.BytesIO(base64.b64decode(pdf_b64))
                upload_pdf = cloudinary.uploader.upload(
                    pdf_bytes,
                    folder=f"fichas_ia/{tipo_prenda}",
                    public_id=f"ficha_{prenda_id}",
                    resource_type="raw",
                    format="pdf"
                )
                ficha_pdf_url = upload_pdf.get("secure_url")
                print(f"📎 Ficha técnica PDF subida: {ficha_pdf_url}")

                fichas_col = get_fichas_collection()
                fichas_col.update_one(
                    {"_id": ObjectId(ficha_id)},
                    {"$set": {"url_pdf": ficha_pdf_url}},
                )

                # Actualizar prenda IA con ficha_id y url pdf
                col_prendas = get_prendas_collection()
                col_prendas.update_one(
                    {"_id": ObjectId(prenda_id)},
                    {"$set": {
                        "ficha_id": ficha_id,
                        "ficha_pdf_url": ficha_pdf_url
                    }}
                )
            except Exception as e:
                print(f"⚠️ No se pudo generar/subir PDF de ficha IA: {e}")

    except Exception as e:
        print(f"⚠️ Error generando ficha técnica IA: {e}")

    print(f"\n{'='*50}")
    print(f"🎉 PROCESO COMPLETADO EXITOSAMENTE")
    print(f"{'='*50}\n")
    
    # 1️⃣4️⃣ Retornar resultado
    return {
        "imageUrl": image_url,
        "prompt": prompt_en,
        "descripcion": descripcion,
        "costo": costo,
        "tipo_prenda": tipo_prenda
    }

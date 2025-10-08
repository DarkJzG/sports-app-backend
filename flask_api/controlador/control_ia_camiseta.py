# flask_api/controlador/control_ia_camiseta.py
import base64, io, requests
import cloudinary.uploader
from flask import current_app
from bson import ObjectId
from googletrans import Translator
from flask_api.componente.traducciones import TRADUCCIONES


from flask_api.modelo.modelo_ia_prendas import guardar_prenda
from flask_api.modelo.modelo_ficha_tecnica import guardar_ficha
from flask_api.controlador.control_ficha_tecnica import construir_ficha_tecnica_detallada

NEGATIVE_PROMPT = (
    "person, people, mannequin, dummy, model, human, arms, hands, fingers, "
    "faces, background, logos, text, watermark, shadows"
)

translator = Translator()

def traducir_texto(texto: str) -> str:
    if not texto:
        return ""
    try:
        result = translator.translate(texto, src="es", dest="en")
        return result.text
    except Exception as e:
        print("⚠️ Error al traducir:", e)
        return texto  # fallback: deja el texto en español

def traducir_atributos(atributos: dict) -> dict:
    traducidos = {}
    for key, value in atributos.items():
        if isinstance(value, str):
            traducidos[key] = TRADUCCIONES.get(value, value)
        elif isinstance(value, dict):
            traducidos[key] = traducir_atributos(value)
        else:
            traducidos[key] = value
    return traducidos

def construir_descripcion_es(atributos_es: dict) -> str:
    genero = atributos_es.get("genero", "unisex")
    cuello = atributos_es.get("cuello", "")
    manga = atributos_es.get("manga", "")
    tela = atributos_es.get("tela", "")
    diseno = atributos_es.get("diseno", "")
    color1 = atributos_es.get("color1", "")
    color2 = atributos_es.get("color2", "")

    return f"Camiseta deportiva para {genero}, manga {manga}, con cuello {cuello}, fabricada en {tela}, con diseño {diseno} con colores {color1} y {color2}."



def generar_camiseta(categoria_id, atributos, user_id):
    STABLE_URL = current_app.config.get("STABLE_URL", "http://127.0.0.1:7860")
    print("🟢 Generando camiseta con:", categoria_id, atributos, user_id)

    atributos_es = traducir_atributos(atributos)
    prompt = build_prompt_v2(atributos)
    print("🔵 Prompt generado:", prompt)

    payload = {
        "prompt": prompt,
        "negative_prompt": NEGATIVE_PROMPT,
        "steps": 30,
        "sampler_name": "DPM++ 2M",
        "cfg_scale": 7.5,
        "width": 1024,
        "height": 1024
    }

    try:

        print("📡 Enviando a Stable Diffusion:", STABLE_URL)
        response = requests.post(f"{STABLE_URL}/sdapi/v1/txt2img", json=payload, timeout=90)
        print("📡 Respuesta SD status:", response.status_code)
        print("📡 Respuesta SD body:", response.text[:300])  # primeros 300 chars
        response.raise_for_status()

        r = response.json()
        images = r.get("images", [])
        if not images:
            return {"error": "No se generó imagen desde SD"}

        # 2️⃣ Subida a Cloudinary
        img_data = base64.b64decode(images[0])
        img_file = io.BytesIO(img_data)
        print("📡 Subiendo imagen a Cloudinary...")
        upload_result = cloudinary.uploader.upload(img_file, folder="camisetasV2")
        print("📡 Cloudinary result:", upload_result)
        image_url = upload_result.get("secure_url")

        
        tela = atributos.get("tela", "cotton")

        costo_material = 3.0 if tela == "cotton" else 2.0 if tela == "polyester" else 3.50
        costo_mano_obra = 0.70
        conto_insumos = 0.80
        costo_diseno = 1.5
        costo_total = costo_material + costo_mano_obra + conto_insumos + costo_diseno



        ficha_tecnica = construir_ficha_tecnica_detallada(
            "camiseta",
            atributos_es,
            {
                "delantera": "https://res.cloudinary.com/dcn5d4wbo/image/upload/v1759364001/CamisetaDelantera_ildkap.png",
                "posterior": "https://res.cloudinary.com/dcn5d4wbo/image/upload/v1759363999/CamisetaTrasera_yigesw.png",
                "acabado": image_url 
            }
        )

        ficha_tecnica["costo"] = {
            "material": costo_material,
            "mano_obra": costo_mano_obra,
            "insumos": conto_insumos,
            "diseno": costo_diseno,
            "total": costo_total,
        }


        ficha_id = guardar_ficha({
            "user_id": ObjectId(user_id),
            "categoria": "camiseta",
            "modelo": ficha_tecnica.get("modelo", ""),
            "imagenes": ficha_tecnica.get("imagenes", {}),
            "descripcion": ficha_tecnica.get("descripcion", ""),
            "caracteristicas": ficha_tecnica.get("caracteristicas", {}),
            "atributos": ficha_tecnica.get("atributos", {}),
            "piezas": ficha_tecnica.get("piezas", []),
            "insumos": ficha_tecnica.get("insumos", []),
            "especificaciones": ficha_tecnica.get("especificaciones", []),
            "costo": ficha_tecnica.get("costo", {})
        })



        prenda_id = guardar_prenda({
            "user_id": ObjectId(user_id),
            "categoria_prd": "camiseta_ia",
            "descripcion": construir_descripcion_es(atributos_es),
            "atributos_es": atributos_es,
            "atributos_en": atributos,
            "prompt_en": prompt,
            "imageUrl": image_url,
            "ficha_id": ficha_id,
            "estado": "generado",
            "costo": {
                    "material": costo_material,
                    "mano_obra": costo_mano_obra,
                    "insumos": conto_insumos,
                    "diseno": costo_diseno,
                    "total": costo_total
                    },
            "precio_venta": costo_total * 1.5,
            "precio_mayor": costo_total * 1.2
        })

        print("🟡 Atributos ES antes de guardar ficha:", atributos_es)
        print("🟡 Atributos EN:", atributos)
        print("🟡 Ficha técnica construida:", ficha_tecnica)

        return {
            "id": prenda_id, 
            "imageUrl": image_url,   
            "descripcion": construir_descripcion_es(atributos_es),
            "costo": {"total": costo_total},
            "precio_venta": costo_total * 1.5,
            "precio_mayor": costo_total * 1.2
            }

    except Exception as e:
        import traceback
        print("❌ Error en generar_camiseta:", traceback.format_exc())
        return {"error": f"Error en generación V2: {str(e)}"}



def build_prompt_v2(atributos: dict) -> str:
    # Datos base
    diseno = atributos.get("diseno", "solid")
    color1 = atributos.get("color1", "white")
    color2 = atributos.get("color2")
    opts   = atributos.get("opcionesDiseno", {}) or {}
    extra_colors = opts.get("extraColors")
    cuello = atributos.get("cuello", "round neck")
    manga  = atributos.get("manga", "short sleeves")
    tela   = atributos.get("tela", "polyester")
    genero = atributos.get("genero", "unisex")

    # 🔹 Base deportiva común (siempre presente)
    prompt_base = [
        "high-end photorealistic sportswear t-shirt mockup",
        f"for {genero}, with {cuello} and {manga}, made of breathable {tela} fabric",
        
    ]

    prompt_patron = []



    # 🔹 Patrón específico
    if diseno == "gradient":
        style = opts.get("style", "linear")
        direction = opts.get("direction", "vertical")
        softness = opts.get("softness", "medium")

        softness_map = {
            "soft": "smooth soft transition",
            "medium": "balanced gradient transition",
            "hard": "distinct sharp transition"
        }
        softness_desc = softness_map.get(softness, "balanced gradient transition")

        prompt_patron = [
            f"The main body features a full {style} gradient pattern",
            f"The color transitions {direction}ly from {color1} to {color2},",
            f"{softness_desc}"
        ]

    elif diseno == "heather":
        density  = opts.get("density", "medium")
        contrast = opts.get("contrast", "medium")
        grain    = opts.get("grain", "regular")

        prompt_patron = [
            f"The entire shirt features a {color1} and {color2} heather texture",
            f"this is an all-over speckled pattern",
            f"with {density} density and {contrast} contrast",
            f"having a {grain} textile grain",
        ]

    elif diseno == "geometric":

        extra_colors = opts.get("extraColors")
        shape    = opts.get("shape", "triangles")
        scale    = opts.get("scale", "medium")
        spacing  = opts.get("spacing", "regular")
        align    = opts.get("alignment", "centered")
        layering = opts.get("layering", "flat, non-overlapping").replace(',', '')

        color_figura = [color2] + (extra_colors or [])

        color_figura_str = ", ".join([f"**{c}**" for c in color_figura])

        prompt_patron = [
            f"The pattern is set against a **{color1} base color**, with geometric fragments colored: {color_figura_str}"
            f"dynamic and complex polygonal pattern covering the entire shirt",
            f"the design features {layering} **{shape}** and abstract geometric shards",
            f"pattern scale: {scale}",
            f"element spacing: {spacing}",
            f"alignment style: {align}",
            f"highly intricate and dynamic aesthetic",
        ]

    elif diseno == "abstract":
        style = opts.get("style", "paint splatter")
        intensity = opts.get("intensity", "bold")
        coverage  = opts.get("coverage", "all-over full coverage")
        flow_direction = opts.get("flow_direction", "random")
        extra_colors = opts.get("extraColors")


        color_patron = [color2] + (extra_colors or [])
        
        color_patron_vibrant = [f"**vibrant {c}**" for c in color_patron]
        color_patron_str = ", ".join(color_patron_vibrant)

        prompt_patron = [
            f"The pattern is set against a **{color1} base color**, with the abstract elements in colors: **{color_patron_str}**",
            f"**{coverage}** abstract **{style}** design",
            f"with **{intensity} intensity** and elements {flow_direction}",
            f"highly artistic and expressive aesthetic",
        ]
        

    elif diseno == "solid":
        prompt_patron = [
            f"solid color fabric",
            f"{color1}"
        ]

    elif diseno == "stripes":
        # Nuevos parámetros
        direction = opts.get("direction", "horizontal")
        style     = opts.get("style", "uniform and continuous")
        
        # Parámetros existentes
        thickness = opts.get("thickness", "medium")
        spacing = opts.get("spacing", "regular")
        edge = opts.get("edge", "hard edge")
        extra_colors = opts.get("extraColors")


        stripe_colors = [color2] + (extra_colors or [])
        stripe_colors_str = ", ".join([f"**{c}**" for c in stripe_colors])

        prompt_patron = [
            f"The pattern is set against a **{color1} base color**",
            f"with stripes in colors: {stripe_colors_str} in **{direction} stripes** pattern",
            
            f"The stripes are **{style}**, with a **{edge}** transition",
            
            f"stripe thickness: {thickness}, spacing: {spacing}",
            
            f"clean, high-contrast linear aesthetic",
        ]

    elif diseno == "camouflage":
        palette = opts.get("palette", "earth tones")
        scale   = opts.get("scale", "medium")
        edge    = opts.get("edge", "organic shapes")
        style = opts.get("style", "splintered fragmented shapes")
        
        color_figura = color2 + color1    

        if palette == "vibrant":

            colors_list_modified = [f"**vibrant {c}**" for c in color_figura]
            palette_desc = f"all-over **vibrant neon camouflage** pattern"
            
        else:
            colors_list_modified = [f"**{c}**" for c in color_figura]
            palette_desc = f"all-over **{palette} camouflage** pattern"
            
            palette_desc += f", utilizing the color tones of a **{palette}** environment"

        all_colors_str = ", ".join(colors_list_modified)

        prompt_patron = [
            palette_desc,
            f"**{style}** style",
            f"using colors: {all_colors_str}",
            f"The blotches have {edge} and are **{scale} scale**",
            f"geometric sport-camo aesthetic",
        ]

    elif diseno == "two_tone":
        division = opts.get("division", "horizontal")
        division_style = opts.get("division_style", "straight line") # Nuevo
        placement = opts.get("placement", "full color block") # Nuevo
        ratio = opts.get("ratio", 50)
        edge = opts.get("edge", "clean edge")

        prompt_patron = [
            f"**{placement}** two-tone color block design",
            f"using colors **{color1}** and **{color2}**",
            f"divided by a **{division} {division_style}** line",
            f"with an approximate ratio of {ratio}:{100-int(ratio)}, and a **{edge}** boundary",
            f"modern, minimal, high-contrast aesthetic",
        ]


    elif diseno == "full_print":
        complexity = opts.get("complexity", "moderate")
        motif      = opts.get("motif")
        style      = opts.get("style")
        density    = opts.get("density", "dense, seamless repetition")
        texture    = opts.get("texture", "vector art")

        motif_en = traducir_texto(motif) if motif else None
        style_en = traducir_texto(style) if style else None

        colors_str = f"primarily in **{color1}** and **{color2}** colors"

        motif_phrase = ""

        prompt_patron = [
            f"all-over **{density}** full print design covering entire shirt",
            f"featuring a **{motif_en}** theme" if motif_en else "",
            f"with **{complexity}** detail",
            f"{colors_str}",
            f"rendered in a **{style_en or texture}** style, highly detailed and seamless",
        ]

    # === Fallback ===
    prompt_detalle = [
        "displayed on an invisible mannequin, ",
        "perfect studio lighting, catalog style, ",
        "sharp focus, plain light gray background, ",
        "no logos, no text, hyper-detailed textile texture."
    ]


    return ", ".join(prompt_base + prompt_patron + prompt_detalle)

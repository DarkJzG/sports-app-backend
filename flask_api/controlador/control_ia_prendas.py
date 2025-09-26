# flask_api/controlador/control_ia_prendas.py
import base64, io, requests
from bson import ObjectId
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
from reportlab.lib.units import cm
from PIL import Image as PILImage
import cloudinary.uploader
from flask import current_app

from flask_api.modelo.modelo_ia_prendas import guardar_prenda

NEGATIVE_PROMPT = (
    "body, human, man, woman, mannequin, arms, hands, fingers, faces, model, "
    "limbs, text, logos"
)

MAPEO_ATRIBUTOS_ES = {
    #Tela
    "cotton" : "algodón",
    "polyester" : "poliéster",
    "cotton/polyester blend" : "algodón/poliéster",

    # Estilos
    "sports style": "deportiva",
    "casual style": "casual",
    "urban style": "urbana",
    "retro style": "retro",

    # Colores
    "black": "negro",
    "white": "blanco",
    "red": "rojo",
    "blue": "azul",
    "green": "verde",
    "yellow": "amarillo",
    "gray": "gris",
    "orange": "naranja",
    "purple": "morado",
    "sky blue": "celeste",

    # Cuello
    "round neck": "cuello redondo",
    "V-neck": "cuello en V",
    "polo collar": "cuello polo",

    # Mangas
    "short sleeves": "manga corta",
    "long sleeves": "manga larga",

    # Diseños
    "striped": "rayas",
    "lined": "líneas",
    "geometric": "geométrico",
    "abstract": "abstracto",
    "paint splatter": "manchas de pintura",
    "gradient": "degradado",
    "other": "otro",

    # Estilos avanzados
    "brush strokes": "brochazos",
    "splatter": "salpicaduras",
    "minimalist": "minimalista",
    "futuristic": "futurista",
    "camouflage": "camuflaje",

    # Acabados
    "matte finish": "mate",
    "glossy finish": "brillante",
    "textured finish": "texturizado",

    # Género
    "male": "hombre",
    "female": "mujer",
    "unisex": "unisex",
}


# --------------------------------------
# Diccionario básico EN → ES (para mostrar al cliente)
# --------------------------------------
TRADUCCION_BASICA_INVERSA = {
    "T-shirt": "camiseta",
    "sports style": "deportiva",
    "urban style": "urbana",
    "casual style": "casual",
    "retro style": "retro",
    "round neck": "cuello redondo",
    "V-neck": "cuello en V",
    "polo collar": "cuello polo",
    "short sleeves": "manga corta",
    "long sleeves": "manga larga",
    "sleeveless": "sin mangas",
    "gradient": "degradado",
    "paint splatter": "manchas de pintura",
    "geometric": "geométrico",
    "abstract": "abstracto",
    "ribbed details on collar and sleeves": "ribetes en cuello y mangas",
    "bicolor sleeves and collar": "bicolor en mangas/cuello",
    "visible seams": "costuras visibles",
    "matte finish": "acabado mate",
    "glossy finish": "acabado brillante",
    "textured finish": "acabado texturizado",
    "studio lighting": "iluminación de estudio",
    "plain white background": "fondo blanco liso",
    "sharp focus": "enfoque nítido",
}

def traducir_atributos_es(atributos):
    traducidos = {}
    for clave, valor in atributos.items():
        if isinstance(valor, list):
            traducidos[clave] = [MAPEO_ATRIBUTOS_ES.get(v, v) for v in valor]
        else:
            traducidos[clave] = MAPEO_ATRIBUTOS_ES.get(valor, valor)
    return traducidos



def traducir_prompt_en_es(prompt_en: str) -> str:
    prompt_es = prompt_en
    for en, es in TRADUCCION_BASICA_INVERSA.items():
        prompt_es = prompt_es.replace(en, es)
    return prompt_es


def calcular_precio_final(categoria_id, atributos):
    db = current_app.mongo.db
    mano = None
    try:
        mano = db.mano_obra.find_one({"categoria_id": ObjectId(categoria_id)})
    except Exception:
        pass

    if not mano:
         mano = db.mano_obra.find_one({"categoria_id": str(categoria_id)})
         
    if not mano:
        return {"costo": 0, "precio": 0, "precio_mayor": 0}

    # costos base de mano de obra
    insumos = float(mano.get("insumosTotal", 0))
    mano_prenda = float(mano.get("mano_obra_prenda", 0))

    # tela (ej: 1.20 m × $1.50)
    metros_tela = 1.20
    precio_metro = 1.50
    costo_tela = metros_tela * precio_metro

    # sublimado/bordado si el diseño lo requiere
    costo_diseno = 0
    if atributos.get("diseno") in ["sublimado", "bordado"]:
        costo_diseno = 4.0

    # total de costos
    costo = insumos + mano_prenda + costo_tela + costo_diseno

    # precio final = costo + ganancia
    ganancia = 3.0
    precio_venta = costo + ganancia

    # precio al mayor (ej. 10% descuento)
    precio_mayor = precio_venta * 0.9

    return {
        "costo": round(costo, 2),
        "precio": round(precio_venta, 2),
        "precio_mayor": round(precio_mayor, 2)
    }


# --------------------------------------
# Costos
# --------------------------------------
def calcular_costo_prenda(categoria_prd, atributos):
    base_costos = {
        "camiseta": 5.0,
        "pantalon": 8.0,
        "chompa": 12.0,
        "conjunto_interno": 15.0,
        "conjunto_externo": 20.0,
    }
    costo = base_costos.get(categoria_prd, 10.0)

    tela = atributos.get("tela", "").lower()
    if tela == "poliéster":
        costo += 1
    elif tela == "algodón":
        costo += 2

    if atributos.get("diseno") in ["sublimado", "bordado"]:
        costo += 3

    return round(costo, 2)


# --------------------------------------
# PROMPT en inglés → traducido a español
# --------------------------------------
def generar_prompt(categoria_prd, atributos):
    if categoria_prd == "Camiseta":
        estilo = atributos.get("estilo", "")
        color1 = atributos.get("color1", "")
        color2 = atributos.get("color2", "")
        diseno = atributos.get("diseno", "")
        cuello = atributos.get("cuello", "")
        manga = atributos.get("manga", "")
        tela = atributos.get("tela", "")
        genero = atributos.get("genero", "")


        # Nuevos campos
        estiloAvanzado = atributos.get("estiloAvanzado", "")
        ubicacion = atributos.get("ubicacion", "")
        detalles = atributos.get("detalles", [])
        acabado = atributos.get("acabado", "")

        partes_en = [
            f"Centered front view, high-quality mockup of a {color1} {tela} {estilo} T-shirt"
        ]

        if diseno and color2:
            partes_en.append(f"featuring a {color2} {diseno} design {('on ' + ubicacion) if ubicacion else ''}")
        elif color2:
            partes_en.append(f"with {color2} details")

        if estiloAvanzado:
            partes_en.append(estiloAvanzado)
        if cuello:
            partes_en.append(cuello)
        if manga:
            partes_en.append(manga)
        if genero:
            partes_en.append(f"for {genero}")
        if detalles:
            partes_en.append(", ".join(detalles))
        if acabado:
            partes_en.append(acabado)

        partes_en.extend([
            "studio lighting",
            "plain white background",
            "sharp focus",
            "no logos",
            "no text",
            "no limbs",
            "just the T-shirt"
        ])

        prompt_en = ", ".join(partes_en)
        prompt_es = traducir_prompt_en_es(prompt_en)

        return prompt_es, prompt_en

    # fallback
    prompt_en = f"{categoria_prd} with attributes: {atributos}"
    prompt_es = traducir_prompt_en_es(prompt_en)
    return prompt_es, prompt_en


def generar_descripcion_es(categoria_prd, atributos_es):
    partes = [f"{categoria_prd.capitalize()} de {atributos_es.get('tela', '')} con estilo {atributos_es.get('estilo', '')}"]

    color1 = atributos_es.get("color1")
    color2 = atributos_es.get("color2")
    if color1 and color2:
        partes.append(f"de color {color1} con {color2}")
    elif color1:
        partes.append(f"de color {color1}")

    diseno = atributos_es.get("diseno")
    if diseno:
        partes.append(f"con un diseño de {diseno}")

    estiloAvanzado = atributos_es.get("estiloAvanzado")
    if estiloAvanzado:
        partes.append(estiloAvanzado)

    acabado = atributos_es.get("acabado")
    if acabado:
        partes.append(f"con acabado {acabado}")

    return " ".join(partes)


# --------------------------------------
# Ficha técnica
# --------------------------------------
def generar_ficha_tecnica(categoria_prd, atributos):
    return {
        "Tipo": categoria_prd,
        "Estilo": atributos.get("estilo", ""),
        "Color principal": atributos.get("color1", ""),
        "Color secundario": atributos.get("color2", ""),
        "Diseño": atributos.get("diseno", ""),
        "Estilo avanzado": atributos.get("estiloAvanzado", ""),
        "Ubicación diseño": atributos.get("ubicacion", ""),
        "Detalles": ", ".join(atributos.get("detalles", [])),
        "Acabado": atributos.get("acabado", ""),
        "Cuello": atributos.get("cuello", ""),
        "Manga": atributos.get("manga", ""),
        "Tela": atributos.get("tela", ""),
        "Género": atributos.get("genero", ""),
    }


# --------------------------------------
# Generar imágenes
# --------------------------------------
def generar_imagen(categoria_id, categoria_prd, atributos, user_id):
    STABLE_URL = current_app.config.get("STABLE_URL", "http://127.0.0.1:7860")
    prompt_es, prompt_en = generar_prompt(categoria_prd, atributos)

    # Traducción de atributos
    atributos_es = traducir_atributos_es(atributos)
    descripcion_es = generar_descripcion_es(categoria_prd, atributos_es)

    payload = {
        "prompt": prompt_en,
        "negative_prompt": NEGATIVE_PROMPT,
        "steps": 30,
        "sampler_name": "DPM++ 2M",
        "cfg_scale": 7,
        "width": 800,
        "height": 800,
        "batch_size": 1
    }

    current_app.logger.info(f"📡 POST {STABLE_URL}/sdapi/v1/txt2img")
    try:
        response = requests.post(f"{STABLE_URL}/sdapi/v1/txt2img", json=payload, timeout=120)
        response.raise_for_status()
        r = response.json()
        images = r.get("images", [])

        if not images:
            return {"error": "No se generaron imágenes"}

        # Subir primera a Cloudinary
        image_base64 = images[0]
        image_data = base64.b64decode(image_base64)
        image_file = io.BytesIO(image_data)
        upload_result = cloudinary.uploader.upload(image_file, folder="prendasIA")
        image_url = upload_result.get("secure_url")

        ficha_tecnica = generar_ficha_tecnica(categoria_prd, atributos_es)
        precios = calcular_precio_final(categoria_id, atributos_es)

        doc = {
            "user_id": ObjectId(user_id),
            "categoria_prd": categoria_prd,
            "atributos": atributos_es,
            "prompt_es": prompt_es,
            "descripcion_es": descripcion_es,
            "prompt_en": prompt_en,
            "imageUrl": image_url,
            "ficha_tecnica": ficha_tecnica,
            "costo": precios["costo"],
            "precio_venta": precios["precio"],
            "precio_mayor": precios["precio_mayor"],
            "estado": "generado"
        }
        inserted_id = guardar_prenda(doc)

        return {
            "id": inserted_id,
            "descripcion": descripcion_es,
            "imageUrl": image_url,
            "ficha_tecnica": ficha_tecnica,
            "costo": precios["costo"],
            "precio_venta": precios["precio"],
            "precio_mayor": precios["precio_mayor"],
        }

    except Exception as e:
        return {"error": f"Error al generar imagen en Stable Diffusion: {str(e)}"}

# --------------------------------------
# PDF ficha técnica
# --------------------------------------
def generar_pdf(ficha, imagen_b64=None, image_url=None):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    elements = []

    styles = getSampleStyleSheet()
    title_style = styles["Heading1"]
    elements.append(Paragraph("FICHA TÉCNICA DE PRENDA", title_style))
    elements.append(Spacer(1, 0.5*cm))

    tabla_data = [["Campo", "Valor"]] + [[k, v if v else "-"] for k, v in ficha.items()]
    tabla = Table(tabla_data, colWidths=[6*cm, 10*cm])
    tabla.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.lightblue),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("ALIGN", (0, 0), (-1, -1), "LEFT"),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
    ]))
    elements.append(tabla)
    elements.append(Spacer(1, 1*cm))

    # Imagen
    img_io = None
    if imagen_b64:
        img_data = base64.b64decode(imagen_b64)
        img_io = io.BytesIO(img_data)
    elif image_url:
        resp = requests.get(image_url, stream=True)
        img_io = io.BytesIO(resp.content)

    if img_io:
        pil_img = PILImage.open(img_io)
        temp_io = io.BytesIO()
        pil_img.save(temp_io, format="JPEG")
        temp_io.seek(0)
        elements.append(Image(temp_io, width=10*cm, height=10*cm, kind="proportional"))

    doc.build(elements)
    buffer.seek(0)
    pdf_b64 = base64.b64encode(buffer.read()).decode("utf-8")
    return pdf_b64

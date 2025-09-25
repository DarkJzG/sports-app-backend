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

# --------------------------------------
# Diccionario básico EN → ES (para mostrar al cliente)
# --------------------------------------
TRADUCCION_BASICA_INVERSA = {
    "T-shirt": "camiseta",
    "sports style": "deportiva",
    "urban style": "urbana",
    "casual style": "casual",
    "formal style": "formal",
    "round neck": "cuello redondo",
    "V-neck": "cuello en V",
    "polo collar": "cuello polo",
    "short sleeves": "manga corta",
    "long sleeves": "manga larga",
    "sleeveless": "sin mangas",
    "stripes": "rayas",
    "checkered pattern": "cuadros",
    "polka dots": "círculos",
    "gradient": "degradado",
    "printed": "estampado",
    "sublimated": "sublimado",
    "embroidered": "bordado",
    "plain white background": "fondo blanco liso",
    "studio lighting": "iluminación de estudio",
    "sharp focus": "enfoque nítido",
}

def traducir_prompt_en_es(prompt_en: str) -> str:
    prompt_es = prompt_en
    for en, es in TRADUCCION_BASICA_INVERSA.items():
        prompt_es = prompt_es.replace(en, es)
    return prompt_es


# --------------------------------------
# Costos
# --------------------------------------
def calcular_costo_prenda(tipo_prenda, atributos):
    base_costos = {
        "camiseta": 5.0,
        "pantalon": 8.0,
        "chompa": 12.0,
        "conjunto_interno": 15.0,
        "conjunto_externo": 20.0,
    }
    costo = base_costos.get(tipo_prenda, 10.0)

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
def generar_prompt(tipo_prenda, atributos):
    if tipo_prenda == "camiseta":
        estilo = atributos.get("estilo", "")
        color1 = atributos.get("color1", "")
        color2 = atributos.get("color2", "")
        cuello = atributos.get("cuello", "")
        manga = atributos.get("manga", "")
        patron = atributos.get("patron", "")
        color_patron = atributos.get("colorPatron", "")

        partes_en = [
            f"Centered front view, high-quality mockup of a {color1} {estilo} T-shirt"
        ]

        if color2:
            partes_en.append(f"with {color2} details")
        if patron and color_patron:
            partes_en.append(f"with {color_patron} {patron.lower()} pattern")
        if cuello:
            partes_en.append(f"{cuello} neck")
        if manga:
            partes_en.append(f"{manga} sleeves")

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
        prompt_es = traducir_prompt_en_es(prompt_en)  # traducido para mostrar al usuario

        return prompt_es, prompt_en

    # fallback
    prompt_en = f"{tipo_prenda} with attributes: {atributos}"
    prompt_es = traducir_prompt_en_es(prompt_en)
    return prompt_es, prompt_en


# --------------------------------------
# Ficha técnica
# --------------------------------------
def generar_ficha_tecnica(tipo_prenda, atributos):
    return {
        "Tipo": tipo_prenda,
        "Estilo": atributos.get("estilo", ""),
        "Colores": f"{atributos.get('color1','')} {atributos.get('color2','')}".strip(),
        "Patrón": atributos.get("patron", ""),
        "Color patrón": atributos.get("colorPatron", ""),
        "Talla": atributos.get("talla", ""),
        "Tela": atributos.get("tela", ""),
        "Diseño": atributos.get("diseno", ""),
        "Género": atributos.get("genero", ""),
    }


# --------------------------------------
# Generar imágenes
# --------------------------------------
def generar_imagen(tipo_prenda, atributos, user_id):
    STABLE_URL = current_app.config.get("STABLE_URL", "http://127.0.0.1:7860")
    prompt_es, prompt_en = generar_prompt(tipo_prenda, atributos)

    # Form vs Guía
    origen = atributos.get("origen", "form")
    batch_size = 2 if origen == "guia" else 1
    width = 512 if origen == "guia" else 1064
    height = 512 if origen == "guia" else 1064

    payload = {
        "prompt": prompt_en,   # SOLO en inglés para Stable Diffusion
        "negative_prompt": NEGATIVE_PROMPT,
        "steps": 28,
        "sampler_name": "DPM++ 2M",
        "cfg_scale": 7,
        "width": width,
        "height": height,
        "batch_size": batch_size
    }

    current_app.logger.info(f"📡 POST {STABLE_URL}/sdapi/v1/txt2img (batch={batch_size})")
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

        ficha_tecnica = generar_ficha_tecnica(tipo_prenda, atributos)
        costo = calcular_costo_prenda(tipo_prenda, atributos)

        doc = {
            "user_id": ObjectId(user_id),
            "tipo_prenda": tipo_prenda,
            "atributos": atributos,
            "prompt_es": prompt_es,  # para mostrar al cliente
            "prompt_en": prompt_en,  # para historial técnico
            "imageUrl": image_url,
            "ficha_tecnica": ficha_tecnica,
            "costo": costo,
            "estado": "generado"
        }
        inserted_id = guardar_prenda(doc)

        return {
            "id": inserted_id,
            "prompt": prompt_es,   # mostramos el español al cliente
            "prompt_en": prompt_en,
            "images": images,
            "imageUrl": image_url,
            "ficha_tecnica": ficha_tecnica,
            "costo": costo,
        }

    except Exception as e:
        return {"error": f"Error al generar imagen en Stable Diffusion: {str(e)}"}


# --------------------------------------
# Guardar prenda seleccionada desde Guia
# --------------------------------------
def guardar_prenda_seleccionada(user_id, prompt, image_base64, atributos):
    try:
        upload_result = cloudinary.uploader.upload(
            f"data:image/png;base64,{image_base64}",
            folder="prendasIA"
        )
        url = upload_result["secure_url"]

        doc = {
            "user_id": ObjectId(user_id),
            "prompt": prompt,
            "imageUrl": url,
            "atributos": atributos,
            "estado": "seleccionado"
        }
        prenda_id = guardar_prenda(doc)

        return {"ok": True, "id": prenda_id, "url": url}
    except Exception as e:
        return {"ok": False, "msg": str(e)}


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



# flask_api/controlador/control_ia_camiseta.py
import os, io, base64, requests
import cloudinary.uploader
from bson import ObjectId
from flask import current_app
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
from reportlab.lib.units import cm
from PIL import Image as PILImage

from flask_api.modelo.modelo_ia_camiseta import guardar_camiseta, listar_camisetas_db

NEGATIVO = (
    "cuerpo, humano, hombre, mujer, maniquí, brazos, manos, dedos, caras, modelo, extremidades, texto, logotipos"
)

# ---------------------------
# Prompt (ES)
# ---------------------------
def construir_prompt_es(atributos: dict) -> str:
    estilo = atributos.get("estilo", "deportiva")
    color1 = atributos.get("color1", "negra")
    patron = atributos.get("patron", "")              # p.ej. Rayas, Cuadros, Degradado, Textura
    color_patron = atributos.get("colorPatron", "")
    cuello = atributos.get("cuello", "")              # Redondo, En V, Polo
    manga = atributos.get("manga", "")                # Cortas, Largas

    partes = [
        f"Vista frontal centrada, maqueta de alta calidad de una camiseta {estilo.lower()} de color {color1.lower()}"
    ]
    if patron and color_patron:
        partes.append(f"con patrón de {patron.lower()} en color {color_patron.lower()}")
    if cuello:
        partes.append(f"con cuello {cuello.lower()}")
    if manga:
        partes.append(f"con mangas {manga.lower()}")

    partes.extend([
        "iluminación de estudio",
        "fondo blanco liso",
        "enfoque nítido",
        "sin texto",
        "sin logotipos",
        "solo la camiseta"
    ])
    return ", ".join(partes)

# ---------------------------
# Ficha técnica + costo
# ---------------------------
def generar_ficha_tecnica(atributos: dict) -> dict:
    return {
        "Tipo": "camiseta",
        "Estilo": atributos.get("estilo", ""),
        "Color principal": atributos.get("color1", ""),
        "Patrón": atributos.get("patron", "") or "Sin patrón",
        "Color del patrón": atributos.get("colorPatron", "") or "-",
        "Cuello": atributos.get("cuello", ""),
        "Manga": atributos.get("manga", ""),
    }

def calcular_costo_camiseta(atributos: dict) -> float:
    # Base
    costo = 5.0
    estilo = (atributos.get("estilo") or "").lower()
    patron = (atributos.get("patron") or "").lower()
    cuello = (atributos.get("cuello") or "").lower()
    manga = (atributos.get("manga") or "").lower()
    color_patron = (atributos.get("colorPatron") or "").lower()

    # Ajustes simples
    if estilo in ["deportiva", "urbana", "retro"]:  # estilos comunes
        costo += 1.0
    if patron and patron != "sin patrón":
        costo += 2.0
    if color_patron:
        costo += 0.5
    if cuello == "polo":
        costo += 1.5
    if manga == "largas":
        costo += 1.0

    return round(costo, 2)

# ---------------------------
# Llamada a A1111 (con fallback proxy gradio)
# ---------------------------
def _stable_txt2img(payload: dict):
    base = os.getenv("STABLE_URL", current_app.config.get("STABLE_URL", "http://127.0.0.1:7860")).rstrip("/")
    endpoints = [
        f"{base}/sdapi/v1/txt2img",
        f"{base}/proxy/sdapi/v1/txt2img",  # fallback típico en algunos gradio share
    ]
    last_err = None
    for url in endpoints:
        try:
            current_app.logger.info(f"📡 POST {url} (sampler={payload.get('sampler_name')}, batch={payload.get('batch_size')})")
            r = requests.post(url, json=payload, timeout=180)
            r.raise_for_status()
            return r.json()
        except Exception as e:
            last_err = e
            current_app.logger.warning(f"⚠️ Falla con {url}: {e}")
    raise last_err

# ---------------------------
# Generar imágenes (batch)
# ---------------------------
def generar_camiseta_batch(atributos: dict, batch_size: int = 4) -> dict:
    prompt = construir_prompt_es(atributos)
    payload = {
        "prompt": prompt,
        "negative_prompt": NEGATIVO,
        "steps": 28,
        "sampler_name": "DPM++ 2M",
        "width": 640,
        "height": 640,
        "cfg_scale": 7,
        "batch_size": batch_size,   # genera N imágenes
    }
    result = _stable_txt2img(payload)
    images = result.get("images", []) or []
    return {
        "prompt": prompt,
        "images": images,
    }

# ---------------------------
# PDF de ficha técnica
# ---------------------------
def generar_pdf_ficha(ficha: dict, imagen_b64: str | None = None, image_url: str | None = None) -> str:
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    elements = []
    styles = getSampleStyleSheet()
    elements.append(Paragraph("FICHA TÉCNICA - CAMISETA", styles["Heading1"]))
    elements.append(Spacer(1, 0.5 * cm))

    tabla_data = [["Campo", "Valor"]] + [[k, v if v else "-"] for k, v in ficha.items()]
    tabla = Table(tabla_data, colWidths=[6 * cm, 10 * cm])
    tabla.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.lightblue),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("ALIGN", (0, 0), (-1, -1), "LEFT"),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
    ]))
    elements.append(tabla)
    elements.append(Spacer(1, 0.8 * cm))

    img_io = None
    if imagen_b64:
        img_data = base64.b64decode(imagen_b64)
        img_io = io.BytesIO(img_data)
    elif image_url:
        resp = requests.get(image_url, stream=True, timeout=30)
        img_io = io.BytesIO(resp.content)

    if img_io:
        pil_img = PILImage.open(img_io)
        temp_io = io.BytesIO()
        pil_img.save(temp_io, format="JPEG")
        temp_io.seek(0)
        elements.append(Image(temp_io, width=10 * cm, height=10 * cm, kind="proportional"))

    doc.build(elements)
    buffer.seek(0)
    return base64.b64encode(buffer.read()).decode("utf-8")

# ---------------------------
# Guardar selección (Cloudinary + Mongo)
# ---------------------------
def guardar_seleccion(user_id: str, prompt: str, atributos: dict, image_b64: str) -> dict:
    # Subir imagen elegida
    upload = cloudinary.uploader.upload(
        f"data:image/png;base64,{image_b64}",
        folder="camisetasIA"
    )
    url = upload["secure_url"]

    # Ficha + costo (final)
    ficha = generar_ficha_tecnica(atributos)
    costo = calcular_costo_camiseta(atributos)

    doc = {
        "user_id": ObjectId(user_id),
        "tipo_prenda": "camiseta",
        "atributos": atributos,
        "prompt": prompt,
        "imageUrl": url,
        "ficha_tecnica": ficha,
        "costo": costo,
        "estado": "seleccionada"
    }
    inserted_id = guardar_camiseta(doc)
    return {"id": inserted_id, "url": url, "ficha_tecnica": ficha, "costo": costo}

# ---------------------------
# Listar guardadas
# ---------------------------
def listar_camisetas(user_id: str) -> list:
    return listar_camisetas_db(user_id)

# flask_api/controladores/control_prendas.py
import base64, io, requests
from bson import ObjectId
from bson.errors import InvalidId
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
from reportlab.lib.units import cm
from PIL import Image as PILImage
import cloudinary.uploader
from flask import current_app

from flask import jsonify
from flask_api.modelo.modelo_ia_prendas import guardar_prenda


NEGATIVE_PROMPT = "cuerpo, humano, hombre, mujer, maniquí, brazos, manos, dedos, caras, modelo, extremidades, texto, logotipos"

# ---------------------------
# Cálculo de costos
# ---------------------------
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

# ---------------------------
# Prompt dinámico
# ---------------------------
def generar_prompt(tipo_prenda, atributos):
    if tipo_prenda == "camiseta":
        estilo = atributos.get("estilo", "")
        color1 = atributos.get("color1", "")
        color2 = atributos.get("color2", "")
        cuello = atributos.get("cuello", "")
        manga = atributos.get("manga", "")

        prompt = f"""
        Vista frontal centrada, maqueta de alta calidad de una camiseta {estilo} de color {color1}
        con detalles de color {color2},
        cuello {cuello} y mangas {manga},
        iluminación de estudio, fondo blanco liso, enfoque nítido, sin texto, sin logotipos,
        solo la camiseta.
        """
        return " ".join(prompt.split())
    elif tipo_prenda == "pantalon":
        return f"Pantalón {atributos.get('color','')} de {atributos.get('tela','')} estilo {atributos.get('estilo','')}, vista frontal, fondo blanco"
    elif tipo_prenda == "chompa":
        return f"Chompa {atributos.get('color','')} de {atributos.get('tela','')} con capucha {atributos.get('capucha','')}, estilo catálogo"
    else:
        return f"Prenda genérica de tipo {tipo_prenda}, atributos: {atributos}"

# ---------------------------
# Ficha técnica
# ---------------------------
def generar_ficha_tecnica(tipo_prenda, atributos):
    return {
        "Tipo": tipo_prenda,
        "Estilo": atributos.get("estilo", ""),
        "Colores": f"{atributos.get('color1','')} {atributos.get('color2','')}".strip(),
        "Talla": atributos.get("talla", ""),
        "Tela": atributos.get("tela", ""),
        "Diseño": atributos.get("diseno", ""),
        "Género": atributos.get("genero", ""),
    }

# ---------------------------
# Generar imagen Stable Diffusion
# ---------------------------
def generar_imagen(tipo_prenda, atributos, user_id):
    STABLE_URL = current_app.config.get("STABLE_URL", "http://127.0.0.1:7860")
    prompt = generar_prompt(tipo_prenda, atributos)

    payload = {
        "prompt": prompt,
        "negative_prompt": NEGATIVE_PROMPT,
        "steps": 26,
        "width": 512,
        "height": 512,
    }

    try:
        response = requests.post(f"{STABLE_URL}/sdapi/v1/txt2img", json=payload, timeout=60)
        response.raise_for_status()
        r = response.json()
        image_base64 = r["images"][0]
    except Exception as e:
        return {"error": f"Error al generar imagen en Stable Diffusion: {str(e)}"}


    # Subir a Cloudinary
    image_data = base64.b64decode(image_base64)
    image_file = io.BytesIO(image_data)
    upload_result = cloudinary.uploader.upload(image_file, folder="prendasIA")
    image_url = upload_result.get("secure_url")

    if not atributos.get("color1"):
        atributos["color1"] = "blanco"
    if not atributos.get("talla"):
        atributos["talla"] = "M"    

    # Guardar en DB
    ficha_tecnica = generar_ficha_tecnica(tipo_prenda, atributos)
    costo = calcular_costo_prenda(tipo_prenda, atributos)

    doc = {
        "user_id": ObjectId(user_id),
        "tipo_prenda": tipo_prenda,
        "atributos": atributos,
        "prompt": prompt,
        "imageUrl": image_url,
        "ficha_tecnica": ficha_tecnica,
        "costo": costo,
        "estado": "generado"
    }
    inserted_id = guardar_prenda(doc)

    return {
        "id": inserted_id,
        "prompt": prompt,
        "imageUrl": image_url,
        "ficha_tecnica": ficha_tecnica,
        "costo": costo,
    }

# ---------------------------
# PDF ficha técnica
# ---------------------------
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

# flask_api/rutas/ruta_ia_prendas.py
from bson.errors import InvalidId
import base64, io, requests
from flask import Blueprint, current_app, request, jsonify
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
from reportlab.lib.units import cm
from PIL import Image as PILImage
from bson import ObjectId


ruta_ia_prendas = Blueprint("ruta_ia_prendas", __name__)

# URL del Automatic1111 con API habilitada
STABLE_URL = "http://127.0.0.1:7860"

# Negativos recomendados para moda y prendas
NEGATIVE_PROMPT = (
    "cuerpo, humano, hombre, mujer, maniquí, brazos, manos, "
    "dedos, caras, modelo, manos, extremidades, texto, logotipos"
)

# -------------------------------
# Calcular costo
# -------------------------------
def calcular_costo_prenda(tipo_prenda, atributos):
    base_costos = {
        "camiseta": 5.0,
        "pantalon": 8.0,
        "chompa": 12.0,
        "conjunto_interno": 15.0,
        "conjunto_externo": 20.0,
    }
    costo = base_costos.get(tipo_prenda, 10.0)

    # Ajustes simples
    tela = atributos.get("tela", "").lower()
    if tela == "poliéster":
        costo += 1
    elif tela == "algodón":
        costo += 2

    if atributos.get("diseno") in ["sublimado", "bordado"]:
        costo += 3

    return round(costo, 2)

# -------------------------------
# Generar PDF ficha técnica
# -------------------------------
@ruta_ia_prendas.route("/api/ia/ficha_tecnica", methods=["POST"])
def generar_ficha_pdf():
    try:
        data = request.get_json()
        ficha = data.get("ficha", {})
        imagen_b64 = data.get("imagen", "")

        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4)
        elements = []

        styles = getSampleStyleSheet()
        title_style = styles["Heading1"]
        normal = styles["Normal"]

        # --- Título ---
        elements.append(Paragraph("FICHA TÉCNICA DE PRENDA", title_style))
        elements.append(Spacer(1, 0.5*cm))

        # --- Tabla de atributos ---
        tabla_data = [[
            "Campo", "Valor"
        ]]
        for k, v in ficha.items():
            tabla_data.append([k, v if v else "-"])

        tabla = Table(tabla_data, colWidths=[6*cm, 10*cm])
        tabla.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.lightblue),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("ALIGN", (0, 0), (-1, -1), "LEFT"),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, 0), 12),
            ("BOTTOMPADDING", (0, 0), (-1, 0), 8),
            ("BACKGROUND", (0, 1), (-1, -1), colors.whitesmoke),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ]))
        elements.append(tabla)
        elements.append(Spacer(1, 1*cm))

        # --- Imagen generada ---
        if imagen_b64:
            img_data = base64.b64decode(imagen_b64)
            img_io = io.BytesIO(img_data)
            pil_img = PILImage.open(img_io)

            # Guardar como JPG temporal
            img_io = io.BytesIO()
            pil_img.save(img_io, format="JPEG")
            img_io.seek(0)

            elements.append(Paragraph("Imagen de la prenda generada:", styles["Heading2"]))
            elements.append(Spacer(1, 0.2*cm))
            elements.append(Image(img_io, width=10*cm, height=10*cm, kind="proportional"))

        # --- Generar PDF ---
        doc.build(elements)
        buffer.seek(0)
        pdf_b64 = base64.b64encode(buffer.read()).decode("utf-8")

        return jsonify({"ok": True, "pdf_base64": pdf_b64})

    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 500

# -------------------------------
# Generar imagen + ficha + costo
# -------------------------------
@ruta_ia_prendas.route("/api/ia/generar_prendas", methods=["POST"])
def generar_imagen_stable():
    try:
        data = request.get_json()
        tipo_prenda = data.get("tipo_prenda")
        atributos = data.get("atributos", {})
        user_id = data.get("userId")

        print("DEBUG Backend: userId recibido:", user_id, type(user_id))

        if not tipo_prenda:
            return jsonify({"error": "Falta el campo tipo_prenda"}), 400
        
        # Validar user_id (si quieres requerir login para guardar)
        if not user_id:
            # Si quieres permitir generación sin usuario, comenta la siguiente línea.
            return jsonify({"error": "Usuario no autenticado (userId faltante)"}), 401
        
        try:
            user_obj_id = ObjectId(user_id)
        except (InvalidId, TypeError) as e:
            print("DEBUG: userId inválido:", user_id, "error:", e)
            return jsonify({"error": "userId inválido", "recibido": user_id}), 400

        # Prompt dinámico
        prompt = generar_prompt(tipo_prenda, atributos)

        payload = {
            "prompt": prompt,
            "negative_prompt": NEGATIVE_PROMPT,
            "steps": 26,
            "width": 512,
            "height": 512
        }

        # Llamada a Stable Diffusion
        response = requests.post(f"{STABLE_URL}/sdapi/v1/txt2img", json=payload)
        r = response.json()
        image_base64 = r["images"][0]

        # Ficha técnica y costo
        ficha_tecnica = generar_ficha_tecnica(tipo_prenda, atributos)
        costo = calcular_costo_prenda(tipo_prenda, atributos)

        prendas = current_app.mongo.db.prendas
        doc = {
            "user_id": user_obj_id,
            "tipo_prenda": tipo_prenda,
            "atributos": atributos,
            "prompt": prompt,
            "imagen_b64": image_base64,
            "ficha_tecnica": ficha_tecnica,
            "costo": costo,
            "estado": "generado"
        }
        result = prendas.insert_one(doc)
        print("DEBUG: prenda insertada id:", str(result.inserted_id))


        return jsonify({
            "id": str(result.inserted_id),
            "prompt": prompt,
            "imagen": image_base64,
            "ficha_tecnica": ficha_tecnica,
            "costo": costo,
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# -------------------------------
# Prompt dinámico
# -------------------------------
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
        return f"Pantalón {atributos.get('color','')} de {atributos.get('tela','')} con estilo {atributos.get('estilo','')} y bolsillos {atributos.get('bolsillos','')}, vista frontal, fondo blanco, fotografía realista"

    elif tipo_prenda == "chompa":
        return f"Chompa {atributos.get('color','')} de {atributos.get('tela','')} con capucha {atributos.get('capucha','')}, cierre {atributos.get('cierre','')}, fondo neutro, estilo catálogo de moda"

    elif tipo_prenda == "conjunto_interno":
        return f"Conjunto deportivo interno {atributos.get('color','')} en talla {atributos.get('talla','')}, material {atributos.get('tela','')}, diseño ergonómico, fondo blanco, fotografía profesional"

    elif tipo_prenda == "conjunto_externo":
        return f"Conjunto deportivo externo {atributos.get('color','')} hecho de {atributos.get('tela','')}, incluye {atributos.get('piezas','')}, estilo moderno, fotografía estilo catálogo"

    else:
        return f"Prenda genérica de tipo {tipo_prenda}, atributos: {atributos}"

# -------------------------------
# Ficha técnica
# -------------------------------
def generar_ficha_tecnica(tipo_prenda, atributos):
    ficha = {
        "Tipo": tipo_prenda,
        "Estilo": atributos.get("estilo", ""),
        "Colores": f"{atributos.get('color1','')} {atributos.get('color2','')}".strip(),
        "Talla": atributos.get("talla", ""),
        "Tela": atributos.get("tela", ""),
        "Diseño": atributos.get("diseno", ""),
        "Género": atributos.get("genero", ""),
    }
    return ficha

import io, base64, requests
from datetime import datetime
from bson import ObjectId
from PIL import Image as PILImage
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, PageBreak
    
)
from flask_api.funciones.normalizar import _norm_cat
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics

from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import cm
from datetime import datetime
import io, requests
from PIL import Image as PILImage
from flask import current_app


from reportlab.lib.enums import TA_CENTER

from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from flask_api.componente.traducciones import (
    MAPEO_ATRIBUTOS_ES,
    TRADUCCION_BASICA_INVERSA)

FICHA_TECNICA_BASE = {
    "camiseta": [
        ("Tipo", "categoria_prd"),
        ("Estilo", "estilo"),
        ("Color principal", "color1"),
        ("Color secundario", "color2"),
        ("Diseño", "diseno"),
        ("Estilo avanzado", "estiloAvanzado"),
        ("Ubicación diseño", "ubicacion"),
        ("Detalles", "detalles"),
        ("Acabado", "acabado"),
        ("Cuello", "cuello"),
        ("Manga", "manga"),
        ("Tela", "tela"),
        ("Género", "genero"),
    ],
    "pantalon": [
        ("Tipo", "categoria_prd"),
        ("Estilo", "estilo"),
        ("Color principal", "color1"),
        ("Color secundario", "color2"),
        ("Diseño", "diseno"),
        ("Estilo avanzado", "estiloAvanzado"),
        ("Detalles", "detalles"),
        ("Acabado", "acabado"),
        ("Pretina", "pretina"),
        ("Ajuste", "ajuste"),
        ("Bolsillos", "bolsillos"),
        ("Tela", "tela"),
        ("Género", "genero"),
    ],
    "chompa": [
        ("Tipo", "categoria_prd"),
        ("Estilo", "estilo"),
        ("Color principal", "color1"),
        ("Color secundario", "color2"),
        ("Diseño", "diseno"),
        ("Estilo avanzado", "estiloAvanzado"),
        ("Detalles", "detalles"),
        ("Acabado", "acabado"),
        ("Cuello o Capucha", "cuelloCapucha"),
        ("Manga", "manga"),
        ("Tela", "tela"),
        ("Género", "genero"),
        ("Cierre", "cierre"),
        ("Capucha", "capucha"),
        ("Bolsillos", "bolsillos")
    ],
    "conjunto_interno": [
        ("Tipo", "categoria_prd"),
        ("Prenda superior", "camiseta"),
        ("Prenda inferior", "pantaloneta"),
        ("Cintura", "cintura"),
        ("Estilo", "estilo"),
        ("Color principal", "color1"),
        ("Color secundario", "color2"),
        ("Diseño", "diseno"),
        ("Estilo avanzado", "estiloAvanzado"),
        ("Detalles", "detalles"),
        ("Acabado", "acabado"),
        ("Tela", "tela"),
        ("Género", "genero"),
    ],
    "conjunto_externo": [
        ("Tipo", "categoria_prd"),
        ("Estilo", "estilo"),
        ("Color principal", "color1"),
        ("Color secundario", "color2"),
        ("Diseño", "diseno"),
        ("Estilo avanzado", "estiloAvanzado"),
        ("Acabado", "acabado"),
        ("Tela", "tela"),
        ("Género", "genero"),
        # Chompa
        ("Capucha", "capucha"),
        ("Cierre", "cierre"),
        ("Bolsillos chompa", "bolsillosChompa"),
        ("Detalles chompa", "detallesChompa"),
        # Pantalón
        ("Ajuste pantalón", "ajustePantalon"),
        ("Cintura pantalón", "cinturaPantalon"),
        ("Bolsillos pantalón", "bolsillosPantalon"),
        ("Detalles pantalón", "detallesPantalon"),
    ],
}


style_link = ParagraphStyle(
    "Link",
    fontSize=9,
    alignment=TA_CENTER,
    textColor="blue",
)

def linkify(url):
    if not url or url == "-":
        return "-"
    return Paragraph(f'<link href="{url}" color="blue">Ver imagen</link>', style_link)

# --------------------------------------
# Ficha técnica
# --------------------------------------
def generar_ficha_tecnica(categoria_prd, atributos):
    cat = _norm_cat(categoria_prd)

    # normalizamos alias igual que en generar_prompt
    alias = {
        "camiseta": "camiseta",
        "pantalon": "pantalon",
        "pantalón": "pantalon",
        "chompa": "chompa",
        "conjunto interno": "conjunto_interno",
        "conjunto_externo": "conjunto_externo",
    }
    cat = alias.get(cat, cat)

    campos = FICHA_TECNICA_BASE.get(cat, [])

    ficha = {}
    for etiqueta, clave in campos:
        valor = atributos.get(clave, "")
        if isinstance(valor, list):
            valor = ", ".join(valor) if valor else ""
        ficha[etiqueta] = valor or "-"
    return ficha

def construir_ficha_tecnica_detallada_ia(categoria, atributos_es, imagenes):
    descripcion = (
        f"Camiseta deportiva para {atributos_es.get('genero','unisex')}, "
        f"manga {atributos_es.get('manga','')}, "
        f"cuello {atributos_es.get('cuello','')}, "
        f"en {atributos_es.get('tela','')}, "
        f"diseño {atributos_es.get('diseno','')}, "
        f"colores {atributos_es.get('color1','')} {atributos_es.get('color2','')}"
    )

    caracteristicas = {
        "genero": atributos_es.get('genero','unisex'), 
        "manga": atributos_es.get('manga',''), 
        "cuello": atributos_es.get('cuello',''), 
        "tela": atributos_es.get('tela',''), 
        "diseno": atributos_es.get('diseno',''), 
        "color1": atributos_es.get('color1',''), 
        "color2": atributos_es.get('color2','')
    }

    ficha = {
        "categoria": categoria,
        "descripcion": descripcion,
        "caracteristicas": caracteristicas,
        "atributos": atributos_es,
        "imagenes": imagenes,
        "piezas": [
            {"pieza": "Delantera", "cantidad": 1, "color": atributos_es.get("color1","")},
            {"pieza": "Posterior", "cantidad": 1, "color": atributos_es.get("color2","")},
            {"pieza": "Mangas", "cantidad": 2, "color": atributos_es.get("color1","")},
            {"pieza": "Cuello", "cantidad": 1, "color": atributos_es.get("color2","")}
        ],
        "insumos": [
            {"descripcion": "Hilo 120", "cantidad": "1 rollo", "color": "a tono"},
            {"descripcion": "Etiqueta interior", "cantidad": "1", "color": "N/A"}
        ],
        "especificaciones": [
            "Costuras sin recogido",
            "Máquinas calibradas con igual puntada",
            "Delantera y posterior sublimadas"
        ]
    }
    return ficha



def construir_ficha_tecnica_detallada(categoria_prd: str, atributos: dict, image_urls: dict = None):

    hoy = datetime.now().strftime("%d/%m/%Y")
    categoria = categoria_prd.capitalize()

    # Modelo único (puedes cambiar lógica por contador en BD)
    codigo_modelo = f"{categoria[:2].upper()}-{hoy.replace('/', '')}-{str(ObjectId())[:4]}"

    # Características base comunes
    caracteristicas = {
        "tela": atributos.get("tela", "-"),
        "color": atributos.get("color1", "-"),
        "color_secundario": atributos.get("color2", "-"),
        "genero": atributos.get("genero", "-"),
        "estilo": atributos.get("estilo", "-"),
        "acabado": atributos.get("acabado", "-"),
        "estilo_avanzado": atributos.get("estiloAvanzado", "-"),
    }

    # Campos extra según tipo
    if categoria_prd == "camiseta":
        caracteristicas.update({
            "mangas": atributos.get("manga", "-"),
            "cuello": atributos.get("cuello", "-"),
            
        })
        piezas = [
            {"pieza": "Delantera", "cantidad": 1, "color": caracteristicas["color"]},
            {"pieza": "Posterior", "cantidad": 1, "color": caracteristicas["color"]},
            {"pieza": "Mangas", "cantidad": 2, "color": caracteristicas["color"]},
        ]

    elif categoria_prd == "pantalon":
        caracteristicas.update({
            "pretina": atributos.get("pretina", "-"),
            "ajuste": atributos.get("ajuste", "-"),
        })
        piezas = [
            {"pieza": "Delantera", "cantidad": 2, "color": caracteristicas["color"]},
            {"pieza": "Trasera", "cantidad": 2, "color": caracteristicas["color"]},
        ]

    elif categoria_prd == "chompa":
        caracteristicas.update({
            "cierre": atributos.get("cierre", "-"),
            "capucha": atributos.get("capucha", "-"),
            "mangas": atributos.get("manga", "-"),
        })
        piezas = [
            {"pieza": "Delantera", "cantidad": 1, "color": caracteristicas["color"]},
            {"pieza": "Posterior", "cantidad": 1, "color": caracteristicas["color"]},
            {"pieza": "Mangas", "cantidad": 2, "color": caracteristicas["color"]},
            {"pieza": "Capucha", "cantidad": 1, "color": caracteristicas["color_secundario"]},
        ]

    elif categoria_prd == "conjunto_interno":
        piezas = [
            {"pieza": "Camiseta delantera", "cantidad": 1, "color": caracteristicas["color"]},
            {"pieza": "Camiseta posterior", "cantidad": 1, "color": caracteristicas["color"]},
            {"pieza": "Pantaloneta", "cantidad": 1, "color": caracteristicas["color_secundario"]},
        ]

    elif categoria_prd == "conjunto_externo":
        piezas = [
            {"pieza": "Chompa delantera", "cantidad": 1, "color": caracteristicas["color"]},
            {"pieza": "Chompa posterior", "cantidad": 1, "color": caracteristicas["color"]},
            {"pieza": "Pantalón", "cantidad": 1, "color": caracteristicas["color_secundario"]},
        ]

    else:
        piezas = [{"pieza": "General", "cantidad": 1, "color": caracteristicas["color"]}]

    # Insumos base (puedes personalizar en BD)
    insumos = [
        {"descripcion": "Hilo poliéster 120", "cantidad": 1, "color": caracteristicas["color"]},
        {"descripcion": "Tela principal", "cantidad": "1.20 m", "color": caracteristicas["color"]},
    ]

    # Logo (si existe en atributos)
    logo = {}
    if "logo" in atributos:
        logo = {
            "imagen": atributos["logo"].get("url"),
            "tamano": atributos["logo"].get("tamano", "Mediano"),
            "ubicacion": atributos["logo"].get("ubicacion", "Frontal"),
            "estilo": atributos["logo"].get("estilo", "Sublimado"),
        }

    # Especificaciones generales
    especificaciones = [
        "Costuras reforzadas",
        "Acabados de alta calidad",
        "Prenda diseñada para uso deportivo",
    ]
    if atributos.get("detalles"):
        especificaciones.append(f"Detalles: {', '.join(atributos.get('detalles'))}")

    # Imagenes
    imagenes = image_urls or {}

    return {
        "categoria": categoria,
        "tipo": atributos.get("estilo", "-"),
        "modelo": codigo_modelo,
        "descripcion": f"{categoria} de {caracteristicas['tela']} color {caracteristicas['color']} con diseño {MAPEO_ATRIBUTOS_ES.get(atributos.get('diseno','-'), atributos.get('diseno','-'))}",
        "caracteristicas": caracteristicas,
        "imagenes": imagenes,
        "piezas": piezas,
        "insumos": insumos,
        "logo": logo,
        "especificaciones": especificaciones,
    }


def add_background(canvas, doc):
    canvas.saveState()
    canvas.setFillColor(colors.HexColor("#f0f6ff"))  # azul claro
    canvas.rect(0, 0, A4[0], A4[1], fill=1)
    canvas.restoreState()

def generar_ficha_tecnica_prueba(ficha: dict, return_elements=False):
    """
    Genera un PDF con layout detallado de ficha técnica basado en la estructura construida.
    Devuelve el PDF en base64 o lista de elementos si return_elements=True.
    """

    buffer = io.BytesIO()
    elements = []

    styles = getSampleStyleSheet()
    title = ParagraphStyle("Titulo", parent=styles["Heading1"],
                           alignment=1, fontSize=16,
                           textColor=colors.HexColor("#0a2e6c"))
    subtitle = ParagraphStyle("Subtitulo", parent=styles["Heading2"],
                              textColor=colors.HexColor("#0a2e6c"))
    normal = ParagraphStyle("Normal", parent=styles["Normal"],
                            fontSize=12, textColor=colors.black)

    # -----------------------------
    # Normalizar caracteristicas
    # -----------------------------
    caracteristicas = ficha.get("caracteristicas", {}).copy()

    # Unificar talla
    if ficha.get("talla"):
        caracteristicas["talla"] = ficha["talla"]

    # Agregar modelo y categoría
    if ficha.get("modelo"):
        caracteristicas["modelo"] = ficha["modelo"]
    if ficha.get("categoria"):
        caracteristicas["categoria"] = ficha["categoria"]

    # -----------------------------
    # Logo empresa
    # -----------------------------
    try:
        logo_url = "https://res.cloudinary.com/dcn5d4wbo/image/upload/v1759365264/LogoHori_eb7nnz.png"
        resp = requests.get(logo_url, stream=True)
        img_io = io.BytesIO(resp.content)
        pil_img = PILImage.open(img_io)
        temp_io = io.BytesIO()
        pil_img.save(temp_io, format="PNG")
        temp_io.seek(0)
        elements.append(Image(temp_io, width=30*cm, height=7*cm))
        elements.append(Spacer(10, 1*cm))
    except Exception:
        pass

    # =====================
    # PORTADA
    # =====================
    elements.append(Paragraph("FICHA TÉCNICA DE PRENDA", title))
    elements.append(Spacer(1, 0.5*cm))
    elements.append(Paragraph(f"<b>Categoría:</b> {ficha.get('categoria','-')}", normal))
    elements.append(Paragraph(f"<b>Modelo:</b> {ficha.get('modelo','-')}", normal))
    elements.append(Paragraph(f"<b>Descripción:</b> {ficha.get('descripcion','-')}", normal))
    elements.append(Spacer(1, 0.8*cm))

    # Imagen principal (acabado si existe)
    if ficha.get("imagenes", {}).get("acabado"):
        try:
            resp = requests.get(ficha["imagenes"]["acabado"], stream=True)
            img_io = io.BytesIO(resp.content)
            pil_img = PILImage.open(img_io)
            temp_io = io.BytesIO()
            pil_img.save(temp_io, format="JPEG")
            temp_io.seek(0)
            elements.append(Image(temp_io, width=10*cm, height=10*cm, kind="proportional"))
            elements.append(Spacer(1, 1*cm))
        except Exception:
            pass

    elements.append(PageBreak())

    # =====================
    # CARACTERÍSTICAS
    # =====================
    elements.append(Paragraph("CARACTERÍSTICAS", subtitle))
    data = [["Campo", "Valor"]]
    for k, v in caracteristicas.items():
        data.append([k.capitalize(), v if v else "-"])
    tabla = Table(data, colWidths=[6*cm, 10*cm])
    tabla.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0a2e6c")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.whitesmoke, colors.lightgrey]),
        ("FONTNAME", (0, 0), (-1, -1), "Helvetica-Bold"),
    ]))
    elements.append(tabla)
    elements.append(Spacer(1, 1*cm))

    # =====================
    # COSTOS
    # =====================
    if ficha.get("costo"):
        elements.append(Paragraph("COSTOS", subtitle))
        data = [["Concepto", "Valor (USD)"]]
        costo = ficha["costo"]
        for k, v in costo.items():
            data.append([k.replace("_", " ").capitalize(), f"${v:.2f}"])
        # Opcional: precios derivados
        if "total" in costo:
            data.append(["Precio Venta", f"${costo['total']*1.5:.2f}"])
            data.append(["Precio Mayor", f"${costo['total']*1.2:.2f}"])
        tabla = Table(data, colWidths=[8*cm, 6*cm])
        tabla.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0a2e6c")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.whitesmoke, colors.lightgrey]),
            ("FONTNAME", (0, 0), (-1, -1), "Helvetica-Bold"),
        ]))
        elements.append(tabla)
        elements.append(Spacer(1, 1*cm))

    # =====================
    # PIEZAS
    # =====================
    elements.append(Paragraph("PIEZAS", subtitle))
    data = [["Pieza", "Cantidad", "Color"]]
    for pieza in ficha.get("piezas", []):
        data.append([pieza.get("pieza","-"), pieza.get("cantidad","-"), pieza.get("color","-")])
    tabla = Table(data, colWidths=[8*cm, 3*cm, 5*cm])
    tabla.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0a2e6c")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.whitesmoke, colors.lightgrey]),
        ("FONTNAME", (0, 0), (-1, -1), "Helvetica-Bold"),
    ]))
    elements.append(tabla)
    elements.append(Spacer(1, 1*cm))

    # =====================
    # INSUMOS
    # =====================
    elements.append(Paragraph("INSUMOS", subtitle))
    data = [["Descripción", "Cantidad", "Color"]]
    for ins in ficha.get("insumos", []):
        data.append([ins.get("descripcion","-"), str(ins.get("cantidad","-")), ins.get("color","-")])
    tabla = Table(data, colWidths=[8*cm, 3*cm, 5*cm])
    tabla.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0a2e6c")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.whitesmoke, colors.lightgrey]),
        ("FONTNAME", (0, 0), (-1, -1), "Helvetica-Bold"),
    ]))
    elements.append(tabla)
    elements.append(Spacer(1, 1*cm))

    # =====================
    # LOGO
    # =====================
    if ficha.get("logo", {}).get("imagen"):
        elements.append(Paragraph("LOGO", subtitle))
        try:
            resp = requests.get(ficha["logo"]["imagen"], stream=True)
            img_io = io.BytesIO(resp.content)
            pil_img = PILImage.open(img_io)
            temp_io = io.BytesIO()
            pil_img.save(temp_io, format="JPEG")
            temp_io.seek(0)
            elements.append(Image(temp_io, width=5*cm, height=5*cm, kind="proportional"))
            elements.append(Spacer(1, 0.5*cm))
        except Exception:
            pass
        elements.append(Paragraph(f"Tamaño: {ficha['logo'].get('tamano','-')}", normal))
        elements.append(Paragraph(f"Ubicación: {ficha['logo'].get('ubicacion','-')}", normal))
        elements.append(Paragraph(f"Estilo: {ficha['logo'].get('estilo','-')}", normal))
        elements.append(Spacer(1, 1*cm))

    # =====================
    # ESPECIFICACIONES
    # =====================
    elements.append(Paragraph("ESPECIFICACIONES", subtitle))
    for esp in ficha.get("especificaciones", []):
        elements.append(Paragraph(f"- {esp}", normal))
    elements.append(Spacer(1, 1*cm))

    # =====================
    # PLANO DEL DISEÑO
    # =====================
    elements.append(Paragraph("PLANO DEL DISEÑO", subtitle))
    imagenes = ficha.get("imagenes", {})
    fila_imgs, titulos = [], []
    for nombre in ["delantera", "posterior", "acabado"]:
        url = imagenes.get(nombre)
        if not url:
            continue
        try:
            resp = requests.get(url, stream=True)
            img_io = io.BytesIO(resp.content)
            pil_img = PILImage.open(img_io)
            temp_io = io.BytesIO()
            pil_img.save(temp_io, format="PNG")
            temp_io.seek(0)
            fila_imgs.append(Image(temp_io, width=6*cm, height=6*cm, kind="proportional"))
            titulos.append(Paragraph(nombre.capitalize(), normal))
        except Exception:
            pass
    if fila_imgs:
        elements.append(Table([fila_imgs], colWidths=[6*cm]*len(fila_imgs)))
        elements.append(Table([titulos], colWidths=[6*cm]*len(titulos)))
        elements.append(Spacer(1, 1*cm))

    # =====================
    # SALIDA
    # =====================
    if return_elements:
        return elements

    doc = SimpleDocTemplate(buffer, pagesize=A4)
    doc.build(elements, onFirstPage=add_background, onLaterPages=add_background)
    buffer.seek(0)
    pdf_b64 = base64.b64encode(buffer.read()).decode("utf-8")
    return pdf_b64


def generar_ficha_tecnica_3d(prenda_data):
    """
    Genera la ficha técnica PDF de un diseño 3D.
    Recibe el mismo objeto que se guardó en MongoDB (prendas_3d).
    """
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    elementos = []
    styles = getSampleStyleSheet()

    titulo = f"FICHA TÉCNICA - {prenda_data.get('categoria', '').upper()}"
    subtitulo = f"Modelo: {prenda_data.get('modelo', '')}   |   Fecha: {datetime.now().strftime('%d/%m/%Y')}"

    # =======================
    # 🧷 PORTADA PRINCIPAL
    # =======================
    elementos.append(Paragraph(titulo, styles["Title"]))
    elementos.append(Spacer(1, 6))
    elementos.append(Paragraph(subtitulo, styles["Normal"]))
    elementos.append(Spacer(1, 12))

    # 📸 Imagen principal (vista de frente)
    renders = prenda_data.get("renders", {})
    render_frente = renders.get("render_frente")


    if render_frente:
        try:
            response = requests.get(render_frente, stream=True)
            img_io = io.BytesIO(response.content)
            pil_img = PILImage.open(img_io)
            temp_io = io.BytesIO()
            pil_img.save(temp_io, format="PNG")
            temp_io.seek(0)
            elementos.append(Image(temp_io, width=13*cm, height=13*cm))
            elementos.append(Spacer(1, 12))
        except Exception as e:
            elementos.append(Paragraph(f"No se pudo cargar la vista frontal: {e}", styles["Italic"]))

    # =====================================================
    # 🎨 Tabla de Colores y Texturas
    # =====================================================
    colors_data = prenda_data.get("colors", {})
    textures_data = prenda_data.get("textures", {})

    tabla_colores = [["Zona", "Color", "Textura"]]
    for zona, color in colors_data.items():
        textura = textures_data.get(zona) or "-"
        tabla_colores.append([zona.capitalize(), color, linkify(textura)])

    tabla_colores_estilo = Table(tabla_colores, colWidths=[4*cm, 4*cm, 7*cm])
    tabla_colores_estilo.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#004488")),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('GRID', (0,0), (-1,-1), 0.5, colors.grey),
        ('BACKGROUND', (0,1), (-1,-1), colors.whitesmoke),
    ]))
    elementos.append(Paragraph("Colores y Texturas", styles["Heading2"]))
    elementos.append(tabla_colores_estilo)
    elementos.append(Spacer(1, 12))

    # =====================================================
    # 🧾 Logos y Textos
    # =====================================================
    decals = prenda_data.get("decals", [])
    textDecals = prenda_data.get("textDecals", [])

    if decals:
        elementos.append(Paragraph("Logos", styles["Heading2"]))
        for idx, d in enumerate(decals, start=1):
            data_logo = [
                ["Logo", linkify(d.get("url", "-"))],
                ["Posición", str(d.get("position", "-"))],
                ["Escala", d.get("scale", "-")],
                ["Rotación", d.get("rotationZ", "-")],
            ]
            tabla_logo = Table(data_logo, colWidths=[3 * cm, 12 * cm])
            tabla_logo.setStyle(TableStyle([
                ('GRID', (0,0), (-1,-1), 0.5, colors.grey),
                ('BACKGROUND', (0,0), (0,-1), colors.HexColor("#004488")),
                ('TEXTCOLOR', (0,0), (0,-1), colors.white),
                ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
                ('ALIGN', (1,0), (-1,-1), 'LEFT'),
            ]))
            elementos.append(Paragraph(f"Logo {idx}", styles["Heading3"]))
            elementos.append(tabla_logo)
            elementos.append(Spacer(1, 8))

    if textDecals:
        elementos.append(Paragraph("Textos", styles["Heading2"]))
        for idx, t in enumerate(textDecals, start=1):
            data_texto = [
                ["Texto", t.get("text", "-")],
                ["Posición", str(t.get("position", "-"))],
                ["Escala", t.get("scale", "-")],
                ["Rotación", t.get("rotationZ", "-")],
            ]
            tabla_texto = Table(data_texto, colWidths=[3 * cm, 12 * cm])
            tabla_texto.setStyle(TableStyle([
                ('GRID', (0,0), (-1,-1), 0.5, colors.grey),
                ('BACKGROUND', (0,0), (0,-1), colors.HexColor("#004488")),
                ('TEXTCOLOR', (0,0), (0,-1), colors.white),
                ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
                ('ALIGN', (1,0), (-1,-1), 'LEFT'),
            ]))
            elementos.append(Paragraph(f"Texto {idx}", styles["Heading3"]))
            elementos.append(tabla_texto)
            elementos.append(Spacer(1, 8))

    # =====================================================
    # 🧵 Vistas del diseño (acabados)
    # =====================================================
    if renders:
        elementos.append(Paragraph("Vistas del diseño (acabados)", styles["Heading2"]))
        fila = []
        for key in ["render_frente", "render_espalda", "render_lado_izq", "render_lado_der"]:
            url = renders.get(key)
            if not url:
                continue
            try:
                resp = requests.get(url, stream=True)
                img_io = io.BytesIO(resp.content)
                pil_img = PILImage.open(img_io)
                temp_io = io.BytesIO()
                pil_img.save(temp_io, format="PNG")
                temp_io.seek(0)
                fila.append(Image(temp_io, width=9*cm, height=9*cm, kind="proportional"))
            except Exception as e:
                elementos.append(Paragraph(f"Error cargando {key}: {e}", styles["Normal"]))
        if fila:
            elementos.append(Table([fila], colWidths=[9*cm]*len(fila), hAlign="CENTER"))
            elementos.append(Spacer(1, 12))

    # =====================================================
    # 🧶 Plano de sublimación
    # =====================================================

    plano_sublimacion_url = prenda_data.get("plano_sublimacion_url")
    if plano_sublimacion_url:
        elementos.append(Paragraph("Plano base de color (sublimación)", styles["Heading2"]))
        try:
            resp = requests.get(plano_sublimacion_url, timeout=10)
            if resp.status_code == 200:
                img_io = io.BytesIO(resp.content)
                pil_img = PILImage.open(img_io).convert("RGB")

                # 🔧 Ajustar tamaño al ancho útil del PDF (A4 con márgenes)
                max_width = 16 * cm
                aspect_ratio = pil_img.width / pil_img.height
                new_height = max_width / aspect_ratio
                if new_height > 16 * cm:
                    new_height = 16 * cm
                    max_width = new_height * aspect_ratio

                temp_io = io.BytesIO()
                pil_img.save(temp_io, format="PNG")
                temp_io.seek(0)

                elementos.append(Image(temp_io, width=max_width, height=new_height))
                elementos.append(Spacer(1, 0.5 * cm))
            else:
                elementos.append(Paragraph("⚠️ No se pudo cargar el plano (respuesta inválida).", styles["Normal"]))
        except Exception as e:
            elementos.append(Paragraph(f"⚠️ Error cargando plano: {str(e)}", styles["Normal"]))
    else:
        elementos.append(Paragraph("No se encontró la imagen de sublimación.", styles["Normal"]))
    # =====================================================
    # 📋 Datos generales
    # =====================================================
    info = [
        ["Categoría", prenda_data.get("categoria", "-")],
        ["Modelo", prenda_data.get("modelo", "-")],
        ["Diseño base", prenda_data.get("design_id", "-")],
        ["Usuario", str(prenda_data.get("user_id", "-"))],
    ]

    tabla_info = Table(info, colWidths=[5*cm, 10*cm])
    tabla_info.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (0,-1), colors.HexColor("#004488")),
        ('TEXTCOLOR', (0,0), (0,-1), colors.white),
        ('GRID', (0,0), (-1,-1), 0.25, colors.grey),
    ]))
    elementos.append(Paragraph("Información General", styles["Heading2"]))
    elementos.append(tabla_info)

    # =====================================================
    # 📄 Generar PDF
    # =====================================================
    doc.build(elementos)
    pdf_bytes = buffer.getvalue()
    buffer.close()
    return pdf_bytes

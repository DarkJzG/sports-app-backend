import io
import base64
import requests
from datetime import datetime
from bson import ObjectId
from PIL import Image as PILImage

from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    Image,
    PageBreak,
)
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

from flask import current_app

from flask_api.funciones.normalizar import _norm_cat
from flask_api.componente.traducciones import (
    MAPEO_ATRIBUTOS_ES,
    TRADUCCION_BASICA_INVERSA,
)

# ============================================================
# CONFIGURACIÓN BASE DE CAMPOS (MODOS SIMPLES / LEGACY)
# ============================================================

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
        ("Bolsillos", "bolsillos"),
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

# ============================================================
# TABLAS DE TELA NECESARIA Y TABLAS DE TALLAS POR PRENDA
# ============================================================

TELA_NECESARIA = {
    "camiseta": {
        "titulo": "Tela necesaria por talla (Camiseta)",
        "header": ["Talla", "Manga corta", "Manga larga"],
        "rows": [
            ["S",  "1.00 m", "1.20 m"],
            ["M",  "1.10 m", "1.30 m"],
            ["L",  "1.20 m", "1.40 m"],
            ["XL", "1.30 m", "1.50 m"],
            ["XXL","1.40 m", "1.60 m"],
        ],
    },
    "pantaloneta": {
        "titulo": "Tela necesaria por talla (Pantaloneta)",
        "header": ["Talla", "Pantaloneta"],
        "rows": [
            ["S",  "0.50 m"],
            ["M",  "0.55 m"],
            ["L",  "0.60 m"],
            ["XL", "0.65 m"],
            ["XXL","0.65 m"],
        ],
    },
    "pantalon": {
        "titulo": "Tela necesaria por talla (Pantalón deportivo)",
        "header": ["Talla", "Pantalón deportivo"],
        "rows": [
            ["S",  "1.20 m"],
            ["M",  "1.20 m"],
            ["L",  "1.25 m"],
            ["XL", "1.30 m"],
            ["XXL","1.30 m"],
        ],
    },
    "chompa": {
        "titulo": "Tela necesaria por talla (Chompa / Buzo)",
        "header": ["Talla", "Chompa / Buzo"],
        "rows": [
            ["S",  "1.50 m"],
            ["M",  "1.55 m"],
            ["L",  "1.60 m"],
            ["XL", "1.65 m"],
            ["XXL","1.65 m"],
        ],
    },
}

TABLAS_TALLAS = {
    "camiseta": {
        "titulo": "Tabla de tallas - Camiseta",
        "header": ["Descripción", "S", "M", "L", "XL", "XXL"],
        "rows": [
            ["Ancho camiseta cm",      "50", "52", "54", "56", "58"],
            ["Espalda cm",             "40", "42", "44", "46", "48"],
            ["Largo camiseta cm",      "65", "68", "70", "74", "76"],
            ["Largo manga x ancho cm",  "20x36", "21x38", "22x40", "23x42", "24x44"],
        ],
    },
    "chompa": {
        "titulo": "Tabla de tallas - Chompa",
        "header": ["Descripción", "S", "M", "L", "XL", "XXL"],
        "rows": [
            ["Ancho chompa cm",        "53", "56", "58", "60", "62"],
            ["Espalda cm",             "42", "44", "46", "48", "50"],
            ["Largo chompa cm",        "62", "65", "68", "70", "72"],
            ["Largo manga x ancho cm",  "62x26", "64x28", "65x29", "66x30", "67x31"],
        ],
    },
    "pantalon": {
        "titulo": "Tabla de tallas - Pantalón",
        "header": ["Descripción", "S", "M", "L", "XL", "XXL"],
        "rows": [
            ["Cintura cm",      "50", "54", "56", "58", "60"],
            ["Cadera cm",       "80", "84", "90", "100", "112"],
            ["Largo total cm",  "94", "100", "104", "106", "110"],
            ["Entrepierna cm",  "66", "70", "73", "76", "82"],
            ["Basta cm",        "19", "20", "20", "22", "22"],
        ],
    },
    "pantaloneta": {
        "titulo": "Tabla de tallas - Pantaloneta",
        "header": ["Descripción", "S", "M", "L", "XL", "XXL"],
        "rows": [
            ["Cintura cm",      "33", "35", "37", "39", "41"],
            ["Cadera cm",       "50", "54", "58", "62", "66"],
            ["Largo total cm",  "40", "42", "44", "46", "48"],
            ["Entrepierna cm",  "10", "12", "14", "16", "18"],
            ["Basta cm",        "28", "30", "32", "34", "36"],
        ],
    },
    
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


# ============================================================
# FICHA SIMPLE (LEGACY)
# ============================================================

def generar_ficha_tecnica(categoria_prd, atributos):
    cat = _norm_cat(categoria_prd)

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


def construir_ficha_tecnica_detallada(
    categoria_prd: str,
    atributos: dict,
    image_urls: dict = None,
):
    """
    Construye una ficha técnica detallada unificada para:
    - camiseta
    - pantalon
    - pantaloneta
    - chompa
    - conjunto_interno
    - conjunto_externo

    Usando los atributos reales que vienen del frontend (atributos_es).
    1) Calcula colores, piezas, insumos, etc.
    2) Agrega TODOS los atributos_es como características (omitiendo vacíos
       y algunos campos técnicos como userId, ids, etc.).
    """

    # ----------------------------
    # Normalizar categoría
    # ----------------------------
    cat_norm = _norm_cat(categoria_prd or "")

    alias = {
        "camiseta": "camiseta",
        "pantalon": "pantalon",
        "pantalón": "pantalon",
        "pantaloneta": "pantaloneta",
        "chompa": "chompa",
        "conjunto interno": "conjunto_interno",
        "conjunto_externo": "conjunto_externo",
    }
    cat_slug = alias.get(cat_norm, cat_norm or "prenda")
    categoria_titulo = cat_slug.replace("_", " ").title()

    codigo_modelo = _build_codigo_modelo(cat_slug)
    camino = atributos.get("caminoSeleccionado")

    # ----------------------------------------------------
    # COLORES (igual que antes)
    # ----------------------------------------------------
    color_principal = "-"
    color_secundario = "-"

    if cat_slug in ("camiseta", "chompa", "conjunto_interno", "conjunto_externo"):
        color_principal = (
            atributos.get("color1")
            or atributos.get("colorBase")
            or atributos.get("colorBasePanel")
            or atributos.get("colorBaseMixto")
            or "-"
        )
        color_secundario = (
            atributos.get("color2")
            or atributos.get("colorAcentos")
            or atributos.get("colorPanel")
            or "-"
        )

    elif cat_slug in ("pantalon", "pantaloneta"):
        if camino in ("solid", "solido"):
            color_principal = atributos.get("colorBase", "-")
            color_secundario = atributos.get("colorAcentos", "-")

        elif camino in ("panels", "paneles"):
            color_principal = atributos.get("colorBasePanel") or atributos.get("colorBase", "-")
            colores_bloque = atributos.get("coloresBloque")
            if isinstance(colores_bloque, list) and colores_bloque:
                color_secundario = ", ".join(colores_bloque)
            else:
                color_secundario = atributos.get("colorPanel", "-")

        elif camino in ("sublimation", "sublimacion"):
            color_principal = (
                atributos.get("colorBaseMixto")
                or atributos.get("colorBase")
                or atributos.get("colorBasePanel")
                or "-"
            )

            if isinstance(atributos.get("coloresGradiente"), list) and atributos["coloresGradiente"]:
                color_secundario = ", ".join(atributos["coloresGradiente"])
            elif isinstance(atributos.get("coloresArtistico"), list) and atributos["coloresArtistico"]:
                color_secundario = ", ".join(atributos["coloresArtistico"])
            else:
                color_secundario = (
                    atributos.get("colorAcentos")
                    or atributos.get("colorPanel")
                    or "-"
                )
        else:
            color_principal = (
                atributos.get("colorBase")
                or atributos.get("colorBasePanel")
                or atributos.get("color1")
                or "-"
            )
            color_secundario = (
                atributos.get("colorAcentos")
                or atributos.get("colorPanel")
                or atributos.get("color2")
                or "-"
            )
    else:
        color_principal = (
            atributos.get("color1")
            or atributos.get("colorBase")
            or atributos.get("colorBasePanel")
            or "-"
        )
        color_secundario = (
            atributos.get("color2")
            or atributos.get("colorAcentos")
            or atributos.get("colorPanel")
            or "-"
        )

    # ----------------------------------------------------
    # ESTILO base
    # ----------------------------------------------------
    estilo = atributos.get("estilo")
    if not estilo:
        if cat_slug == "pantalon":
            estilo = atributos.get("tipoCorte")
        elif cat_slug == "pantaloneta":
            estilo = atributos.get("largo")
    estilo = estilo or "-"

    # ----------------------------------------------------
    # CARACTERÍSTICAS BASE (claves más importantes)
    # ----------------------------------------------------
    caracteristicas = {
        "Tela": atributos.get("tela", "-"),
        "Color base": color_principal,
        "Color secundario": color_secundario,
        "Género": atributos.get("genero", "-"),
        "Estilo": estilo,
        "Acabado": atributos.get("acabado", "-"),
        "Estilo avanzado": atributos.get("estiloAvanzado", "-"),
    }

    # Campos extra por tipo
    if cat_slug == "camiseta":
        caracteristicas.update(
            {
                "Manga": atributos.get("manga", "-"),
                "Cuello": atributos.get("cuello", "-"),
            }
        )
        piezas = [
            {"pieza": "Delantera", "cantidad": 1, "color": "A tono"},
            {"pieza": "Posterior", "cantidad": 1, "color": "A tono"},
            {"pieza": "Mangas", "cantidad": 2, "color": "A tono"},
        ]

    elif cat_slug == "pantalon":
        caracteristicas.update(
            {
                "Tipo de corte": atributos.get("tipoCorte", "-"),
                "Tipo de tobillo": atributos.get("tipoTobillo", "-"),
                "Bolsillos": atributos.get("bolsillos", "-"),
            }
        )
        piezas = [
            {"pieza": "Delantera izquierda", "cantidad": 1, "color": "A tono"},
            {"pieza": "Delantera derecha", "cantidad": 1, "color": "A tono"},
            {"pieza": "Trasera izquierda", "cantidad": 1, "color": "A tono"},
            {"pieza": "Trasera derecha", "cantidad": 1, "color": "A tono"},
        ]

    elif cat_slug == "pantaloneta":
        caracteristicas.update(
            {
                "Largo": atributos.get("largo", "-"),
                "Bolsillos": atributos.get("bolsillos", "-"),
                "Cordón": atributos.get("cordon", "-"),
            }
        )
        piezas = [
            {"pieza": "Delantera izquierda", "cantidad": 1, "color": "A tono"},
            {"pieza": "Delantera derecha", "cantidad": 1, "color": "A tono"},
            {"pieza": "Trasera izquierda", "cantidad": 1, "color": "A tono"},
            {"pieza": "Trasera derecha", "cantidad": 1, "color": "A tono"},
            {"pieza": "Pretina", "cantidad": 1, "color": "A tono"},
        ]

    elif cat_slug == "chompa":
        caracteristicas.update(
            {
                "Cierre": atributos.get("cierre", "-"),
                "Capucha": atributos.get("capucha", "-"),
                "Mangas": atributos.get("manga", "-"),
            }
        )
        piezas = [
            {"pieza": "Delantera", "cantidad": 1, "color": "A tono"},
            {"pieza": "Posterior", "cantidad": 1, "color": "A tono"},
            {"pieza": "Mangas", "cantidad": 2, "color": "A tono"},
            {"pieza": "Capucha", "cantidad": 1, "color": "A tono"},
        ]

    elif cat_slug == "conjunto_interno":
        piezas = [
            {"pieza": "Camiseta delantera", "cantidad": 1, "color": "A tono"},
            {"pieza": "Camiseta posterior", "cantidad": 1, "color": "A tono"},
            {"pieza": "Pantaloneta", "cantidad": 1, "color": "A tono"},
        ]

    elif cat_slug == "conjunto_externo":
        piezas = [
            {"pieza": "Chompa delantera", "cantidad": 1, "color": "A tono"},
            {"pieza": "Chompa posterior", "cantidad": 1, "color": "A tono"},
            {"pieza": "Pantalón", "cantidad": 1, "color": "A tono"},
        ]

    else:
        piezas = [
            {"pieza": "General", "cantidad": 1, "color": "A tono"},
        ]

    # ----------------------------------------------------
    # INSUMOS BASE
    # ----------------------------------------------------
    insumos = [
        {"descripcion": "Hilo poliéster 120", "cantidad": "Varios", "color": "A tono"},
    ]

    

    # ----------------------------------------------------
    # LOGO (si existe)
    # ----------------------------------------------------
    logo = {}
    if "logo" in atributos and isinstance(atributos["logo"], dict):
        logo = {
            "imagen": atributos["logo"].get("url"),
            "tamano": atributos["logo"].get("tamano", "Mediano"),
            "ubicacion": atributos["logo"].get("ubicacion", "Frontal"),
            "estilo": atributos["logo"].get("estilo", "Sublimado"),
        }

    # ----------------------------------------------------
    # ESPECIFICACIONES
    # ----------------------------------------------------
    especificaciones = [
        "Costuras reforzadas",
        "Acabados de alta calidad",
        "Prenda diseñada para uso deportivo",
    ]
    if atributos.get("detalles"):
        det = atributos.get("detalles")
        if isinstance(det, list):
            especificaciones.append(f"Detalles: {', '.join(det)}")
        else:
            especificaciones.append(f"Detalles: {det}")

    imagenes = image_urls or {}

    # ----------------------------------------------------
    # ➕ AGREGAR TODOS LOS ATRIBUTOS_ES RESTANTES COMO CARACTERÍSTICAS
    # ----------------------------------------------------
    claves_ignoradas = {
        "userId",
        "user_id",
        "categoria_id",
        "categoria_prd",
        "imageUrl",
        "imagen",
        "prompt_en",
        "descripcion",
        "_id",
        "estado",
        "ficha_id",
    }

    # atributos ya representados explícitamente en caracteristicas
    atributos_usados = {
        "tela",
        "color1",
        "color2",
        "colorBase",
        "colorBaseMixto",
        "colorBasePanel",
        "colorAcentos",
        "colorPanel",
        "genero",
        "estilo",
        "estiloAvanzado",
        "acabado",
        "manga",
        "cuello",
        "tipoCorte",
        "tipoTobillo",
        "bolsillos",
        "largo",
        "cordon",
        "cierre",
        "capucha",
    }

    

    for key, value in atributos.items():
        if key in claves_ignoradas or key in atributos_usados:
            continue

        if value is None:
            continue
        if isinstance(value, str) and not value.strip():
            continue
        if isinstance(value, (list, dict)) and not value:
            continue

        if isinstance(value, list):
            value = ", ".join(str(v) for v in value if v)

        etiqueta = MAPEO_ATRIBUTOS_ES.get(key, key)
        # Evitar pisar claves ya existentes (ej. Tela, Género, etc.)
        if etiqueta in caracteristicas:
            continue

        caracteristicas[etiqueta] = value

    # ----------------------------------------------------
    # DESCRIPCIÓN BASE (la IA la sobreescribe luego si quieres)
    # ----------------------------------------------------
    diseno_raw = atributos.get("diseno")
    if not diseno_raw:
        if camino in ("solid", "solido"):
            diseno_raw = "solid"
        elif camino in ("panels", "paneles"):
            diseno_raw = "paneles"
        elif camino in ("sublimation", "sublimacion"):
            diseno_raw = atributos.get("tipoDisenoIA", "sublimado")

    diseno_legible = "-"
    if diseno_raw:
        diseno_legible = MAPEO_ATRIBUTOS_ES.get(diseno_raw, diseno_raw)

    descripcion = (
        f"{categoria_titulo} en tela {caracteristicas.get('Tela','-')} "
        f"color base {caracteristicas.get('Color base','-')} "
        f"con diseño {diseno_legible}"
    )

    return {
        "categoria": categoria_titulo,
        "tipo": caracteristicas.get("Estilo", "-"),
        "modelo": codigo_modelo,
        "descripcion": descripcion,
        "caracteristicas": caracteristicas,
        "imagenes": imagenes,
        "piezas": piezas,
        "insumos": insumos,
        "logo": logo,
        "especificaciones": especificaciones,
    }


def _build_codigo_modelo(categoria_slug: str) -> str:
    """
    Genera un código de modelo único para la prenda.
    Ej: CA-09122025-ab12
    """
    hoy = datetime.now().strftime("%d%m%Y")
    prefijo = (categoria_slug or "PR")[:2].upper()
    return f"{prefijo}-{hoy}-{str(ObjectId())[:4]}"




# ============================================================
# PDF: ESTILO Y GENERACIÓN
# ============================================================

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
    title = ParagraphStyle(
        "Titulo",
        parent=styles["Heading1"],
        alignment=1,
        fontSize=16,
        textColor=colors.HexColor("#0a2e6c"),
    )
    subtitle = ParagraphStyle(
        "Subtitulo",
        parent=styles["Heading2"],
        textColor=colors.HexColor("#0a2e6c"),
    )
    normal = ParagraphStyle(
        "Normal",
        parent=styles["Normal"],
        fontSize=12,
        textColor=colors.black,
    )

    # -----------------------------
    # Normalizar características
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
    # Logo empresa (cabecera)
    # -----------------------------
    try:
        logo_url = "https://res.cloudinary.com/dcn5d4wbo/image/upload/v1759365264/LogoHori_eb7nnz.png"
        resp = requests.get(logo_url, stream=True, timeout=8)
        img_io = io.BytesIO(resp.content)
        pil_img = PILImage.open(img_io)
        temp_io = io.BytesIO()
        pil_img.save(temp_io, format="PNG")
        temp_io.seek(0)
        elements.append(Image(temp_io, width=30 * cm, height=7 * cm))
        elements.append(Spacer(10, 1 * cm))
    except Exception:
        pass

    # =====================
    # PORTADA
    # =====================
    elements.append(Paragraph("FICHA TÉCNICA DE PRENDA", title))
    elements.append(Spacer(1, 0.5 * cm))
    elements.append(
        Paragraph(f"<b>Categoría:</b> {ficha.get('categoria', '-')}", normal)
    )
    elements.append(Paragraph(f"<b>Modelo:</b> {ficha.get('modelo', '-')}", normal))
    elements.append(
        Paragraph(f"<b>Descripción:</b> {ficha.get('descripcion', '-')}", normal)
    )
    elements.append(Spacer(1, 0.8 * cm))

    # Imagen principal (acabado si existe)
    if ficha.get("imagenes", {}).get("acabado"):
        try:
            resp = requests.get(ficha["imagenes"]["acabado"], stream=True, timeout=10)
            img_io = io.BytesIO(resp.content)
            pil_img = PILImage.open(img_io)
            temp_io = io.BytesIO()
            pil_img.save(temp_io, format="JPEG")
            temp_io.seek(0)
            elements.append(
                Image(temp_io, width=10 * cm, height=10 * cm, kind="proportional")
            )
            elements.append(Spacer(1, 1 * cm))
        except Exception:
            pass

    elements.append(PageBreak())

    # =====================
    # CARACTERÍSTICAS
    # =====================
    elements.append(Paragraph("CARACTERÍSTICAS", subtitle))
    data = [["Campo", "Valor"]]

    for k, v in caracteristicas.items():
        # ❌ Omitimos completamente si:
        # - es None
        # - es cadena vacía o solo espacios
        # - es "-" (valor por defecto que no aporta info)
        # - es lista/dict vacío
        if v is None:
            continue

        if isinstance(v, str):
            v_str = v.strip()
            if not v_str or v_str == "-":
                continue
            valor_final = v_str
        elif isinstance(v, (list, dict)) and not v:
            continue
        else:
            valor_final = v

        data.append([str(k), str(valor_final)])

    # Si por alguna razón no hay nada, ponemos un mensaje
    if len(data) == 1:
        data.append(["-", "Sin características registradas"])

    tabla = Table(data, colWidths=[6 * cm, 10 * cm])
    tabla.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0a2e6c")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.whitesmoke, colors.lightgrey]),
                ("FONTNAME", (0, 0), (-1, -1), "Helvetica-Bold"),
            ]
        )
    )
    elements.append(tabla)
    elements.append(Spacer(1, 1 * cm))

    # =====================
    # COSTOS
    # =====================
    if ficha.get("costo"):
        elements.append(Paragraph("COSTOS", subtitle))
        data = [["Concepto", "Valor (USD)"]]
        costo = ficha["costo"]

        for k, v in costo.items():
            nombre = k.replace("_", " ").capitalize()
            try:
                val = float(v)
                valor_str = f"${val:.2f}"
            except (TypeError, ValueError):
                valor_str = str(v)
            data.append([nombre, valor_str])

        tabla = Table(data, colWidths=[8 * cm, 6 * cm])
        tabla.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0a2e6c")),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                    ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
                    ("ALIGN", (1, 1), (1, -1), "RIGHT"),
                    ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                    ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.whitesmoke, colors.lightgrey]),
                ]
            )
        )
        elements.append(tabla)
        elements.append(Spacer(1, 1 * cm))

    # =====================
    # PIEZAS
    # =====================
    elements.append(Paragraph("PIEZAS", subtitle))
    data = [["Pieza", "Cantidad", "Color"]]
    for pieza in ficha.get("piezas", []):
        data.append(
            [
                pieza.get("pieza", "-"),
                pieza.get("cantidad", "-"),
                pieza.get("color", "A tono"),
            ]
        )
    tabla = Table(data, colWidths=[8 * cm, 3 * cm, 5 * cm])
    tabla.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0a2e6c")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
                ("ALIGN", (1, 1), (-1, -1), "CENTER"),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.whitesmoke, colors.lightgrey]),
            ]
        )
    )
    elements.append(tabla)
    elements.append(Spacer(1, 1 * cm))

    # =====================
    # TELA NECESARIA Y TABLAS DE TALLAS
    # =====================

    cat_raw = (ficha.get("categoria") or "").lower().strip()
    cat_key = cat_raw.split()[0] if cat_raw else ""

    tela_cfg = TELA_NECESARIA.get(cat_key)
    if tela_cfg:
        elements.append(Paragraph(tela_cfg["titulo"], subtitle))
        data_tela = [tela_cfg["header"]]
        data_tela.extend(tela_cfg["rows"])

        tabla_tela = Table(data_tela, colWidths=[4 * cm] * len(tela_cfg["header"]))
        tabla_tela.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0a2e6c")),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                    ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
                    ("ALIGN", (1, 1), (-1, -1), "CENTER"),
                    ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                    ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.whitesmoke, colors.lightgrey]),
                ]
            )
        )
        elements.append(tabla_tela)
        elements.append(Spacer(1, 1 * cm))

    # ---- Tabla: Medidas por talla (si aplica) ----
    talla_cfg = TABLAS_TALLAS.get(cat_key)
    if talla_cfg:
        elements.append(Paragraph(talla_cfg["titulo"], subtitle))
        data_talla = [talla_cfg["header"]]
        data_talla.extend(talla_cfg["rows"])

        tabla_talla = Table(data_talla, colWidths=[5 * cm, 2 * cm, 2 * cm, 2 * cm, 2 * cm, 2 * cm])
        tabla_talla.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0a2e6c")),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                    ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
                    ("ALIGN", (1, 1), (-1, -1), "CENTER"),
                    ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                    ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.whitesmoke, colors.lightgrey]),
                ]
            )
        )
        elements.append(tabla_talla)
        elements.append(Spacer(1, 1 * cm))

    # =====================
    # INSUMOS
    # =====================
    elements.append(Paragraph("INSUMOS", subtitle))
    data = [["Descripción", "Cantidad", "Color"]]
    for ins in ficha.get("insumos", []):
        data.append(
            [
                ins.get("descripcion", "-"),
                str(ins.get("cantidad", "-")),
                ins.get("color", "A tono"),
            ]
        )
    tabla = Table(data, colWidths=[8 * cm, 3 * cm, 5 * cm])
    tabla.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0a2e6c")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
                ("ALIGN", (1, 1), (-1, -1), "CENTER"),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.whitesmoke, colors.lightgrey]),
            ]
        )
    )
    elements.append(tabla)
    elements.append(Spacer(1, 1 * cm))

    # =====================
    # LOGO
    # =====================
    if ficha.get("logo", {}).get("imagen"):
        elements.append(Paragraph("LOGO", subtitle))
        try:
            resp = requests.get(ficha["logo"]["imagen"], stream=True, timeout=10)
            img_io = io.BytesIO(resp.content)
            pil_img = PILImage.open(img_io)
            temp_io = io.BytesIO()
            pil_img.save(temp_io, format="JPEG")
            temp_io.seek(0)
            elements.append(
                Image(temp_io, width=5 * cm, height=5 * cm, kind="proportional")
            )
            elements.append(Spacer(1, 0.5 * cm))
        except Exception:
            pass
        elements.append(
            Paragraph(f"Tamaño: {ficha['logo'].get('tamano', '-')}", normal)
        )
        elements.append(
            Paragraph(f"Ubicación: {ficha['logo'].get('ubicacion', '-')}", normal)
        )
        elements.append(
            Paragraph(f"Estilo: {ficha['logo'].get('estilo', '-')}", normal)
        )
        elements.append(Spacer(1, 1 * cm))

    # =====================
    # ESPECIFICACIONES
    # =====================
    elements.append(Paragraph("ESPECIFICACIONES", subtitle))
    for esp in ficha.get("especificaciones", []):
        elements.append(Paragraph(f"- {esp}", normal))
    elements.append(Spacer(1, 1 * cm))

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
            resp = requests.get(url, stream=True, timeout=10)
            img_io = io.BytesIO(resp.content)
            pil_img = PILImage.open(img_io)
            temp_io = io.BytesIO()
            pil_img.save(temp_io, format="PNG")
            temp_io.seek(0)
            fila_imgs.append(
                Image(temp_io, width=6 * cm, height=6 * cm, kind="proportional")
            )
            titulos.append(Paragraph(nombre.capitalize(), normal))
        except Exception:
            pass
    if fila_imgs:
        elements.append(Table([fila_imgs], colWidths=[6 * cm] * len(fila_imgs)))
        elements.append(Table([titulos], colWidths=[6 * cm] * len(titulos)))
        elements.append(Spacer(1, 1 * cm))

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

    - Características generales por tipo de prenda:
      * Camiseta: cuello redondo, manga corta.
      * Pantalón: corte jogger, tobillo elástico, sin cierre ni cordón.
      * Chompa: sin cierre, con capucha, sin bolsillos.
      * Todo en tela de algodón si no se especifica otra cosa.

    - Usa prenda_data["costo"] (calculado con calcular_costo_prenda).
    - Muestra tablas de tela necesaria y tallas según la categoría.
    - Incluye insumos, especificaciones, colores/texturas, logos, textos.
    - Muestra hasta 4 renders en grilla 2×2.
    """
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    elementos = []
    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        "Title3D",
        parent=styles["Title"],
        alignment=1,
        textColor=colors.HexColor("#0a2e6c"),
    )
    subtitle = ParagraphStyle(
        "Sub3D",
        parent=styles["Heading2"],
        textColor=colors.HexColor("#0a2e6c"),
    )
    normal = styles["Normal"]

    categoria = (prenda_data.get("categoria") or "").strip()
    cat_key = categoria.lower().split()[0] if categoria else ""
    modelo = prenda_data.get("modelo", "")
    design_id = prenda_data.get("design_id") or "-"
    tela = prenda_data.get("tela") or "Algodón"
    hoy = datetime.now().strftime("%d/%m/%Y")

    # =======================
    # PORTADA
    # =======================
    try:
        logo_url = "https://res.cloudinary.com/dcn5d4wbo/image/upload/v1759365264/LogoHori_eb7nnz.png"
        resp = requests.get(logo_url, stream=True, timeout=8)
        img_io = io.BytesIO(resp.content)
        pil_img = PILImage.open(img_io)
        temp_io = io.BytesIO()
        pil_img.save(temp_io, format="PNG")
        temp_io.seek(0)
        elementos.append(Image(temp_io, width=30 * cm, height=7 * cm))
        elementos.append(Spacer(1, 0.5 * cm))
    except Exception:
        pass

    elementos.append(Paragraph(f"FICHA TÉCNICA 3D - {categoria.upper() or 'PRENDA'}", title_style))
    elementos.append(Spacer(1, 0.2 * cm))
    elementos.append(Paragraph(f"Modelo: {modelo or '-'}   |   Fecha: {hoy}", normal))
    elementos.append(Spacer(1, 0.5 * cm))

    renders = prenda_data.get("renders", {}) or {}
    render_frente = renders.get("render_frente")
    if render_frente:
        try:
            response = requests.get(render_frente, stream=True, timeout=10)
            img_io = io.BytesIO(response.content)
            pil_img = PILImage.open(img_io)
            temp_io = io.BytesIO()
            pil_img.save(temp_io, format="PNG")
            temp_io.seek(0)
            elementos.append(Image(temp_io, width=12 * cm, height=12 * cm, kind="proportional"))
            elementos.append(Spacer(1, 0.5 * cm))
        except Exception as e:
            elementos.append(Paragraph(f"No se pudo cargar la vista frontal: {e}", styles["Italic"]))

    elementos.append(PageBreak())

    # =======================
    # CARACTERÍSTICAS GENERALES (sin id usuario)
    # =======================
    elementos.append(Paragraph("CARACTERÍSTICAS GENERALES", subtitle))
    caracteristicas = {
        "Categoría": categoria or "-",
        "Modelo": modelo or "-",
        "Diseño base": design_id,
        "Tela": tela,
    }

    if cat_key == "camiseta":
        caracteristicas.update({
            "Cuello": "Redondo",
            "Manga": "Corta",
        })
    elif cat_key == "pantalon":
        caracteristicas.update({
            "Tipo de corte": "Jogger",
            "Tipo de tobillo": "Elástico",
            "Cierre": "Sin cierre",
            "Cordón": "Sin cordón",
        })
    elif cat_key == "chompa":
        caracteristicas.update({
            "Cierre": "Sin cierre",
            "Capucha": "Con capucha",
            "Bolsillos": "Sin bolsillos",
        })
    # pantaloneta: de momento sin extras fijos

    data_car = [["Campo", "Valor"]]
    for k, v in caracteristicas.items():
        if v is None:
            continue
        if isinstance(v, str) and not v.strip():
            continue
        data_car.append([k, str(v)])

    tabla_car = Table(data_car, colWidths=[6 * cm, 10 * cm])
    tabla_car.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0a2e6c")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.whitesmoke, colors.lightgrey]),
            ]
        )
    )
    elementos.append(tabla_car)
    elementos.append(Spacer(1, 0.8 * cm))

    # =======================
    # COSTOS (mismo esquema que IA)
    # =======================
    if prenda_data.get("costo"):
        elementos.append(Paragraph("COSTOS", subtitle))
        costo = prenda_data["costo"]
        data_costo = [["Concepto", "Valor (USD)"]]
        for k, v in costo.items():
            nombre = k.replace("_", " ").capitalize()
            try:
                val = float(v)
                valor_str = f"${val:.2f}"
            except (TypeError, ValueError):
                valor_str = str(v)
            data_costo.append([nombre, valor_str])

        tabla_costo = Table(data_costo, colWidths=[8 * cm, 6 * cm])
        tabla_costo.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0a2e6c")),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                    ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
                    ("ALIGN", (1, 1), (1, -1), "RIGHT"),
                    ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                    ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.whitesmoke, colors.lightgrey]),
                ]
            )
        )
        elementos.append(tabla_costo)
        elementos.append(Spacer(1, 0.8 * cm))

    # =======================
    # TELA NECESARIA + TABLA DE TALLAS
    # =======================
    tela_cfg = TELA_NECESARIA.get(cat_key)
    if tela_cfg:
        elementos.append(Paragraph(tela_cfg["titulo"], subtitle))
        data_tela = [tela_cfg["header"]]
        data_tela.extend(tela_cfg["rows"])
        tabla_tela = Table(data_tela, colWidths=[4 * cm] * len(tela_cfg["header"]))
        tabla_tela.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0a2e6c")),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                    ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                    ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.whitesmoke, colors.lightgrey]),
                ]
            )
        )
        elementos.append(tabla_tela)
        elementos.append(Spacer(1, 0.6 * cm))

    talla_cfg = TABLAS_TALLAS.get(cat_key)
    if talla_cfg:
        elementos.append(Paragraph(talla_cfg["titulo"], subtitle))
        data_talla = [talla_cfg["header"]]
        data_talla.extend(talla_cfg["rows"])
        tabla_talla = Table(
            data_talla,
            colWidths=[5 * cm, 2 * cm, 2 * cm, 2 * cm, 2 * cm, 2 * cm],
        )
        tabla_talla.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0a2e6c")),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                    ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                    ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.whitesmoke, colors.lightgrey]),
                ]
            )
        )
        elementos.append(tabla_talla)
        elementos.append(Spacer(1, 0.8 * cm))

    # =======================
    # INSUMOS
    # =======================
    elementos.append(Paragraph("INSUMOS", subtitle))
    insumos = [
        {"descripcion": "Tela principal algodón", "cantidad": "Según talla", "color": "A tono"},
        {"descripcion": "Hilo poliéster 120", "cantidad": "Varios", "color": "A tono"},
    ]
    data_ins = [["Descripción", "Cantidad", "Color"]]
    for ins in insumos:
        data_ins.append([
            ins.get("descripcion", "-"),
            str(ins.get("cantidad", "-")),
            ins.get("color", "A tono"),
        ])
    tabla_ins = Table(data_ins, colWidths=[8 * cm, 3 * cm, 5 * cm])
    tabla_ins.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0a2e6c")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
                ("ALIGN", (1, 1), (-1, -1), "CENTER"),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.whitesmoke, colors.lightgrey]),
            ]
        )
    )
    elementos.append(tabla_ins)
    elementos.append(Spacer(1, 0.8 * cm))

    # =======================
    # ESPECIFICACIONES
    # =======================
    elementos.append(Paragraph("ESPECIFICACIONES", subtitle))
    especificaciones = [
        "Costuras reforzadas",
        "Acabados de alta calidad",
        "Prenda diseñada para uso deportivo",
    ]
    for esp in especificaciones:
        elementos.append(Paragraph(f"- {esp}", normal))
    elementos.append(Spacer(1, 0.8 * cm))

    # =======================
    # COLORES Y TEXTURAS POR ZONA
    # =======================
    colors_data = prenda_data.get("colors", {}) or {}
    textures_data = prenda_data.get("textures", {}) or {}
    if colors_data or textures_data:
        elementos.append(Paragraph("COLORES Y TEXTURAS POR ZONA", subtitle))
        tabla_colores = [["Zona", "Color", "Textura"]]
        for zona, color in colors_data.items():
            textura = textures_data.get(zona) or "-"
            tabla_colores.append([str(zona).capitalize(), color, linkify(textura)])
        tabla_col = Table(tabla_colores, colWidths=[5 * cm, 4 * cm, 7 * cm])
        tabla_col.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0a2e6c")),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                    ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                    ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                    ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.whitesmoke, colors.lightgrey]),
                ]
            )
        )
        elementos.append(tabla_col)
        elementos.append(Spacer(1, 0.8 * cm))

    # =======================
    # LOGOS
    # =======================
    decals = prenda_data.get("decals", []) or []
    if decals:
        elementos.append(Paragraph("LOGOS", subtitle))
        for idx, d in enumerate(decals, start=1):
            data_logo = [
                ["Logo", linkify(d.get("url", "-"))],
                ["Posición", str(d.get("position", "-"))],
                ["Escala", d.get("scale", "-")],
                ["Rotación", d.get("rotationZ", "-")],
            ]
            tabla_logo = Table(data_logo, colWidths=[3 * cm, 12 * cm])
            tabla_logo.setStyle(
                TableStyle(
                    [
                        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                        ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#0a2e6c")),
                        ("TEXTCOLOR", (0, 0), (0, -1), colors.white),
                        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                        ("ALIGN", (1, 0), (-1, -1), "LEFT"),
                    ]
                )
            )
            elementos.append(Paragraph(f"Logo {idx}", styles["Heading3"]))
            elementos.append(tabla_logo)
            elementos.append(Spacer(1, 0.4 * cm))

    # =======================
    # TEXTOS
    # =======================
    textDecals = prenda_data.get("textDecals", []) or []
    if textDecals:
        elementos.append(Paragraph("TEXTOS APLICADOS", subtitle))
        for idx, t in enumerate(textDecals, start=1):
            data_texto = [
                ["Texto", t.get("text", "-")],
                ["Posición", str(t.get("position", "-"))],
                ["Escala", t.get("scale", "-")],
                ["Rotación", t.get("rotationZ", "-")],
            ]
            tabla_texto = Table(data_texto, colWidths=[3 * cm, 12 * cm])
            tabla_texto.setStyle(
                TableStyle(
                    [
                        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                        ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#0a2e6c")),
                        ("TEXTCOLOR", (0, 0), (0, -1), colors.white),
                        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                        ("ALIGN", (1, 0), (-1, -1), "LEFT"),
                    ]
                )
            )
            elementos.append(Paragraph(f"Texto {idx}", styles["Heading3"]))
            elementos.append(tabla_texto)
            elementos.append(Spacer(1, 0.4 * cm))

    # =======================
    # VISTAS DEL DISEÑO 2×2
    # =======================
    if renders:
        elementos.append(Paragraph("VISTAS DEL DISEÑO (ACABADOS)", subtitle))
        imgs = []
        for key in ["render_frente", "render_espalda", "render_lado_izq", "render_lado_der"]:
            url = renders.get(key)
            if not url:
                continue
            try:
                resp = requests.get(url, stream=True, timeout=10)
                img_io = io.BytesIO(resp.content)
                pil_img = PILImage.open(img_io)
                temp_io = io.BytesIO()
                pil_img.save(temp_io, format="PNG")
                temp_io.seek(0)
                imgs.append(Image(temp_io, width=8 * cm, height=8 * cm, kind="proportional"))
            except Exception as e:
                elementos.append(Paragraph(f"Error cargando {key}: {e}", normal))

        # construir grilla 2x2
        filas = []
        if imgs:
            for i in range(0, len(imgs), 2):
                fila = imgs[i:i+2]
                # si falta una en la fila, agregamos espacio en blanco para mantener columnas
                while len(fila) < 2:
                    fila.append(Spacer(1, 8 * cm))
                filas.append(fila)

            tabla_vistas = Table(filas, colWidths=[8 * cm, 8 * cm], hAlign="CENTER")
            elementos.append(tabla_vistas)
            elementos.append(Spacer(1, 0.8 * cm))

    # Plano de sublimación (si existe)
    plano_sublimacion_url = prenda_data.get("plano_sublimacion_url")
    if plano_sublimacion_url:
        elementos.append(Paragraph("PLANO BASE DE COLOR (SUBLIMACIÓN)", subtitle))
        try:
            resp = requests.get(plano_sublimacion_url, timeout=10)
            if resp.status_code == 200:
                img_io = io.BytesIO(resp.content)
                pil_img = PILImage.open(img_io).convert("RGB")
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
        except Exception as e:
            elementos.append(Paragraph(f"⚠️ Error cargando plano: {str(e)}", normal))

    doc.build(elementos)
    pdf_bytes = buffer.getvalue()
    buffer.close()
    return pdf_bytes

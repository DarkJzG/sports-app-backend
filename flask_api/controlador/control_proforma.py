# flask_api/controlador/control_proforma.py
import io
from datetime import datetime

import requests
from PIL import Image as PILImage

from flask import current_app

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
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER


# ==========================
# ESTILOS COMPARTIDOS
# ==========================

def add_background(canvas, doc):
    """Fondo azul claro, igual que en la ficha técnica."""
    canvas.saveState()
    canvas.setFillColor(colors.HexColor("#f0f6ff"))
    canvas.rect(0, 0, A4[0], A4[1], fill=1)
    canvas.restoreState()


style_link = ParagraphStyle(
    "Link",
    fontSize=8,
    alignment=TA_CENTER,
    textColor="blue",
)


def linkify(url: str):
    """Devuelve un Paragraph con link clicable o '-' si no hay URL."""
    if not url or url == "-":
        return "-"
    return Paragraph(f'<link href="{url}" color="blue">Ver ficha</link>', style_link)


# ==========================
# PROFORMA PDF
# ==========================

def generar_pdf_proforma(pedido: dict, empresa: dict, usuario: dict) -> bytes:
    """
    Genera un PDF de proforma con diseño similar a las fichas técnicas.

    Incluye:
    - Logo y datos de la empresa
    - Datos del cliente y envío
    - Detalle de ítems (talla, cantidad, precios, link a ficha técnica)
    - Subtotal, IVA, envío y total
    """

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        leftMargin=2 * cm,
        rightMargin=2 * cm,
        topMargin=2 * cm,
        bottomMargin=2 * cm,
    )

    styles = getSampleStyleSheet()

    title_empresa = ParagraphStyle(
        "TituloEmpresa",
        parent=styles["Title"],
        alignment=TA_CENTER,
        textColor=colors.HexColor("#0a2e6c"),
    )
    subtitle = ParagraphStyle(
        "Subtitulo",
        parent=styles["Heading2"],
        textColor=colors.HexColor("#0a2e6c"),
        alignment=TA_CENTER,
    )
    normal = styles["Normal"]
    small = ParagraphStyle(
        "Small",
        parent=styles["Normal"],
        fontSize=9,
    )

    elements = []

    # ==========================
    # LOGO + DATOS EMPRESA
    # ==========================
    logo_url = (
        empresa.get("logo_url")
        or empresa.get("logoUrl")
        or empresa.get("logo")
    )

    # Fallback al logo que ya usas en fichas técnicas
    if not logo_url:
        logo_url = "https://res.cloudinary.com/dcn5d4wbo/image/upload/v1759365264/LogoHori_eb7nnz.png"

    try:
        resp = requests.get(logo_url, stream=True, timeout=8)
        if resp.status_code == 200:
            img_io = io.BytesIO(resp.content)
            pil_img = PILImage.open(img_io)
            temp_io = io.BytesIO()
            pil_img.save(temp_io, format="PNG")
            temp_io.seek(0)
            # Logo horizontal en la parte superior
            elements.append(Image(temp_io, width=14 * cm, height=3 * cm))
            elements.append(Spacer(1, 0.3 * cm))
    except Exception as e:
        current_app.logger.warning(f"⚠️ No se pudo cargar logo empresa: {e}")

    empresa_nombre = (
        empresa.get("nombre_comercial")
        or empresa.get("razon_social")
        or empresa.get("nombre")
        or "Confecciones Johan Sport"
    )
    ruc = empresa.get("ruc", "")
    direccion_emp = empresa.get("direccion", "")
    telefono_emp = empresa.get("telefono", "")
    correo_emp = empresa.get("correo", "")

    elements.append(Paragraph(empresa_nombre, title_empresa))
    elements.append(Spacer(1, 0.1 * cm))

    # Datos empresa en pequeño
    linea_empresa = []
    if ruc:
        linea_empresa.append(f"RUC: {ruc}")
    if direccion_emp:
        linea_empresa.append(f"Dirección: {direccion_emp}")
    if telefono_emp:
        linea_empresa.append(f"Teléfono: {telefono_emp}")
    if correo_emp:
        linea_empresa.append(f"Correo: {correo_emp}")

    if linea_empresa:
        elements.append(Paragraph(" &nbsp; • &nbsp; ".join(linea_empresa), small))

    elements.append(Spacer(1, 0.5 * cm))
    elements.append(Paragraph("PROFORMA", subtitle))
    elements.append(Spacer(1, 0.2 * cm))

    fecha_str = datetime.utcnow().strftime("%d/%m/%Y %H:%M")
    numero_pedido = (
        pedido.get("numero")
        or pedido.get("codigo")
        or str(pedido.get("_id", ""))[:8]
    )
    elements.append(
        Paragraph(f"Fecha: {fecha_str} UTC &nbsp;&nbsp;&nbsp; N° Pedido: {numero_pedido}", small)
    )
    elements.append(Spacer(1, 0.6 * cm))

    # ==========================
    # DATOS CLIENTE / ENVÍO
    # ==========================
    elements.append(Paragraph("Datos del Cliente", styles["Heading3"]))
    elements.append(Spacer(1, 0.1 * cm))

    cliente_nombre = (
        pedido.get("clienteNombre")
        or pedido.get("cliente_nombre")
        or usuario.get("nombre_completo")
        or "-"
    )
    cliente_correo = (
        pedido.get("clienteCorreo")
        or usuario.get("email")
        or "-"
    )

    elements.append(Paragraph(f"<b>Cliente:</b> {cliente_nombre}", normal))
    if cliente_correo and cliente_correo != "-":
        elements.append(Paragraph(f"<b>Correo:</b> {cliente_correo}", normal))

    direccion_envio = pedido.get("direccionEnvio", {}) or {}
    tipo_envio = direccion_envio.get("tipoEnvio", "domicilio")

    if tipo_envio == "domicilio":
        dir_linea = direccion_envio.get("direccion_principal", "")
        ciudad = direccion_envio.get("ciudad", "")
        provincia = direccion_envio.get("provincia", "")
        telefono = direccion_envio.get("telefono", "")
        elements.append(
            Paragraph(f"<b>Dirección:</b> {dir_linea or '-'}", normal)
        )
        elements.append(
            Paragraph(
                f"<b>Ciudad/Provincia:</b> {ciudad or '-'} - {provincia or '-'}",
                normal,
            )
        )
        if telefono:
            elements.append(
                Paragraph(f"<b>Teléfono:</b> {telefono}", normal)
            )
    else:
        elements.append(
            Paragraph("<b>Entrega:</b> Retiro en tienda", normal)
        )

    elements.append(Spacer(1, 0.5 * cm))
    # ==========================
    # TABLA DE ITEMS
    # ==========================
    elements.append(Paragraph("Detalle de la Proforma", styles["Heading3"]))
    elements.append(Spacer(1, 0.2 * cm))

    simbolo_moneda = (
        empresa.get("configuracion", {}) or {}
    ).get("simboloMoneda", "$")

    header_items = [
        "Ítem",
        "Producto",
        "Talla",
        "Cantidad",
        f"Precio Unit. ({simbolo_moneda})",
        f"Total ({simbolo_moneda})",
        "Ficha técnica",
    ]
    data_items = [header_items]

    # 👇 Estilo para celdas de texto que deben hacer wrap (Producto)
    cell_style = styles["Normal"].clone('CellStyle')
    cell_style.fontSize = 8
    cell_style.leading = 9  # espacio entre líneas

    items = pedido.get("items", []) or []
    for idx, item in enumerate(items, start=1):
        # Nombre crudo
        nombre_raw = (
            item.get("codigo")
            or item.get("sku")
            or item.get("nombre")
            or "Producto"
        )
        # ⬅️ Ahora el nombre es un Paragraph → permite salto de línea
        nombre = Paragraph(nombre_raw, cell_style)

        talla = item.get("talla") or "N/A"
        cantidad = int(item.get("cantidad", 1) or 1)

        p_unit = float(
            item.get("precioUnitario")
            or item.get("precio_unitario")
            or item.get("precio")
            or 0
        )
        p_total = float(
            item.get("precioTotal")
            or item.get("precio_total")
            or p_unit * cantidad
        )

        # URL de ficha técnica (se espera que ya venga en ficha_pdf_url)
        ficha_url = (
            item.get("ficha_pdf_url")
            or item.get("ficha_url")
            or item.get("fichaPdfUrl")
        )

        fila = [
            str(idx),
            nombre,          # 👈 aquí va el Paragraph, no el string
            talla,
            str(cantidad),
            f"{p_unit:.2f}",
            f"{p_total:.2f}",
            linkify(ficha_url),
        ]
        data_items.append(fila)

    tabla_items = Table(
        data_items,
        colWidths=[
            1.2 * cm,  # Ítem
            6.0 * cm,  # Producto (el Paragraph se ajusta a este ancho)
            1.2 * cm,  # Talla
            1.8 * cm,  # Cantidad
            2.8 * cm,  # P.Unit
            2.0 * cm,  # Total
            3.0 * cm,  # Ficha
        ],
        hAlign="LEFT",
    )

    tabla_items.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0a2e6c")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("ALIGN", (0, 0), (-1, 0), "CENTER"),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, 0), 9),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                ("ALIGN", (0, 1), (0, -1), "CENTER"),
                ("ALIGN", (3, 1), (5, -1), "RIGHT"),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("FONTSIZE", (0, 1), (-1, -1), 8),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1),
                 [colors.whitesmoke, colors.lightgrey]),
            ]
        )
    )

    elements.append(tabla_items)
    elements.append(Spacer(1, 0.6 * cm))

    # ==========================
    # TOTALES
    # ==========================
    costos = pedido.get("costos", {}) or {}
    subtotal = float(costos.get("subtotal", 0) or 0)
    envio = float(costos.get("envio", 0) or 0)
    impuestos = float(costos.get("impuestos", 0) or 0)
    total = float(costos.get("total", subtotal + envio + impuestos) or 0)
    iva_porcentaje = (
        empresa.get("configuracion", {}) or {}
    ).get("iva", 15)

    data_totales = [
        ["", "", "Subtotal:", f"{simbolo_moneda}{subtotal:.2f}"],
        ["", "", f"IVA ({iva_porcentaje}%):", f"{simbolo_moneda}{impuestos:.2f}"],
        ["", "", "Envío:", f"{simbolo_moneda}{envio:.2f}"],
        ["", "", "TOTAL:", f"{simbolo_moneda}{total:.2f}"],
    ]

    tabla_totales = Table(
        data_totales,
        colWidths=[6 * cm, 4 * cm, 4 * cm, 3 * cm],
        hAlign="RIGHT",
    )

    tabla_totales.setStyle(
        TableStyle(
            [
                ("ALIGN", (2, 0), (3, -1), "RIGHT"),
                ("FONTNAME", (2, 0), (3, -2), "Helvetica"),
                ("FONTSIZE", (2, 0), (3, -1), 9),
                ("TEXTCOLOR", (2, 0), (3, -2), colors.black),
                ("FONTNAME", (2, -1), (3, -1), "Helvetica-Bold"),
                ("BACKGROUND", (2, -1), (3, -1), colors.HexColor("#E5E7EB")),
                ("GRID", (2, 0), (3, -1), 0.25, colors.grey),
            ]
        )
    )

    elements.append(tabla_totales)
    elements.append(Spacer(1, 0.8 * cm))

    # Nota final
    elements.append(
        Paragraph(
            "Esta proforma es referencial y no constituye comprobante tributario.",
            styles["Italic"],
        )
    )

    # ==========================
    # GENERAR PDF
    # ==========================
    doc.build(
        elements,
        onFirstPage=add_background,
        onLaterPages=add_background,
    )

    pdf_bytes = buffer.getvalue()
    buffer.close()
    return pdf_bytes

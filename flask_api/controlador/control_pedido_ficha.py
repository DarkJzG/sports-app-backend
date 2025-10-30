# flask_api/controlador/control_pedido_ficha.py
import io, cloudinary.uploader
from flask import current_app
from bson import ObjectId
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
from reportlab.lib.units import cm
from datetime import datetime

from flask_api.modelo.modelo_pedido import get_pedidos_collection, _serialize
from flask_api.modelo.modelo_ia_prendas import get_prendas_collection
from flask_api.modelo.modelo_ficha_tecnica import get_fichas_collection


def generar_ficha_tecnica_pedido(pedido_id: str):
    """
    Genera un PDF consolidado con todas las prendas IA de un pedido.
    Devuelve { ok, url, ficha_id }.
    """
    col_pedidos = get_pedidos_collection()
    pedido = col_pedidos.find_one({"_id": ObjectId(pedido_id)})
    if not pedido:
        return {"ok": False, "msg": "Pedido no encontrado"}

    pedido = _serialize(pedido)
    items_ia = [it for it in pedido["items"] if it.get("tipo") == "ia_prenda"]

    if not items_ia:
        return {"ok": False, "msg": "El pedido no contiene prendas IA"}

    col_prendas = get_prendas_collection()
    fichas_col = get_fichas_collection()

    # 🧱 Crear documento PDF en memoria
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    styles = getSampleStyleSheet()
    story = []

    # Encabezado principal
    story.append(Paragraph("<b>FICHA TÉCNICA - PEDIDO CONSOLIDADO</b>", styles["Title"]))
    story.append(Spacer(1, 0.4 * cm))
    story.append(Paragraph(f"<b>Pedido:</b> {pedido['_id']}", styles["Normal"]))
    story.append(Paragraph(f"<b>Cliente:</b> {pedido.get('direccionEnvio', {}).get('nombre', 'N/A')}", styles["Normal"]))
    story.append(Paragraph(f"<b>Fecha:</b> {datetime.now().strftime('%d/%m/%Y')}", styles["Normal"]))
    story.append(Spacer(1, 0.5 * cm))

    # Recorrer prendas IA
    for idx, item in enumerate(items_ia, 1):
        story.append(Paragraph(f"<b>Prenda {idx}:</b> {item['nombre']}", styles["Heading3"]))
        story.append(Spacer(1, 0.2 * cm))

        # Buscar prenda base (colección prendas)
        prenda = col_prendas.find_one({"_id": ObjectId(item["productId"])})
        if not prenda:
            story.append(Paragraph("<font color='red'>No se encontró la prenda en base de datos.</font>", styles["Normal"]))
            continue

        # Datos básicos
        atributos = prenda.get("atributos_es", {})
        costo = prenda.get("costo", {})

        data = [
            ["Talla", item.get("talla", "-"), "Cantidad", item.get("cantidad", "-")],
            ["Color Principal", atributos.get("color1", "-"), "Color Secundario", atributos.get("color2", "-")],
            ["Tela", atributos.get("tela", "-"), "Género", atributos.get("genero", "-")],
            ["Precio Unit.", f"${costo.get('precio_venta', 0):.2f}", "Subtotal", f"${item.get('cantidad', 0) * costo.get('precio_venta', 0):.2f}"],
        ]
        tabla = Table(data, colWidths=[3*cm, 4*cm, 3*cm, 4*cm])
        tabla.setStyle(TableStyle([
            ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
            ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
            ("FONTNAME", (0, 0), (-1, -1), "Helvetica"),
            ("ALIGN", (1, 0), (-1, -1), "CENTER"),
        ]))
        story.append(tabla)
        story.append(Spacer(1, 0.3 * cm))

        # Imagen
        image_url = prenda.get("imageUrl")
        if image_url:
            try:
                story.append(Image(image_url, width=6*cm, height=6*cm))
                story.append(Spacer(1, 0.3 * cm))
            except Exception:
                story.append(Paragraph("⚠️ No se pudo cargar la imagen.", styles["Normal"]))

        story.append(Spacer(1, 0.6 * cm))

    # Pie de página
    story.append(Paragraph("<b>Fin de Ficha Técnica Consolidada</b>", styles["Italic"]))

    # Guardar PDF en memoria
    doc.build(story)
    pdf_data = buffer.getvalue()
    buffer.close()

    # Subir PDF a Cloudinary
    upload = cloudinary.uploader.upload(
        io.BytesIO(pdf_data),
        folder="fichas_tecnicas_pedidos",
        resource_type="raw",
        public_id=f"FichaPedido_{pedido['_id']}"
    )

    pdf_url = upload.get("secure_url")

    # Guardar en colección fichas_tecnicas
    ficha_doc = {
        "pedido_id": pedido["_id"],
        "user_id": pedido["userId"],
        "tipo": "consolidado_ia",
        "url_pdf": pdf_url,
        "createdAt": datetime.utcnow(),
        "items_incluidos": [it["productId"] for it in items_ia],
    }

    ficha_id = fichas_col.insert_one(ficha_doc).inserted_id

    # Actualizar pedido con el id de ficha técnica
    col_pedidos.update_one(
        {"_id": ObjectId(pedido_id)},
        {"$set": {"ficha_tecnica_id": str(ficha_id), "ficha_tecnica_url": pdf_url}}
    )

    return {"ok": True, "url": pdf_url, "ficha_id": str(ficha_id)}

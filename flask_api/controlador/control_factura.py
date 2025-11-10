# flask_api/controlador/control_factura.py
from flask import current_app, jsonify
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image as RLImage
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_RIGHT, TA_LEFT
from bson import ObjectId
from datetime import datetime
import io
import cloudinary.uploader
import requests
from io import BytesIO

from flask_api.modelo.modelo_pedido import get_pedidos_collection, _serialize
from flask_api.modelo.modelo_empresa import obtener_empresa
from flask_api.modelo.modelo_usuario import get_users_collection


def generar_factura_pdf(pedido_id: str):
    """
    Genera una factura en PDF con diseño profesional similar a la imagen de referencia.
    
    Returns:
        tuple: (success: bool, url_o_error: str)
    """
    try:
        # Obtener el pedido
        col = get_pedidos_collection()
        pedido = col.find_one({"_id": ObjectId(pedido_id)})
        
        if not pedido:
            return False, "Pedido no encontrado"
        
        # Serializar pedido
        pedido_data = _serialize(pedido)
        
        # Validar que el pago esté completo
        if pedido_data.get("infoPago", {}).get("estado_pago") != "pago_completo":
            return False, "El pedido no tiene el pago completo"
        
        # Obtener datos de la empresa
        empresa = obtener_empresa()
        if not empresa:
            return False, "No se pudo obtener información de la empresa"
        
        # Crear buffer en memoria para el PDF
        buffer = io.BytesIO()
        
        # Crear documento PDF con márgenes ajustados
        doc = SimpleDocTemplate(
            buffer,
            pagesize=letter,
            rightMargin=40,
            leftMargin=40,
            topMargin=40,
            bottomMargin=40
        )
        
        # Contenedor para los elementos del PDF
        story = []
        styles = getSampleStyleSheet()
        
        # ===== ESTILOS PERSONALIZADOS =====
        header_text_style = ParagraphStyle(
            'HeaderText',
            parent=styles['Normal'],
            fontSize=8,
            textColor=colors.HexColor('#000000'),
            leading=10
        )
        
        info_label_style = ParagraphStyle(
            'InfoLabel',
            parent=styles['Normal'],
            fontSize=9,
            textColor=colors.HexColor('#000000'),
            fontName='Helvetica-Bold'
        )
        
        info_value_style = ParagraphStyle(
            'InfoValue',
            parent=styles['Normal'],
            fontSize=9,
            textColor=colors.HexColor('#000000')
        )
        
        section_title_style = ParagraphStyle(
            'SectionTitle',
            parent=styles['Normal'],
            fontSize=10,
            textColor=colors.whitesmoke,
            fontName='Helvetica-Bold',
            alignment=TA_LEFT
        )
        
        # ===== HEADER: Logo + Datos Empresa + Números de Factura =====
        logo = None
        logo_width = 1.3 * inch
        logo_height = 1.3 * inch
        
        # Intentar cargar el logo
        if empresa.get('imagenPdf') or empresa.get('logo'):
            logo_url = empresa.get('imagenPdf') or empresa.get('logo')
            try:
                response = requests.get(logo_url, timeout=5)
                if response.status_code == 200:
                    logo_io = BytesIO(response.content)
                    logo = RLImage(logo_io, width=logo_width, height=logo_height)
                    current_app.logger.info(f"Logo cargado desde: {logo_url}")
            except Exception as e:
                current_app.logger.warning(f"No se pudo cargar el logo: {str(e)}")
        
        # Datos de la empresa
        empresa_text = f"""
            <b><font size="11">{empresa.get('nombre', 'Empresa')}</font></b><br/>
            <font size="8">RUC: {empresa.get('ruc', 'N/A')}</font><br/>
            <font size="8">{empresa.get('direccion', '')}</font><br/>
            <font size="8">{empresa.get('ciudad', '')}, {empresa.get('provincia', '')}</font><br/>
            <font size="8">Tel: {empresa.get('telefono', '')}</font><br/>
            <font size="8">Email: {empresa.get('email', '')}</font>
        """
        
        # Números de factura y pedido
        num_factura = f"FAC-{pedido_data['_id'][-10:].upper()}"
        num_pedido = f"#{pedido_data['_id'][-6:].upper()}"
        
        numeros_text = f"""
            <para alignment="right">
                <b><font size="10">Nº Factura:</font></b><br/>
                <font size="12">{num_factura}</font><br/>
                <br/>
                <b><font size="10">Nº Pedido:</font></b><br/>
                <font size="12">{num_pedido}</font>
            </para>
        """
        
        # Construir header
        if logo:
            header_row = [
                logo,
                Paragraph(empresa_text, header_text_style),
                Paragraph(numeros_text, header_text_style)
            ]
            header_table = Table([header_row], colWidths=[1.5*inch, 3.5*inch, 2.3*inch])
        else:
            header_row = [
                Paragraph(empresa_text, header_text_style),
                Paragraph(numeros_text, header_text_style)
            ]
            header_table = Table([header_row], colWidths=[4.8*inch, 2.5*inch])
        
        header_table.setStyle(TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('ALIGN', (0, 0), (0, 0), 'LEFT'),
            ('ALIGN', (-1, 0), (-1, 0), 'RIGHT'),
        ]))
        
        story.append(header_table)
        story.append(Spacer(1, 0.25*inch))
        
        # ===== SECCIÓN: DATOS DEL CLIENTE =====
        cliente_header = Table(
            [[Paragraph("NOMBRES CLIENTE", section_title_style)]],
            colWidths=[7.3*inch]
        )
        cliente_header.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#1e3a8a')),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.whitesmoke),
            ('PADDING', (0, 0), (-1, -1), 6),
        ]))
        story.append(cliente_header)

        # ✅ Obtener datos completos del cliente desde la BD
        from flask_api.modelo.modelo_usuario import get_users_collection

        user_id = pedido.get('userId')
        usuario = None
        if user_id:
            users_col = get_users_collection()
            usuario = users_col.find_one({"_id": ObjectId(user_id)})

        # Construir datos del cliente
        if usuario:
            cliente_nombre = f"{usuario.get('nombre', '')} {usuario.get('apellido', '')}".strip()
            cliente_correo = usuario.get('correo', 'N/A')
            cliente_cedula = usuario.get('cedula', 'N/A')  # ✅ Campo que contiene CI o RUC
            cliente_telefono = usuario.get('telefono', 'N/A')
        else:
            # Fallback a datos del pedido si no se encuentra el usuario
            cliente_nombre = pedido_data.get('clienteNombre', 'N/A')
            cliente_correo = pedido_data.get('clienteCorreo', 'N/A')
            cliente_cedula = 'N/A'
            cliente_telefono = pedido_data.get('direccionEnvio', {}).get('telefono', 'N/A')

        # Obtener dirección de envío
        direccion_envio = pedido_data.get('direccionEnvio', {})
        if direccion_envio.get('tipoEnvio') == 'retiro':
            cliente_direccion = "RETIRO EN LOCAL"
        else:
            dir_principal = direccion_envio.get('direccion_principal', '')
            ciudad = direccion_envio.get('ciudad', '')
            provincia = direccion_envio.get('provincia', '')
            
            # Construir dirección completa
            partes_direccion = [p for p in [dir_principal, ciudad, provincia] if p]
            cliente_direccion = ', '.join(partes_direccion) if partes_direccion else 'N/A'

        # Tabla de datos del cliente
        cliente_data = [
            # Primera fila: nombre completo del cliente
            [Paragraph(cliente_nombre, info_value_style), "", "", ""],
            # Segunda fila: headers de las columnas
            [Paragraph("<b>CORREO</b>", info_label_style), 
            Paragraph("<b>R.U.C. / C.I.</b>", info_label_style),
            Paragraph("<b>DIRECCIÓN</b>", info_label_style),
            Paragraph("<b>TELÉFONO</b>", info_label_style)],
            # Tercera fila: valores
            [Paragraph(cliente_correo, info_value_style), 
            Paragraph(cliente_cedula, info_value_style),
            Paragraph(cliente_direccion, info_value_style),
            Paragraph(cliente_telefono, info_value_style)]
        ]

        cliente_table = Table(cliente_data, colWidths=[1.825*inch, 1.825*inch, 1.825*inch, 1.825*inch])
        cliente_table.setStyle(TableStyle([
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('SPAN', (0, 0), (-1, 0)),  # ✅ Unir celdas de la primera fila para el nombre
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (0, 0), 10),  # Nombre más grande
            ('FONTSIZE', (0, 1), (-1, -1), 8),
            ('PADDING', (0, 0), (-1, -1), 4),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        story.append(cliente_table)
        story.append(Spacer(1, 0.15*inch))
        
        # ===== SECCIÓN: FECHA Y HORA DE EMISIÓN + ENVÍO =====
        fecha_emision = datetime.now()
        direccion_envio = pedido_data.get('direccionEnvio', {})
        
        if direccion_envio.get('tipoEnvio') == 'retiro':
            envio_text = "RETIRO EN LOCAL"
            direccion_text = empresa.get('direccion', 'Dirección de tienda')
        else:
            envio_text = "ENVÍO A DOMICILIO"
            direccion_text = f"{direccion_envio.get('direccion_principal', '')}, {direccion_envio.get('ciudad', '')}"
        
        fecha_envio_header = Table(
            [[Paragraph("FECHA Y HORA DE EMISIÓN", section_title_style),
              Paragraph("ENVÍO:", section_title_style)]],
            colWidths=[3.65*inch, 3.65*inch]
        )
        fecha_envio_header.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#1e3a8a')),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.whitesmoke),
            ('PADDING', (0, 0), (-1, -1), 6),
        ]))
        story.append(fecha_envio_header)
        
        fecha_envio_data = [
            [fecha_emision.strftime("%d/%m/%Y %H:%M"), envio_text],
            ["", direccion_text]
        ]
        
        fecha_envio_table = Table(fecha_envio_data, colWidths=[3.65*inch, 3.65*inch])
        fecha_envio_table.setStyle(TableStyle([
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('FONTSIZE', (0, 0), (-1, -1), 8),
            ('PADDING', (0, 0), (-1, -1), 4),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ]))
        story.append(fecha_envio_table)
        story.append(Spacer(1, 0.15*inch))
        
        # ===== SECCIÓN: DETALLE DE PRODUCTOS =====
        productos_header = Table(
            [[Paragraph("DESCRIPCIÓN", section_title_style),
              Paragraph("CANTIDAD", section_title_style),
              Paragraph("PRECIO UNITARIO", section_title_style),
              Paragraph("VALOR TOTAL", section_title_style)]],
            colWidths=[3.5*inch, 1.2*inch, 1.3*inch, 1.3*inch]
        )
        productos_header.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#1e3a8a')),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.whitesmoke),
            ('PADDING', (0, 0), (-1, -1), 6),
            ('ALIGN', (1, 0), (-1, 0), 'CENTER'),
        ]))
        story.append(productos_header)
        
        # Items de productos
        simbolo_moneda = empresa.get('configuracion', {}).get('simboloMoneda', '$')
        productos_data = []
        
        for item in pedido_data.get('items', []):
            nombre = item.get('nombre', 'N/A')
            cantidad = item.get('cantidad', 0)
            precio = float(item.get('precioUnitario', 0))
            subtotal_item = cantidad * precio
            
            # Agregar detalles de talla/color
            detalles = []
            if item.get('talla'):
                detalles.append(f"Talla: {item['talla']}")
            if item.get('color'):
                if isinstance(item['color'], dict):
                    detalles.append(f"Color: {item['color'].get('color', 'N/A')}")
                else:
                    detalles.append(f"Color: {item['color']}")
            
            if detalles:
                nombre_completo = f"{nombre}\n({', '.join(detalles)})"
            else:
                nombre_completo = nombre
            
            productos_data.append([
                Paragraph(nombre_completo, info_value_style),
                str(cantidad),
                f"{simbolo_moneda}{precio:.2f}",
                f"{simbolo_moneda}{subtotal_item:.2f}"
            ])
        
        productos_table = Table(productos_data, colWidths=[3.5*inch, 1.2*inch, 1.3*inch, 1.3*inch])
        productos_table.setStyle(TableStyle([
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('FONTSIZE', (0, 0), (-1, -1), 8),
            ('PADDING', (0, 0), (-1, -1), 4),
            ('ALIGN', (1, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ]))
        story.append(productos_table)
        story.append(Spacer(1, 0.15*inch))
        
        # ===== SECCIÓN: TOTALES =====
        costos = pedido_data.get('costos', {})
        subtotal_val = float(costos.get('subtotal', 0))
        envio_val = float(costos.get('envio', 0))
        impuestos_val = float(costos.get('impuestos', 0))
        total_val = float(costos.get('total', 0))
        iva_porcentaje = empresa.get('configuracion', {}).get('iva', 15)
        
        # Crear tabla de totales alineada a la derecha
        totales_data = [
            ["", "", Paragraph("<b>SUBTOTAL</b>", info_label_style), f"{simbolo_moneda}{subtotal_val:.2f}"],
            ["", "", Paragraph("<b>COSTO DE ENVÍO</b>", info_label_style), f"{simbolo_moneda}{envio_val:.2f}"],
            ["", "", Paragraph(f"<b>IVA ({iva_porcentaje}%)</b>", info_label_style), f"{simbolo_moneda}{impuestos_val:.2f}"],
            ["", "", Paragraph("<b>VALOR TOTAL</b>", info_label_style), Paragraph(f"<b>{simbolo_moneda}{total_val:.2f}</b>", info_label_style)],
        ]
        
        totales_table = Table(totales_data, colWidths=[2.5*inch, 2*inch, 1.5*inch, 1.3*inch])
        totales_table.setStyle(TableStyle([
            ('GRID', (2, 0), (-1, -1), 0.5, colors.grey),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('PADDING', (2, 0), (-1, -1), 4),
            ('ALIGN', (2, 0), (2, -1), 'RIGHT'),
            ('ALIGN', (3, 0), (3, -1), 'CENTER'),
            ('BACKGROUND', (2, -1), (-1, -1), colors.HexColor('#e0e7ff')),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        story.append(totales_table)
        story.append(Spacer(1, 0.15*inch))
        
        # ===== SECCIÓN: FORMA DE PAGO =====
        pago_header = Table(
            [[Paragraph("FORMA DE PAGO", section_title_style)]],
            colWidths=[7.3*inch]
        )
        pago_header.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#1e3a8a')),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.whitesmoke),
            ('PADDING', (0, 0), (-1, -1), 6),
        ]))
        story.append(pago_header)
        
        metodo_pago = pedido_data.get('metodoPago', 'transferencia').upper()
        tipo_pago = pedido_data.get('tipoPago', 'completo')
        
        if tipo_pago == 'anticipo':
            metodo_text = f"{metodo_pago} - Anticipo 50%"
        else:
            metodo_text = f"{metodo_pago} - Pago Completo"
        
        pago_data = [
            [Paragraph("<b>MÉTODO</b>", info_label_style), metodo_text]
        ]
        
        pago_table = Table(pago_data, colWidths=[1.5*inch, 5.8*inch])
        pago_table.setStyle(TableStyle([
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('FONTSIZE', (0, 0), (-1, -1), 8),
            ('PADDING', (0, 0), (-1, -1), 4),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        story.append(pago_table)
        
        # Construir PDF
        doc.build(story)
        
        # Obtener el contenido del buffer
        buffer.seek(0)
        pdf_content = buffer.getvalue()
        buffer.close()
        
        # Subir a Cloudinary con descarga forzada
        nombre_archivo = f"factura_{pedido_data['_id'][-8:].upper()}_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        upload_result = cloudinary.uploader.upload(
            pdf_content,
            folder="facturas",
            resource_type="raw",
            public_id=nombre_archivo,
            format="pdf",
            type="upload",
            access_mode="public"
        )
        
        factura_url = upload_result['secure_url']
        
        current_app.logger.info(f"✅ Factura generada y subida: {factura_url}")
        
        return True, factura_url
        
    except Exception as e:
        current_app.logger.error(f"❌ Error al generar factura: {str(e)}")
        import traceback
        traceback.print_exc()
        return False, str(e)


def obtener_factura(pedido_id: str):
    """
    Obtiene la URL de la factura de un pedido.
    """
    try:
        col = get_pedidos_collection()
        pedido = col.find_one({"_id": ObjectId(pedido_id)})
        
        if not pedido:
            return jsonify({"ok": False, "msg": "Pedido no encontrado"}), 404
        
        factura_url = pedido.get("facturaUrl")
        
        if not factura_url:
            return jsonify({"ok": False, "msg": "El pedido no tiene factura generada"}), 404
        
        return jsonify({
            "ok": True,
            "facturaUrl": factura_url
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Error al obtener factura: {str(e)}")
        return jsonify({"ok": False, "msg": str(e)}), 500

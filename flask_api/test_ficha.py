# test_ficha.py
import base64
from flask_api.controlador.control_ficha_tecnica import generar_ficha_tecnica_prueba

if __name__ == "__main__":
    # ⚡ Datos ficticios para probar la ficha técnica
    ficha_fake = {
        "categoria": "Camiseta",
        "modelo": "CAM-20251002-ABCD",
        "descripcion": "Camiseta deportiva para hombre, manga corta, cuello redondo, algodón, diseño geométrico en blanco y negro.",
        "caracteristicas": {
            "tela": "Algodón",
            "color": "Blanco",
            "color_secundario": "Negro",
            "genero": "Hombre",
            "estilo": "Deportivo",
            "cuello": "Redondo",
            "mangas": "Corta",
            "acabado": "Costuras reforzadas"
        },
        "imagenes": {
            "delantera": "https://res.cloudinary.com/dcn5d4wbo/image/upload/v1759364001/CamisetaDelantera_ildkap.png",
            "posterior": "https://res.cloudinary.com/dcn5d4wbo/image/upload/v1759363999/CamisetaTrasera_yigesw.png",
            "acabado": "https://res.cloudinary.com/dcn5d4wbo/image/upload/v1759365270/ejemplo_camiseta_generada.png"
        },
        "piezas": [
            {"pieza": "Delantera", "cantidad": 1, "color": "Blanco"},
            {"pieza": "Posterior", "cantidad": 1, "color": "Negro"},
            {"pieza": "Mangas", "cantidad": 2, "color": "Blanco"},
            {"pieza": "Cuello", "cantidad": 1, "color": "Negro"}
        ],
        "insumos": [
            {"descripcion": "Hilo poliéster 120", "cantidad": "1 rollo", "color": "Negro"},
            {"descripcion": "Etiqueta interior", "cantidad": 1, "color": "N/A"},
            {"descripcion": "Tela principal", "cantidad": "1.2m", "color": "Blanco"}
        ],
        "logo": {
            "imagen": "https://res.cloudinary.com/dcn5d4wbo/image/upload/v1759365264/LogoHori_eb7nnz.png",
            "tamano": "Mediano",
            "ubicacion": "Frontal",
            "estilo": "Sublimado"
        },
        "especificaciones": [
            "Costuras reforzadas",
            "Acabados de alta calidad",
            "Prenda diseñada para uso deportivo"
        ]
    }

    print("⚡ Generando PDF de prueba...")
    pdf_b64 = generar_ficha_tecnica_prueba(ficha_fake)
    
    # Guardar en archivo local
    with open("ficha_prueba.pdf", "wb") as f:
        f.write(base64.b64decode(pdf_b64))

    print("✅ PDF generado: ficha_prueba.pdf")

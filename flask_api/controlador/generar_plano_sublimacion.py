# flask_api/controlador/generar_plano_sublimacion.py
import io, requests, os, math
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import cloudinary.uploader


# -----------------------------------------------------
# Función principal
# -----------------------------------------------------
def generar_plano_uv(mask_path, prenda_data, uv_layout_path=None):
    """
    Genera un plano 2D de sublimación real a partir del UV layout + máscara RGB.
    Cada canal (R,G,B) representa una zona distinta.
    """

    # === 1️⃣ Cargar la máscara RGB base ===
    mask = Image.open(mask_path).convert("RGB")

    # Usar tamaño real de la máscara (sin redimensionar)
    width, height = mask.size
    npmask = np.array(mask)

    # Crear lienzo base del mismo tamaño
    base = Image.new("RGBA", (width, height), (0, 0, 0, 0))

    # Guardar resolución usada (opcional)
    prenda_data["uv_resolution_real"] = [width, height]


    if uv_layout_path and uv_layout_path.endswith((".png", ".jpg")):
        try:
            uv_img = Image.open(uv_layout_path).convert("RGBA")
            if uv_img.size != (width, height):
                uv_img = uv_img.resize((width, height), Image.LANCZOS)
            base.alpha_composite(uv_img, (0, 0))
        except Exception as e:
            print("⚠️ No se pudo usar el UV layout:", e)


    # === 3️⃣ Función auxiliar: rellenar zonas RGB ===
    def fill_zone(channel, color_hex):
        mask_bin = (npmask[:, :, channel] > 128).astype(np.uint8) * 255
        mask_img = Image.fromarray(mask_bin, "L")
        color_layer = Image.new("RGBA", mask.size, color_hex)
        base.paste(color_layer, (0, 0), mask_img)

    # === 4️⃣ Rellenar colores según canales definidos en la máscara ===
    zones = prenda_data.get("colors", {})
    design_id = prenda_data.get("design_id", "base")

    channel_map = _get_channel_map(design_id)
    for zona, color_hex in zones.items():
        ch = channel_map.get(zona)
        if ch is not None:
            fill_zone(ch, color_hex)


    return base


def _get_channel_map(design_id):
    """
    Define qué canal RGB usa cada zona según el diseño.
    """
    maps = {
        "base": {"cuello": 0, "mangas": 1, "torso": 2},  # R,G,B
        "rayo": {"torso": 0, "franja": 1, "cuello": 2},
    }
    return maps.get(design_id, {"torso": 0, "mangas": 1, "cuello": 2})


# -----------------------------------------------------
# Subir a Cloudinary
# -----------------------------------------------------
def subir_plano_sublimacion(prenda_data, mask_path):
    """
    Genera el plano final combinando la máscara RGB con el UV layout.
    """
    from flask_api.controlador.generar_plano_sublimacion import generar_plano_uv

    # 1️⃣ Ruta local del UV layout
    uv_layout_path = os.path.join(os.path.dirname(mask_path), "uv_guia.png")

    # 2️⃣ Generar imagen PIL del plano
    plano_img = generar_plano_uv(mask_path, prenda_data, uv_layout_path=uv_layout_path)

    # 3️⃣ Reducir tamaño (para evitar límite de Cloudinary)
    max_size = (2048, 2048)
    plano_img.thumbnail(max_size, Image.LANCZOS)

    # 4️⃣ Convertir a buffer binario
    output = io.BytesIO()
    plano_img.save(output, format="PNG", optimize=True)
    output.seek(0)

    # 5️⃣ Subir a Cloudinary
    upload_result = cloudinary.uploader.upload(
        output,
        folder="disenos3d/plantillas",
        public_id=f"plano_{prenda_data['modelo']}",
        resource_type="image",
    )

    print(f"🧵 Plano de sublimación subido correctamente: {upload_result['secure_url']}")
    return upload_result["secure_url"]

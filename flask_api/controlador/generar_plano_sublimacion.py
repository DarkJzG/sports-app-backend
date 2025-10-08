# flask_api/controlador/generar_plano_sublimacion.py
import io
import requests
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageOps
import cloudinary.uploader

def aplicar_color_por_canal(mask_path, zones):
    """
    Colorea la máscara RGB según los colores definidos en 'zones'.
    """
    mask = Image.open(mask_path).convert("RGB")
    arr = np.array(mask)

    base = np.zeros_like(arr)
    for zona, data in zones.items():
        color_hex = data.get("color", "#FFFFFF").lstrip("#")
        rgb = tuple(int(color_hex[i:i+2], 16) for i in (0, 2, 4))
        channel = data.get("channel")
        if not channel:
            continue
        if channel == "R":
            base[(arr[:, :, 0] > 128) & (arr[:, :, 1] < 100) & (arr[:, :, 2] < 100)] = rgb
        elif channel == "G":
            base[(arr[:, :, 1] > 128) & (arr[:, :, 0] < 100) & (arr[:, :, 2] < 100)] = rgb
        elif channel == "B":
            base[(arr[:, :, 2] > 128) & (arr[:, :, 0] < 100) & (arr[:, :, 1] < 100)] = rgb
    return Image.fromarray(base.astype("uint8"), "RGB")


def generar_plano_sublimacion(prenda_data, mask_path):
    """
    Genera una plantilla 2D plana con colores, texturas, logos y textos.
    """
    zones = {}
    design_zones = prenda_data.get("colors", {})
    textures = prenda_data.get("textures", {})

    # Combinar canales y texturas
    for zona, color in design_zones.items():
        zones[zona] = {
            "color": color,
            "channel": _map_channel(zona),
            "texture": textures.get(zona)
        }

    # 1️⃣ Colorear base según máscara RGB
    base = aplicar_color_por_canal(mask_path, zones).convert("RGBA")

    # 2️⃣ Superponer texturas
    for zona, data in zones.items():
        tex_url = data.get("texture")
        if tex_url:
            try:
                tex_img = Image.open(io.BytesIO(requests.get(tex_url).content)).convert("RGBA")
                tex_img = tex_img.resize(base.size)
                base = Image.alpha_composite(base, tex_img)
            except Exception:
                continue

    draw = ImageDraw.Draw(base)

    # 3️⃣ Añadir logos (posición fija simulada)
    for logo in prenda_data.get("decals", []):
        url = logo.get("url")
        if not url:
            continue
        try:
            logo_img = Image.open(io.BytesIO(requests.get(url).content)).convert("RGBA")
            logo_img = logo_img.resize((300, 300))
            x, y = (1000, 400)  # Posición base fija o según tipo de zona
            base.alpha_composite(logo_img, (x, y))
        except Exception:
            pass

    # 4️⃣ Añadir textos
    for t in prenda_data.get("textDecals", []):
        txt = t.get("text", "")
        color = t.get("fill", "#000000")
        font = ImageFont.truetype("arial.ttf", 160)
        draw.text((1300, 1700), txt, fill=color, font=font)

    # 5️⃣ Guardar en memoria
    out = io.BytesIO()
    base.save(out, format="PNG")
    out.seek(0)
    return out


def _map_channel(zona_name):
    """
    Relaciona nombres de zonas con canales RGB (depende de tu máscara).
    """
    mapping = {
        "torso": "R",
        "mangas": "G",
        "cuello": "B",
        "franja": "G",
    }
    return mapping.get(zona_name, "R")


def subir_plano_sublimacion(prenda_data, mask_path):
    """
    Genera y sube la plantilla de sublimación a Cloudinary.
    """
    plano_io = generar_plano_sublimacion(prenda_data, mask_path)
    modelo = prenda_data.get("modelo", f"plano_{prenda_data.get('_id', '')}")
    upload = cloudinary.uploader.upload(
        plano_io,
        folder="disenos3d/plantillas",
        public_id=modelo,
        resource_type="image"
    )
    return upload["secure_url"]

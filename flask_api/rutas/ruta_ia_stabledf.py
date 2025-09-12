# flask_api/rutas/ruta_ia_stabledf.py
import requests
from flask import Blueprint, request, jsonify

ruta_ia_stable = Blueprint("ruta_ia_stable", __name__)

# Endpoint de Automatic1111
SD_API_URL = "http://127.0.0.1:7860/sdapi/v1/txt2img"


def build_prompt_from_user(data: dict):
    categoria = data.get("categoria", "camiseta")
    estilo = data.get("estilo", "deportivo")
    tela = data.get("tela", "poliéster")
    color_principal = data.get("color_principal", "blanco")
    color_secundario = data.get("color_secundario", "ninguno")
    color_terciario = data.get("color_terciario", "ninguno")
    mangas = data.get("mangas", "cortas")
    cuello = data.get("cuello", "redondo")
    patron = data.get("patron", "ninguno")
    talla = data.get("talla", "M")
    genero = data.get("genero", "unisex")

    descripcion = (
        f"{categoria.capitalize()} {estilo} de {tela}, "
        f"color principal {color_principal}"
        f"{', con detalles en ' + color_secundario if color_secundario != 'ninguno' else ''}"
        f"{', y acentos en ' + color_terciario if color_terciario != 'ninguno' else ''}, "
        f"mangas {mangas}, cuello {cuello}, "
        f"patrón {patron if patron != 'ninguno' else 'liso'}, "
        f"talla {talla}, {genero}."
    )

    prompt = (
        f"Front view, centered, high-quality mockup of a {estilo} {categoria}, "
        f"made of {tela}, primary color {color_principal}, "
        f"{'secondary color ' + color_secundario + ', ' if color_secundario != 'ninguno' else ''}"
        f"{'tertiary accents ' + color_terciario + ', ' if color_terciario != 'ninguno' else ''}"
        f"{mangas} sleeves, {cuello} neck, "
        f"{'pattern of ' + patron if patron != 'ninguno' else 'plain design'}, "
        f"studio lighting, plain white seamless background, sharp focus, no text, no logos, "
        "only the garment."
    )

    negative = "text, watermark, human, mannequin, logo text, blurry, deformed, extra arms, faces"

    return prompt, negative, descripcion


@ruta_ia_stable.route("/ia/generar_stable", methods=["POST"])
def generar_stable():
    try:
        # Recibe JSON desde frontend
        data = request.get_json(force=True)

        prompt, negative_prompt, descripcion = build_prompt_from_user(data)

        # Parámetros internos (no manipulables por usuario)
        payload = {
            "prompt": prompt,
            "negative_prompt": negative_prompt,
            "steps": 20,
            "width": 512,
            "height": 512,
            "cfg_scale": 7.5
        }

        # Llamada a Automatic1111
        response = requests.post(SD_API_URL, json=payload)
        r = response.json()

        image_base64 = r["images"][0]

        return jsonify({
            "ok": True,
            "image_base64": image_base64,
            "meta": {
                "descripcion": descripcion
            }
        })

    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 500

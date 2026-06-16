# flask_api/controlador/prompts_texturas/personalizado.py

from typing import Dict, List
from googletrans import Translator

translator = Translator()

def traducir_texto(texto: str) -> str:
    """Traduce ES → EN usando googletrans."""
    try:
        if not texto:
            return ""
        return translator.translate(texto, src="es", dest="en").text
    except Exception:
        return texto


def _build_color_phrase(colores: List[str]) -> str:
    """Construye una frase natural con la paleta limitada."""
    if not colores:
        return "a limited neutral color palette"

    if len(colores) == 1:
        return f"a limited palette in {colores[0]} tones"

    base = colores[0]
    accents = ", ".join(colores[1:])
    return f"{base} base with accents in {accents}"


def _build_direction_phrase(direccion: str) -> str:
    """Traduce horizontal/vertical a instrucciones útiles para la IA."""
    if not direccion:
        return ""

    d = direccion.lower()
    if "horizontal" in d:
        return "elements arranged in a soft horizontal flow"
    if "vertical" in d:
        return "elements arranged in vertical columns"
    return "balanced overall distribution of elements"


def build_prompt_personalizado(attr: Dict) -> str:
    """
    Genera un prompt preciso para crear texturas de IA.
    Traduciendo automáticamente a inglés todo lo que el usuario ingresa.
    """
    print("🎨 Entrando a build_prompt_personalizado con:", attr)

    # 1️⃣ Texto del usuario (ES → EN)
    custom_raw = (attr.get("custom") or "").strip()
    if not custom_raw:
        custom_raw = "formas abstractas"

    custom_en = traducir_texto(custom_raw)
    if not custom_en:
        custom_en = "abstract shapes"

    # 2️⃣ Colores (ya vienen en inglés desde el frontend)
    colores: List[str] = attr.get("colores") or ["gray", "white"]
    color_phrase = _build_color_phrase(colores)

    # 3️⃣ Dirección
    direction_phrase = _build_direction_phrase(attr.get("direccion", ""))

    # 4️⃣ Zona de la prenda
    zona = (attr.get("zona") or "").replace("_", " ")
    if zona:
        garment_context = f"for a sportswear garment {zona} area"
    else:
        garment_context = "for modern sportswear fabrics"

    # 5️⃣ Prompt final optimizado
    prompt = (
        f"Seamless repeating pattern featuring {custom_en}, "
        f"{color_phrase}, {direction_phrase}. "
        f"Clean, bold shapes, flat colors, no gradients, no logos, no text. "
        f"High-detail textile surface, perfectly tileable, "
        f"{garment_context}, studio lighting, high resolution. "
        f"User description (ES): \"{custom_raw}\"."
    )

    prompt = " ".join(prompt.split())

    print("🎨 Prompt final:", prompt)
    return prompt

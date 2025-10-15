from typing import Dict
from flask_api.componente.traducciones import TRADUCCIONES

def build_prompt_geometrico(attr: Dict) -> str:
    print("🧩 Entrando a build_prompt_geometrico con:", attr)

    try:
        colores = [c for c in attr.get("colores", []) if isinstance(c, str) and c.strip()]
        num_colores = len(colores)
        figura = attr.get("figura", "geometric shapes")
        escala = attr.get("escala", "medium").lower()       
        espaciado = attr.get("espaciado", "regular").lower() 
        superposicion = attr.get("superposicion", "flat").lower() 

        genero = attr.get("genero", "")
        cuello = attr.get("cuello", "")
        manga = attr.get("manga", "")
        tela = attr.get("tela", "")
        garment = f"high-end photorealistic sportswear t-shirt mockup for {genero}, with {cuello} neck and {manga} sleeves, made of {tela} fabric"

        if num_colores == 3:
            color_desc = f"{colores[0]} color base with {colores[1]} color main {figura} and {colores[2]} color accent details"
        elif num_colores == 4:
            color_desc = f"{colores[0]} color base, featuring {figura} in {colores[1]}, {colores[2]}, and {colores[3]} tones"
        elif num_colores >= 5:
            color_desc = f"{colores[0]} color base, with complex {figura} in multiple tones: {', '.join(map(str, colores[1:]))}"
        else:
            color_desc = f"geometric pattern with varied colors and {figura}"

        scale_desc = (
            "small-scale fine shapes" if "pequeña" in escala or "small" in escala
            else "large-scale wide shapes"
        )

        space_desc = (
            "tightly packed, minimal spacing" if "ajustado" in espaciado or "tight" in espaciado
            else "widely spaced, airy composition"
        )

        if superposicion == "flat":
            overlay_desc = "flat non-overlapping layout"
        elif superposicion == "layered":
            overlay_desc = "slightly overlapping layered layout for depth"
        elif superposicion == "fragmented":
            overlay_desc = "fragmented and dynamic composition, with broken shapes"
        else:
            overlay_desc = "balanced geometric arrangement"

        pattern_desc = f"{color_desc}, {scale_desc}, {space_desc}, {overlay_desc}"

        context = (
            "displayed on an invisible mannequin, "
            "perfect studio lighting, catalog style, "
            "sharp focus, plain light gray background, "
            "no logos, no text, hyper-detailed textile texture."
        )

        prompt = f"{garment}, {pattern_desc}, {context}"

        print("🟢 build_prompt_geometrico OK")
        print("🟢 Prompt generado:", prompt)
        return prompt

    except Exception as e:
        print("❌ Error dentro de build_prompt_geometrico:", e)
        raise


# =========================================
# 🇪🇸 Descripción en español
# =========================================
def descripcion_geometrico_es(attr: Dict) -> str:
    colores = [c for c in attr.get("colores", []) if isinstance(c, str) and c.strip()]
    figura = attr.get("figura", "figuras geométricas")
    escala = attr.get("escala", "")
    espaciado = attr.get("espaciado", "")
    superposicion = attr.get("superposicion", "")
    genero = attr.get("genero", "unisex")

    figura_es = TRADUCCIONES.get(figura, figura)
    colores_es = [TRADUCCIONES.get(c, c) for c in colores]
    escala_es = TRADUCCIONES.get(escala, escala)
    espaciado_es = TRADUCCIONES.get(espaciado, espaciado)
    superposicion_es = TRADUCCIONES.get(superposicion, superposicion)
    genero_es = TRADUCCIONES.get(genero, genero)

    base = f"Camiseta deportiva para {genero_es.lower()} con patrón geométrico de {figura_es}"
    if colores:
        base += f" en tonos {', '.join(colores_es)}"
    if escala:
        base += f", figuras de escala {escala_es}"
    if espaciado:
        base += f" y espaciado {espaciado_es}"
    if superposicion:
        base += f" con disposición {superposicion_es}"

    return base + "."
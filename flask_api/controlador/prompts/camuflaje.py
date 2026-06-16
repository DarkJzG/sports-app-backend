from typing import Dict
from flask_api.componente.traducciones import TRADUCCIONES


# =========================================
# 🎨 Prompt principal para patrón de camuflaje
# =========================================
def build_prompt_camuflaje(attr: Dict) -> str:
    print("🧩 Entrando a build_prompt_camuflaje con:", attr)

    try:
        # ========= 1️⃣ Datos base =========
        paleta = attr.get("paletaCamuflaje", "forest").lower()
        colores = [c for c in attr.get("colores", []) if isinstance(c, str) and c.strip()]
        tamano = attr.get("tamanoCamo", "medium").lower()
        estilo = attr.get("estiloCamo", "classic").lower()

        genero = attr.get("genero", "")
        cuello = attr.get("cuello", "")
        manga = attr.get("manga", "")
        tela = attr.get("tela", "")

        garment = (
            f"high-end photorealistic sportswear t-shirt mockup for {genero}, "
            f"with {cuello} neck and {manga} sleeves, made of {tela} fabric"
        )

        # ========= 2️⃣ Descripción de la paleta =========
        if paleta == "forest":
            palette_desc = "forest camouflage palette with olive green, brown and black tones"
        elif paleta == "desert":
            palette_desc = "desert camouflage palette with beige, tan and light brown tones"
        elif paleta == "urban":
            palette_desc = "urban camouflage palette with gray, white and black tones"
        elif paleta == "personalized":
            if colores:
                palette_desc = f"custom camouflage palette blending {', '.join(colores)} tones"
            else:
                palette_desc = "custom camouflage palette with mixed tones"
        else:
            palette_desc = "balanced camouflage palette blending neutral colors"

        # ========= 3️⃣ Tamaño del patrón =========
        if tamano == "small":
            size_desc = "fine small-scale pattern, micro camo style with detailed textures"
        elif tamano == "large":
            size_desc = "large-scale classic military pattern with broad blotches"
        else:
            size_desc = "medium-scale balanced camouflage texture"

        # ========= 4️⃣ Estilo del camuflaje =========
        if estilo == "classic":
            style_desc = "rounded organic shapes with smooth edges, classic military look"
        elif estilo == "digital":
            style_desc = "pixelated camouflage with square digital blocks"
        elif estilo == "fragmented":
            style_desc = "fragmented geometric pattern with angular and modern shapes"
        else:
            style_desc = "abstract camouflage with natural irregular shapes"

        # ========= 5️⃣ Contexto visual =========
        context = (
            "displayed on an invisible mannequin, perfect studio lighting, catalog style, "
            "sharp focus, plain light gray background, no logos, no text, hyper-detailed textile texture."
        )

        # ========= 6️⃣ Construcción final =========
        pattern_desc = f"{palette_desc}, {size_desc}, {style_desc}"
        prompt = f"{garment}, {pattern_desc}, {context}"

        print("🟢 build_prompt_camuflaje OK")
        print("🟢 Prompt generado:", prompt)
        return prompt

    except Exception as e:
        print("❌ Error dentro de build_prompt_camuflaje:", e)
        raise


# =========================================
# 🇪🇸 Descripción en español
# =========================================
def descripcion_camuflaje_es(attr: Dict) -> str:
    paleta = attr.get("paletaCamuflaje", "forest")
    colores = [c for c in attr.get("colores", []) if isinstance(c, str) and c.strip()]
    tamano = attr.get("tamanoCamo", "")
    estilo = attr.get("estiloCamo", "")
    genero = attr.get("genero", "unisex")

    # 🔹 Traducciones desde TRADUCCIONES global
    paleta_es = TRADUCCIONES.get(paleta, paleta)
    tamano_es = TRADUCCIONES.get(tamano, tamano)
    estilo_es = TRADUCCIONES.get(estilo, estilo)
    genero_es = TRADUCCIONES.get(genero, genero)
    colores_es = [TRADUCCIONES.get(c, c) for c in colores]

    base = f"Camiseta deportiva para {genero_es.lower()} con patrón de camuflaje estilo {estilo_es}"
    if paleta:
        base += f" con paleta {paleta_es}"
    if colores:
        base += f" en tonos {', '.join(colores_es)}"
    if tamano:
        base += f", de tamaño {tamano_es}"

    return base + "."

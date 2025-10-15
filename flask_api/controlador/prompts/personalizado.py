from typing import Dict
from flask_api.componente.traducciones import TRADUCCIONES


# =========================================
# 🎨 Prompt principal para diseño FULL PRINT
# =========================================
def build_prompt_personalizado(attr: Dict) -> str:
    print("🧩 Entrando a build_prompt_personalizado con:", attr)

    try:
        tipo = attr.get("tipoFullPrint", "objects").lower()

        # ======== Datos base ========
        genero = attr.get("genero", "")
        cuello = attr.get("cuello", "")
        manga = attr.get("manga", "")
        tela = attr.get("tela", "")
        garment = (
            f"high-end photorealistic sportswear t-shirt mockup for {genero}, "
            f"with {cuello} neck and {manga} sleeves, made of {tela} fabric"
        )

        # ====================================
        # 🟢 1️⃣ Modo “por objetos o elementos”
        # ====================================
        if tipo == "objects":
            motifs = attr.get("motifs", "") or "abstract shapes"
            style = attr.get("styleFP", "realistic style")
            distribution = attr.get("distributionFP", "balanced layout")
            colores = [c for c in attr.get("coloresExtraFP", []) if isinstance(c, str) and c.strip()]
            num_colores = len(colores)

            # --- 🔹 Descripción de color ---
            if num_colores == 2:
                color_desc = f"{colores[0]} base with {colores[1]} {motifs} motifs"
            elif num_colores >= 3:
                color_desc = (
                    f"{colores[0]} base featuring {motifs} motifs in {', '.join(colores[1:])} tones"
                )
            else:
                color_desc = f"vivid {motifs} elements"

            # --- 🔹 Descripción de distribución ---
            # Diferenciamos semánticamente la cantidad / disposición
            if "no repetition" in distribution:
                dist_desc = (
                    f"a single large {motifs} element centered on the shirt, "
                    f"prominent and detailed"
                )
            elif "random" in distribution:
                dist_desc = (
                    f"multiple {motifs} motifs randomly scattered across the shirt, "
                    f"creating a dynamic and energetic layout"
                )
            elif "spaced" in distribution:
                dist_desc = (
                    f"repeated {motifs} motifs evenly spaced over the fabric, "
                    f"balanced composition with visible separation"
                )
            else:
                dist_desc = f"{motifs} motifs distributed across the shirt"

            # --- 🔹 Composición general ---
            pattern_desc = (
                f"full print design composed of {dist_desc}, "
                f"{color_desc}, rendered in {style}"
            )

        # ====================================
        # 🟣 2️⃣ Modo “por textura o patrón”
        # ====================================
        elif tipo == "textures":
            texture_type = attr.get("textureType", "abstract texture")
            custom_texture = attr.get("customTexture", "").strip()
            colores = [c for c in attr.get("coloresExtraFP", []) if isinstance(c, str) and c.strip()]
            style = attr.get("styleFP", "realistic style")

            texture_desc = custom_texture if custom_texture else texture_type
            if len(colores) == 2:
                color_desc = f"{colores[0]} base with {colores[1]} {texture_desc}"
            elif len(colores) >= 3:
                color_desc = (
                    f"{colores[0]} base, with {texture_desc} in {', '.join(colores[1:])} tones"
                )
            else:
                color_desc = f"{texture_desc} over neutral background"

            pattern_desc = f"all-over texture pattern, {color_desc}, {style}"

        else:
            pattern_desc = "full surface artistic print covering the entire shirt"

        # ====================================
        # 🪶 Contexto visual
        # ====================================
        context = (
            "displayed on an invisible mannequin, perfect studio lighting, catalog style, "
            "sharp focus, plain light gray background, no logos, no text, hyper-detailed textile texture."
        )

        prompt = f"{garment}, {pattern_desc}, {context}"

        print("🟢 build_prompt_personalizado OK")
        print("🟢 Prompt generado:", prompt)
        return prompt

    except Exception as e:
        print("❌ Error dentro de build_prompt_personalizado:", e)
        raise



# =========================================
# 🇪🇸 Descripción en español
# =========================================
def descripcion_personalizado_es(attr: Dict) -> str:
    tipo = attr.get("tipoFullPrint", "objects").lower()
    genero = attr.get("genero", "unisex")

    # 🔹 Traducciones globales
    genero_es = TRADUCCIONES.get(genero, genero)
    tipo_es = TRADUCCIONES.get(tipo, tipo)
    style_es = TRADUCCIONES.get(attr.get("styleFP", ""), attr.get("styleFP", ""))
    distribution_es = TRADUCCIONES.get(attr.get("distributionFP", ""), attr.get("distributionFP", ""))
    texture_es = TRADUCCIONES.get(attr.get("textureType", ""), attr.get("textureType", ""))
    custom_texture_es = TRADUCCIONES.get(attr.get("customTexture", ""), attr.get("customTexture", ""))
    motifs_es = TRADUCCIONES.get(attr.get("motifs", ""), attr.get("motifs", ""))

    colores = [TRADUCCIONES.get(c, c) for c in attr.get("coloresExtraFP", []) if isinstance(c, str) and c.strip()]

    if tipo == "objects":
        base = f"Camiseta deportiva para {genero_es.lower()} con diseño full print de {motifs_es}"
        if colores:
            base += f" en tonos {', '.join(colores)}"
        if style_es:
            base += f", estilo {style_es}"
        if distribution_es:
            base += f" con distribución {distribution_es}"
    elif tipo == "textures":
        textura = custom_texture_es or texture_es
        base = f"Camiseta deportiva para {genero_es.lower()} con textura {textura}"
        if colores:
            base += f" en tonos {', '.join(colores)}"
        if style_es:
            base += f", estilo {style_es}"
    else:
        base = f"Camiseta deportiva full print para {genero_es.lower()} con diseño artístico personalizado"

    return base + "."

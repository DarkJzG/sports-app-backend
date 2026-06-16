from typing import Dict
from flask_api.componente.traducciones import TRADUCCIONES


# =========================================
# 🎨 Prompt principal para diseño SÓLIDO
# =========================================
def build_prompt_solido(attr: Dict) -> str:
    print("🧩 Entrando a build_prompt_solido con:", attr)

    try:
        # ========= 1️⃣ Datos base =========
        color1 = attr.get("color1", "white")
        color_cuello = attr.get("colorCuello", "")
        usar_color_unico = attr.get("usarColorUnicoCuello", True)

        genero = attr.get("genero", "")
        cuello = attr.get("cuello", "")
        manga = attr.get("manga", "")
        tela = attr.get("tela", "")

        garment = (
            f"high-end photorealistic sportswear t-shirt mockup for {genero}, "
            f"with {cuello} neck and {manga} sleeves, made of {tela} fabric"
        )

        # ========= 2️⃣ Descripción del color =========
        if usar_color_unico or not color_cuello:
            color_desc = f"solid {color1} color applied uniformly across torso, sleeves, and collar"
        else:
            color_desc = (
                f"main body in {color1} with collar and cuffs in contrasting {color_cuello}"
            )

        # ========= 3️⃣ Contexto visual =========
        context = (
            "displayed on an invisible mannequin, perfect studio lighting, catalog style, "
            "sharp focus, plain light gray background, no logos, no text, hyper-detailed textile texture."
        )

        # ========= 4️⃣ Prompt final =========
        prompt = f"{garment}, {color_desc}, {context}"

        print("🟢 build_prompt_solido OK")
        print("🟢 Prompt generado:", prompt)
        return prompt

    except Exception as e:
        print("❌ Error dentro de build_prompt_solido:", e)
        raise


# =========================================
# 🇪🇸 Descripción en español
# =========================================
def descripcion_solido_es(attr: Dict) -> str:
    color1 = attr.get("color1", "")
    color_cuello = attr.get("colorCuello", "")
    usar_color_unico = attr.get("usarColorUnicoCuello", True)
    genero = attr.get("genero", "unisex")

    # 🔹 Traducciones desde TRADUCCIONES global
    color1_es = TRADUCCIONES.get(color1, color1)
    color_cuello_es = TRADUCCIONES.get(color_cuello, color_cuello)
    genero_es = TRADUCCIONES.get(genero, genero)

    base = f"Camiseta deportiva para {genero_es.lower()} de color sólido {color1_es}"
    if not usar_color_unico and color_cuello:
        base += f" con cuello y puños en color {color_cuello_es}"

    return base + "."

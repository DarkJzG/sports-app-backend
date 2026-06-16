from typing import Dict
from flask_api.componente.traducciones import TRADUCCIONES


# =========================================
# 🎨 Prompt principal para diseño DOS TONOS
# =========================================
def build_prompt_dos_tonos(attr: Dict) -> str:
    print("🧩 Entrando a build_prompt_dos_tonos con:", attr)

    try:
        # ========= 1️⃣ Datos base =========
        color1 = attr.get("color1TwoTone", "white")
        color2 = attr.get("color2TwoTone", "black")
        division = attr.get("division", "horizontal").lower()

        genero = attr.get("genero", "")
        cuello = attr.get("cuello", "")
        manga = attr.get("manga", "")
        tela = attr.get("tela", "")

        garment = (
            f"high-end photorealistic sportswear t-shirt mockup for {genero}, "
            f"with {cuello} neck and {manga} sleeves, made of {tela} fabric"
        )

        # ========= 2️⃣ Tipo de división =========
        if division == "horizontal":
            division_desc = (
                f"divided horizontally with {color1} on the upper area and {color2} on the lower part"
            )
        elif division == "vertical":
            division_desc = (
                f"divided vertically with {color1} on the left side and {color2} on the right"
            )
        elif division == "diagonal":
            division_desc = (
                f"diagonal two-tone layout with {color1} upper-left and {color2} bottom-right"
            )
        elif division == "sleeves and torso":
            division_desc = (
                f"{color1} torso and {color2} sleeves and collar for a contrasting sporty style"
            )
        else:
            division_desc = f"two-tone pattern blending {color1} and {color2}"

        # ========= 3️⃣ Contexto visual =========
        context = (
            "displayed on an invisible mannequin, perfect studio lighting, catalog style, "
            "sharp focus, plain light gray background, no logos, no text, hyper-detailed textile texture."
        )

        # ========= 4️⃣ Prompt final =========
        prompt = f"{garment}, {division_desc}, {context}"

        print("🟢 build_prompt_dos_tonos OK")
        print("🟢 Prompt generado:", prompt)
        return prompt

    except Exception as e:
        print("❌ Error dentro de build_prompt_dos_tonos:", e)
        raise


# =========================================
# 🇪🇸 Descripción en español
# =========================================
def descripcion_dos_tonos_es(attr: Dict) -> str:
    color1 = attr.get("color1TwoTone", "")
    color2 = attr.get("color2TwoTone", "")
    division = attr.get("division", "")
    genero = attr.get("genero", "unisex")

    # 🔹 Traducciones desde TRADUCCIONES global
    color1_es = TRADUCCIONES.get(color1, color1)
    color2_es = TRADUCCIONES.get(color2, color2)
    division_es = TRADUCCIONES.get(division, division)
    genero_es = TRADUCCIONES.get(genero, genero)

    base = f"Camiseta deportiva para {genero_es.lower()} de dos tonos"
    if division_es:
        base += f" con división {division_es}"
    base += f", combinando {color1_es} y {color2_es}"

    return base + "."

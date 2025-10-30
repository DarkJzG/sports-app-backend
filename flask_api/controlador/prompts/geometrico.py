from typing import Dict
from flask_api.componente.traducciones import TRADUCCIONES

# flask_api/controlador/patrones/geometrico.py
from typing import Dict

def build_prompt_geometrico(attr: Dict) -> str:
    print("🧩 Entrando a build_prompt_geometrico con:", attr)

    try:
        # ====== 🟡 Datos base ======
        colores = [c for c in attr.get("colores", []) if isinstance(c, str) and c.strip()]
        num_colores = len(colores)
        figura = attr.get("figura", "geometric shapes").lower()
        escala = attr.get("escala", "medium").lower()
        espaciado = attr.get("espaciado", "regular").lower()
        superposicion = attr.get("superposicion", "flat").lower()

        genero = attr.get("genero", "")
        cuello = attr.get("cuello", "")
        manga = attr.get("manga", "")
        tela = attr.get("tela", "")

        # ====== 🩳 Descripción del modelo base ======
        garment = (
            f"high-end photorealistic sportswear t-shirt mockup for {genero}, "
            f"with {cuello} neck and {manga} sleeves, made of {tela} performance fabric, "
            f"showing realistic textile folds and fine fiber texture."
        )

        # ====== 🎨 Colores y relación visual ======
        if num_colores == 2:
            color_desc = (
                f"The entire shirt is coated in a solid {colores[0]} base tone, "
                f"with geometric {figura} printed in a contrasting {colores[1]}."
            )
        elif num_colores == 3:
            color_desc = (
                f"The shirt features a {colores[0]} background, "
                f"with main {figura} shapes in {colores[1]} and subtle accent fragments in {colores[2]}."
            )
        elif num_colores >= 4:
            color_desc = (
                f"A dynamic composition with a {colores[0]} base tone, "
                f"and {figura} in multi-tonal palette of {', '.join(colores[1:])}, "
                f"creating vibrant contrasts and visual depth."
            )
        else:
            color_desc = f"Full-shirt geometric pattern with bright, varied colors harmoniously combined."

        # ====== ⚙️ Escala ======
        if "small" in escala or "peque" in escala:
            scale_desc = "tiny and dense geometric elements forming a detailed texture"
        elif "large" in escala or "grande" in escala:
            scale_desc = "large bold geometric figures clearly visible"
        else:
            scale_desc = "medium-scale geometric shapes evenly distributed"

        # ====== ⚙️ Espaciado ======
        if "tight" in espaciado or "ajustado" in espaciado:
            spacing_desc = "minimal spacing between shapes for compact coverage"
        elif "wide" in espaciado or "amplio" in espaciado:
            spacing_desc = "wide spacing with clear separation between elements"
        else:
            spacing_desc = "regular spacing maintaining balanced rhythm across the surface"

        # ====== ⚙️ Superposición / profundidad ======
        if "layer" in superposicion:
            layering_desc = "slightly overlapping and layered fragments adding sense of depth and motion"
        elif "fragment" in superposicion:
            layering_desc = "fragmented, interlocking shapes producing a dynamic shattered effect"
        else:
            layering_desc = "flat, non-overlapping layout emphasizing clean geometry"


        # ====== 🧩 Descripción del patrón ======
        pattern_desc = (
            f"{color_desc} "
            f"The {figura} composition covers the entire garment, including torso, sleeves, and collar, "
            f"with {scale_desc}, {spacing_desc}, {layering_desc}, and randomly oriented figures creating spontaneous arrangement. "
            f"The result is a modern and dynamic sportswear aesthetic, highly intricate and eye-catching visual layout."
        )

        # ====== 🌤️ Contexto fotográfico ======
        context = (
            "Displayed on an invisible mannequin under soft studio light, "
            "catalog presentation, sharp focus, light gray background, "
            "high-detail fabric texture, no text, no logos, professional product photography."
        )

        # ====== 🧠 Construcción final ======
        prompt = f"{garment} {pattern_desc} {context}"

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
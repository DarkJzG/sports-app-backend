from typing import Dict
from flask_api.componente.traducciones import TRADUCCIONES

def build_prompt_abstracto(attr: Dict) -> str:
    print("🎨 Entrando a build_prompt_abstracto con:", attr)

    try:
        # 1. Atributos que selecciona el usuario
        colores = [c for c in attr.get("colores", []) if isinstance(c, str) and c.strip()]
        num_colores = len(colores)
        estilo = attr.get("estiloArtistico", "abstract art") 
        intensidad = attr.get("intensidad", "moderate").lower() 
        cobertura = attr.get("cobertura", "full").lower()        

        genero = attr.get("genero", "")
        cuello = attr.get("cuello", "")
        manga = attr.get("manga", "")
        tela = attr.get("tela", "")

        garment = (
            f"high-end photorealistic sportswear t-shirt mockup for {genero}, "
            f"with {cuello} neck and {manga} sleeves, made of {tela} fabric"
        )

        # 2. Descripción del estilo artístico
        if estilo == "brush strokes":
            style_desc = "artistic brush strokes with expressive paint textures"
        elif estilo == "paint splatter":
            style_desc = "dynamic paint splatter effect, conveying energy and motion"
        elif estilo == "fluid art":
            style_desc = "fluid art effect with smooth watercolor-like transitions"
        elif estilo == "smoke effect":
            style_desc = "ethereal smoke-like effect with soft diffusion and transparency"
        else:
            style_desc = "artistic abstract texture blending colors organically"

        # 3. Colores
        if num_colores == 2:
            color_desc = f"applied on a {colores[0]} base color. The entire artistic pattern uses {colores[1]} as the single primary style hue."
        elif num_colores == 3:
            color_desc = f"applied on a {colores[0]} base color. The pattern utilizes {colores[1]} as the primary style hue, with {colores[2]} as a strong complementary accent."
        elif num_colores == 4:
            color_desc = f"applied on a {colores[0]} base color. The pattern utilizes {colores[1]} as the primary style hue, with {colores[2]} and {colores[3]} as complementary accents"   
        else:
            color_desc = "with mixed tones and soft gradients"

        # 4. Intensidad y cobertura
        if intensidad == "subtle":
            intensity_desc = "subtle and soft contrast"
        elif intensidad == "bold":
            intensity_desc = "bold, high-contrast artistic appearance"
        else:
            intensity_desc = "moderate artistic intensity"

        if cobertura == "full":
            coverage_desc = "covering the entire shirt surface, including torso and sleeves"
        elif cobertura == "partial":
            coverage_desc = "applied diffusely across scattered zones"
        else:
            coverage_desc = "balanced coverage across the garment"

        # 5. Contexto visual
        context = (
            "displayed on an invisible mannequin, perfect studio lighting, catalog style, "
            "sharp focus, plain light gray background, no logos, no text, hyper-detailed textile texture."
        )

        # 6. Construcción final
        pattern_desc = f"{style_desc}, {color_desc}, {intensity_desc}, {coverage_desc}"
        prompt = f"{garment}, {pattern_desc}, {context}"

        print("🟢 build_prompt_abstracto OK")
        print("🟢 Prompt generado:", prompt)
        return prompt

    except Exception as e:
        print("❌ Error dentro de build_prompt_abstracto:", e)
        raise


# 🇪🇸 Descripción en español
def descripcion_abstracto_es(attr: Dict) -> str:
    colores = [c for c in attr.get("colores", []) if isinstance(c, str) and c.strip()]
    estilo = attr.get("estiloArtistico", "arte abstracto")
    intensidad = attr.get("intensidad", "")
    cobertura = attr.get("cobertura", "")
    genero = attr.get("genero", "unisex")


    estilo_es = TRADUCCIONES.get(estilo, estilo)
    intensidad_es = TRADUCCIONES.get(intensidad, intensidad)
    cobertura_es = TRADUCCIONES.get(cobertura, cobertura)
    colores_es = [TRADUCCIONES.get(c, c) for c in colores]
    genero_es = TRADUCCIONES.get(genero, genero)

    base = f"Camiseta deportiva para {genero_es.lower()} con diseño artístico tipo {estilo_es}"
    if colores_es:
        if len(colores_es) > 1:
            base += f" en tonos {', '.join(colores_es[:-1])} y {colores_es[-1]}"
        else:
            base += f" en tono {colores_es[0]}"
    if intensidad_es:
        base += f", de intensidad {intensidad_es}"
    if cobertura_es:
        base += f" y cobertura {cobertura_es}"

    return base + "."

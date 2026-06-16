from typing import Dict
from flask_api.componente.traducciones import TRADUCCIONES


# =========================================
# 🎨 Prompt principal para diseño de rayas
# =========================================
from typing import Dict

def build_prompt_rayas(attr: Dict) -> str:
    print("🧩 Entrando a build_prompt_rayas con:", attr)

    try:
        # ========= 1️⃣ Datos base =========
        colores = [c for c in attr.get("colores", []) if isinstance(c, str) and c.strip()]
        base_color = colores[0] if len(colores) > 0 else "white"
        stripe_color = colores[1] if len(colores) > 1 else "black"

        direccion = attr.get("direccion", "horizontal").lower()
        grosor = attr.get("grosor", "medium").lower()
        num_rayas_input = str(attr.get("numRayas", "random")).lower() # Usar un nombre diferente para evitar conflicto
        cobertura = attr.get("coberturaRayas", "full").lower()

        genero = attr.get("genero", "")
        cuello = attr.get("cuello", "")
        manga = attr.get("manga", "")
        tela = attr.get("tela", "")

        garment = (
            f"high-end photorealistic sportswear t-shirt mockup for {genero}, "
            f"with {cuello} neck and {manga} sleeves, made of {tela} fabric"
        )

        # ========= 2️⃣ Dirección =========
        if direccion == "horizontal":
            dir_desc = "horizontal stripe pattern reminiscent of classic football jerseys"
        elif direccion == "vertical":
            dir_desc = "vertical stripe pattern inspired by basketball uniforms"
        else:
            dir_desc = "diagonal or irregular stripe composition"

        # ========= 3️⃣ Grosor (Ajustado para interacción con num_rayas) =========
        thick_desc_base = ""
        if grosor == "thin":
            thick_desc_base = "thin elegant stripes for a refined appearance"
        elif grosor == "thick":
            thick_desc_base = "bold thick stripes for a striking and modern look"
        else: # medium
            thick_desc_base = "medium-width stripes for balanced aesthetics"

        # ========= 4️⃣ Número de rayas (Mejorado para 3, 5, 7 y random) =========
        count_desc = ""
        if num_rayas_input == "random":
            count_desc = "a dynamic and random number of stripes"
        elif num_rayas_input in ["3", "5", "7"]:
            # Combinamos la descripción del grosor con el número de rayas para mayor claridad
            if grosor == "thin":
                count_desc = f"{thick_desc_base}, with exactly {num_rayas_input} clearly defined stripes evenly distributed"
            elif grosor == "thick":
                count_desc = f"{thick_desc_base}, featuring {num_rayas_input} prominent stripes evenly distributed"
            else: # medium
                count_desc = f"{thick_desc_base}, with {num_rayas_input} well-defined stripes evenly distributed"
        else:
            # Fallback para otros números específicos si los hubiera
            count_desc = f"approximately {num_rayas_input} visible stripes evenly distributed"

        # Si ya hemos incorporado thick_desc_base en count_desc, no lo repetimos.
        # Si num_rayas_input es "random", mantenemos la descripción de grosor separada.
        if num_rayas_input != "random":
            thick_desc = "" # Ya está cubierto en count_desc
        else:
            thick_desc = thick_desc_base # Se mantiene si es random


        # ========= 5️⃣ Cobertura =========
        if cobertura == "full":
            coverage_desc = "covering the entire shirt surface including torso and sleeves"
        elif cobertura == "chest":
            coverage_desc = "limited to the chest area with plain sleeves and back"
        else:
            coverage_desc = "balanced coverage across the main torso"

        # ========= 6️⃣ Colores =========
        color_desc = (
            f"featuring {stripe_color} stripes on a {base_color} base"
        )

        # ========= 7️⃣ Contexto visual =========
        context = (
            "displayed on an invisible mannequin, perfect studio lighting, catalog style, "
            "sharp focus, plain light gray background, no logos, no text, hyper-detailed textile texture."
        )

        # ========= 8️⃣ Construcción final =========
        # Ajustamos el orden y la inclusión de thick_desc
        pattern_elements = [dir_desc, color_desc]
        if thick_desc: # Si thick_desc no se incluyó en count_desc, lo añadimos
            pattern_elements.append(thick_desc)
        pattern_elements.append(count_desc)
        pattern_elements.append(coverage_desc)

        pattern_desc = ", ".join(filter(None, pattern_elements)) # Filtramos elementos vacíos
        
        prompt = f"{garment}, {pattern_desc}, {context}"

        print("🟢 build_prompt_rayas OK")
        print("🟢 Prompt generado:", prompt)
        return prompt

    except Exception as e:
        print("❌ Error dentro de build_prompt_rayas:", e)
        raise

# Descripción en español
def descripcion_rayas_es(attr: Dict) -> str:
    colores = [c for c in attr.get("colores", []) if isinstance(c, str) and c.strip()]
    base_color = colores[0] if len(colores) > 0 else "white"
    stripe_color = colores[1] if len(colores) > 1 else "black"

    direccion = attr.get("direccion", "")
    grosor = attr.get("grosor", "")
    num_rayas = str(attr.get("numRayas", "random"))
    cobertura = attr.get("coberturaRayas", "")
    genero = attr.get("genero", "unisex")

    # 🔹 Traducciones desde componente global
    direccion_es = TRADUCCIONES.get(direccion, direccion)
    grosor_es = TRADUCCIONES.get(grosor, grosor)
    cobertura_es = TRADUCCIONES.get(cobertura, cobertura)
    genero_es = TRADUCCIONES.get(genero, genero)
    base_color_es = TRADUCCIONES.get(base_color, base_color)
    stripe_color_es = TRADUCCIONES.get(stripe_color, stripe_color)

    base = f"Camiseta deportiva para {genero_es.lower()} con diseño de rayas {direccion_es}"
    base += f" en color base {base_color_es} y rayas {stripe_color_es}"

    if grosor:
        base += f" de grosor {grosor_es}"
    if num_rayas != "aleatorio":
        base += f", con {num_rayas} rayas visibles"
    elif num_rayas == "aleatorio":
        base += ", con número aleatorio de rayas"
    if cobertura:
        base += f" y cobertura {cobertura_es}"

    return base + "."

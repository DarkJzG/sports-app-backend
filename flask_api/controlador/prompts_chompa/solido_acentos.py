# flask_api/controlador/prompts_chompa/solido_acentos.py
from typing import Dict
from flask_api.componente.traducciones import TRADUCCIONES


def build_prompt_solido_acentos(attr: Dict) -> str:
    """
    Camino 1: Chompa de color sólido con detalles en color de acento.
    Soporta:
      - hoodie con capucha
      - sweatshirt sin capucha
      - zip-up jacket con o sin capucha
    """
    print("🧥 Entrando a build_prompt_solido_acentos con:", attr)
    
    try:
        tipo_chompa = attr.get("tipoChompa", "hoodie")     # "hoodie" | "jacket" | "sweatshirt"
        capucha = attr.get("capucha", "Yeah")              # "Yeah" | "No"
        bolsillos = attr.get("bolsillos", "kangaroo")      # "Kangaroo" | "sides" | "none"
        tela = attr.get("tela", "cotton")
        genero = attr.get("genero", "unisex")

        color_base = attr.get("colorBase", "black")
        color_acentos = attr.get("colorAcentos", "neon yellow")

        # === Tipo de prenda y cuello/capucha ===
        if tipo_chompa == "jacket":
            if capucha == "Yeah":
                garment_type = "zip-up jacket with hood"
                hood_desc = "with hood"
                has_hood = True
            else:
                garment_type = "zip-up jacket with high collar, no hood"
                hood_desc = "with high collar, without hood"
                has_hood = False
        else:
            if capucha == "Yeah":
                garment_type = "pullover hoodie"
                hood_desc = "with hood"
                has_hood = True
            else:
                garment_type = "pullover sweatshirt with high collar"
                hood_desc = "with high collar, without hood"
                has_hood = False

        # === Bolsillos ===
        if bolsillos.lower() == "kangaroo":
            pocket_desc = "with a large kangaroo pocket on the front"
        elif bolsillos.lower() in ["sides", "laterales"]:
            pocket_desc = "with side pockets"
        else:
            pocket_desc = "without pockets"

        # === Base de la prenda ===
        garment = (
            f"high-end photorealistic sportswear {garment_type} mockup for {genero}, "
            f"{hood_desc}, {pocket_desc}, made of {tela} fabric"
        )

        # === Color sólido base ===
        if has_hood:
            base_zones = "covering the body, sleeves, hood and pockets uniformly"
        else:
            base_zones = "covering the body, sleeves and pockets uniformly, no hood"

        design_desc = (
            f"The entire {garment_type} is {color_base} as the solid base color, "
            f"{base_zones}. "
        )
        if not has_hood:
            design_desc += " This design must NOT include any hood or hood shapes, only a high collar. "

        # === Detalles de acentos ===
        if tipo_chompa == "jacket":
            accent_targets = ["zipper", "zipper pull", "pocket edges"]
            if has_hood:
                accent_targets.append("hood drawstrings")
        else:
            accent_targets = ["pocket edges", "ribbing on cuffs and hem"]
            if has_hood:
                accent_targets.append("hood drawstrings")

        accent_list = ", ".join(accent_targets)
        accent_desc = f"{color_acentos} accent details on: {accent_list}. "

        # === Contexto visual ===
        context = (
            "displayed on an invisible mannequin, perfect studio lighting, catalog style, "
            "sharp focus, plain light gray background, no text, hyper-detailed textile texture, "
            "athletic fit, modern sportswear design."
        )

        prompt = f"{garment}, {design_desc}{accent_desc}{context}"

        print("🟢 build_prompt_solido_acentos OK")
        print("🟢 Prompt generado:", prompt)
        return prompt

    except Exception as e:
        print("❌ Error en build_prompt_solido_acentos:", e)
        raise


def descripcion_solido_acentos_es(attr: Dict) -> str:

    tipo_chompa = attr.get("tipoChompa", "sudadera")
    capucha = attr.get("capucha", "si")
    bolsillos = attr.get("bolsillos", "canguro")
    color_base = attr.get("colorBase", "")
    color_acentos = attr.get("colorAcentos", "")
    genero = attr.get("genero", "unisex")

    print("🟢 Entrando a descripcion_solido_acentos_es con:", attr)
    
    # Traducciones
    color_base_es = TRADUCCIONES.get(color_base, color_base)
    color_acentos_es = TRADUCCIONES.get(color_acentos, color_acentos)
    genero_es = TRADUCCIONES.get(genero, genero)
    
    # Tipo de prenda
    if tipo_chompa == "sudadera":
        tipo_desc = "sudadera" if capucha == "si" else "buzo"
    else:
        tipo_desc = "chaqueta deportiva"
    
    if bolsillos == "Canguro":
        bolsillo_desc = "y bolsillo canguro"
    elif bolsillos == "Laterales":
        bolsillo_desc = "y bolsillos laterales"
    else:
        bolsillo_desc = "sin bolsillos"

    if capucha == "Sí":
        capucha_desc = "con capucha"
    elif capucha == "No":
        capucha_desc = "sin capucha"
    
    base = (
        f"{tipo_desc.capitalize()} {capucha_desc} para {genero_es.lower()} "
        f"de color {color_base_es.lower()} con detalles en {color_acentos_es.lower()}"
    )
    
    base += f" {bolsillo_desc}"
    
    print("🟢 Descripción generada exitosamente")
    return base + "."

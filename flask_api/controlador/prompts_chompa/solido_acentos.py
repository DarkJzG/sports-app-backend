# flask_api/controlador/prompts_chompa/solido_acentos.py
from typing import Dict
from flask_api.componente.traducciones import TRADUCCIONES


def build_prompt_solido_acentos(attr: Dict) -> str:
    """
    Camino 1: Chompa de color sólido con detalles en color de acento
    """
    print("🧥 Entrando a build_prompt_solido_acentos con:", attr)
    
    try:
        # Datos estructurales
        tipo_chompa = attr.get("tipoChompa", "hoodie")  # sudadera/chaqueta → hoodie/jacket
        capucha = attr.get("capucha", "Yeah")  # si/no → Yeah/no
        bolsillos = attr.get("bolsillos", "kangaroo")  # canguro/laterales/sin_bolsillos
        tela = attr.get("tela", "cotton")
        genero = attr.get("genero", "unisex")
        
        # Colores
        color_base = attr.get("colorBase", "black")
        color_acentos = attr.get("colorAcentos", "neon yellow")
        
        # Construcción del tipo de prenda
        if tipo_chompa == "jacket":
            garment_type = "zip-up jacket"
        else:
            garment_type = "pullover hoodie" if capucha == "Yeah" else "pullover sweatshirt"
        
        # Descripción de capucha
        hood_desc = "with hood" if capucha == "Yeah" else "without hood"
        
        # Descripción de bolsillos
        if bolsillos == "kangaroo":
            pocket_desc = "with large kangaroo pocket on front"
        elif bolsillos == "sides":
            pocket_desc = "with side pockets"
        else:
            pocket_desc = "without pockets"
        
        # Base de la prenda
        garment = (
            f"high-end photorealistic sportswear {garment_type} mockup for {genero}, "
            f"{hood_desc}, {pocket_desc}, made of {tela} fabric"
        )
        
        # Descripción del diseño sólido con acentos
        design_desc = (
            f"The entire {garment_type} is {color_base} as the solid base color, "
            f"covering the body, sleeves, hood, and pockets uniformly. "
        )
        
        # Detalles de acentos
        if tipo_chompa == "jacket":
            accent_desc = (
                f"{color_acentos} accent details on: zipper, zipper pull, drawstrings, "
                f"and pocket edges. "
            )
        else:
            if capucha == "Yeah":
                accent_desc = (
                    f"{color_acentos} accent details on: hood drawstrings, "
                    f"pocket edges, ribbing on cuffs and hem."
                )
            else:
                accent_desc = (
                    f"{color_acentos} accent details on: pocket edges, "
                    f"ribbing on cuffs and hem. "
                )
        
        # Contexto visual
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
    """Descripción en español del diseño sólido con acentos"""
    tipo_chompa = attr.get("tipoChompa", "sudadera")
    capucha = attr.get("capucha", "si")
    bolsillos = attr.get("bolsillos", "canguro")
    color_base = attr.get("colorBase", "")
    color_acentos = attr.get("colorAcentos", "")
    genero = attr.get("genero", "unisex")
    
    # Traducciones
    color_base_es = TRADUCCIONES.get(color_base, color_base)
    color_acentos_es = TRADUCCIONES.get(color_acentos, color_acentos)
    genero_es = TRADUCCIONES.get(genero, genero)
    
    # Tipo de prenda
    if tipo_chompa == "sudadera":
        tipo_desc = "sudadera" if capucha == "si" else "buzo"
    else:
        tipo_desc = "chaqueta deportiva"
    
    # Descripción de bolsillos
    if bolsillos == "canguro":
        bolsillo_desc = "bolsillo canguro"
    elif bolsillos == "sides":
        bolsillo_desc = "bolsillos laterales"
    else:
        bolsillo_desc = "sin bolsillos"
    
    base = (
        f"{tipo_desc.capitalize()} para {genero_es.lower()} "
        f"de color {color_base_es.lower()} con detalles en {color_acentos_es.lower()}"
    )
    
    if capucha == "Yeah":
        base += ", con capucha"
    
    base += f", {bolsillo_desc}"
    
    return base + "."

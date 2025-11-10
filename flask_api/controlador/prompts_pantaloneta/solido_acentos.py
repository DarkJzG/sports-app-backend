# flask_api/controlador/prompts_pantaloneta/solido_acentos.py
from typing import Dict
from flask_api.componente.traducciones import TRADUCCIONES


def build_prompt_solido_acentos(attr: Dict) -> str:
    """
    Camino 1: Pantaloneta de color sólido con detalles en color de acento
    """
    print("🩳 Entrando a build_prompt_solido_acentos con:", attr)
    
    try:
        # Datos estructurales
        largo = attr.get("largo", "half")  # corto/medio/largo → short/medium/long
        bolsillos = attr.get("bolsillos", "side pockets with zipper")
        cordon = attr.get("cordon", "visible")  # visible/interno → visible/internal
        tela = attr.get("tela", "polyester")
        genero = attr.get("genero", "unisex")
        
        # Colores
        color_base = attr.get("colorBase", "black")
        color_acentos = attr.get("colorAcentos", "neon yellow")
        
        # Construcción del tipo de prenda según el largo
        if largo == "short":
            garment_type = "short athletic running shorts"
            length_desc = "above mid-thigh length, running style"
        elif largo == "half":
            garment_type = "mid-length athletic shorts"
            length_desc = "at mid-thigh, soccer/tennis style"
        else:  # largo
            garment_type = "long athletic basketball shorts"
            length_desc = "just above knee length, basketball style"
        
        # Descripción de bolsillos
        if bolsillos == "lateral_zip":
            pocket_desc = "with side zipper pockets"
        elif bolsillos == "sides_without_zip":
            pocket_desc = "with simple side pockets"
        else:  # sin_bolsillos
            pocket_desc = "without pockets, minimalist design"
        
        # Descripción del cordón
        if cordon == "visible":
            drawstring_desc = "with visible external drawstring at waistband"
        else:
            drawstring_desc = "with internal hidden drawstring"
        
        # Base de la prenda
        garment = (
            f"high-end photorealistic sportswear {garment_type} mockup for {genero}, "
            f"{length_desc}, {pocket_desc}, {drawstring_desc}, "
            f"made of {tela} fabric, elastic waistband"
        )
        
        # Descripción del diseño sólido con acentos
        design_desc = (
            f"The entire shorts are {color_base} as the solid base color, "
            f"covering the body uniformly from waistband to hem. "
        )
        
        # Detalles de acentos
        accent_desc = (
            f"{color_acentos} accent details on: drawstring, "
            f"zipper pulls (if applicable), waistband stripe, "
        )
        
        # Contexto visual
        context = (
            "on invisible mannequin, perfect studio lighting, catalog style, "
            "sharp focus, plain light gray background, no text, hyper-detailed textile texture, "
            "modern athletic design, professional sportswear presentation."
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
    largo = attr.get("largo", "medio")
    bolsillos = attr.get("bolsillos", "laterales_zip")
    color_base = attr.get("colorBase", "")
    color_acentos = attr.get("colorAcentos", "")
    genero = attr.get("genero", "unisex")
    
    # Traducciones
    color_base_es = TRADUCCIONES.get(color_base, color_base)
    color_acentos_es = TRADUCCIONES.get(color_acentos, color_acentos)
    genero_es = TRADUCCIONES.get(genero, genero)
    
    # Tipo de largo
    if largo == "corto":
        largo_desc = "corta estilo running"
    elif largo == "medio":
        largo_desc = "media estilo fútbol"
    else:
        largo_desc = "larga estilo básquet"
    
    # Descripción de bolsillos
    if bolsillos == "laterales_zip":
        bolsillo_desc = "bolsillos laterales con zipper"
    elif bolsillos == "laterales_sin_zip":
        bolsillo_desc = "bolsillos laterales simples"
    else:
        bolsillo_desc = "sin bolsillos"
    
    base = (
        f"Pantaloneta deportiva {largo_desc} para {genero_es.lower()} "
        f"de color {color_base_es.lower()} con detalles en {color_acentos_es.lower()}, "
        f"{bolsillo_desc}"
    )
    
    return base + "."

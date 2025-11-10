# flask_api/controlador/prompts_pantalon/solido_acentos.py
from typing import Dict
from flask_api.componente.traducciones import TRADUCCIONES


def build_prompt_solido_acentos(attr: Dict) -> str:
    """
    Camino 1: Pantalón de color sólido con detalles en color de acento
    """
    print("👖 Entrando a build_prompt_solido_acentos con:", attr)
    
    try:
        # Datos estructurales
        tipo_corte = attr.get("tipoCorte", "jogger")  # jogger/recto
        tipo_tobillo = attr.get("tipoTobillo", "elastic")  # elastico/suelto → elastic/loose
        bolsillos = attr.get("bolsillos", "side pockets with zipper")
        tela = attr.get("tela", "polyester")
        genero = attr.get("genero", "unisex")
        
        # Colores
        color_base = attr.get("colorBase", "black")
        color_acentos = attr.get("colorAcentos", "red")
        
        # Construcción del tipo de prenda
        if tipo_corte == "joggers":
            garment_type = "athletic jogger pants"
            fit_desc = "tapered fit with athletic cut"
        else:  # recto
            garment_type = "straight-leg athletic pants"
            fit_desc = "regular straight fit"
        
        # Descripción de tobillo
        if tipo_tobillo == "elastic":
            ankle_desc = "with ribbed elastic cuffs at ankles"
        else:  # loose
            ankle_desc = "with loose hem at ankles"
        
        # Descripción de bolsillos
        if bolsillos == "lateral_zip":
            pocket_desc = "with side pockets featuring zipper closures"
        elif bolsillos == "sides_without_zip":
            pocket_desc = "with simple side pockets"
        else:  # without_pockets
            pocket_desc = "without pockets, minimalist design"
        
        # Base de la prenda
        garment = (
            f"high-end photorealistic sportswear {garment_type} mockup for {genero}, "
            f"{fit_desc}, {ankle_desc}, {pocket_desc}, made of {tela} fabric"
        )
        
        # Descripción del diseño sólido con acentos
        design_desc = (
            f"The entire pants are {color_base} as the solid base color, "
            f"covering the legs, waistband, and pockets uniformly. "
        )
        
        # Detalles de acentos
        accent_desc = (
            f"{color_acentos} accent details on: drawstring at waistband, "
            f"zipper pulls (if applicable), pocket edges, "
            
        )
        
        # Contexto visual
        context = (
            "displayed on an invisible mannequin or flat lay, perfect studio lighting, catalog style, "
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
    tipo_corte = attr.get("tipoCorte", "joggers")
    tipo_tobillo = attr.get("tipoTobillo", "elastico")
    bolsillos = attr.get("bolsillos", "laterales_zip")
    color_base = attr.get("colorBase", "")
    color_acentos = attr.get("colorAcentos", "")
    genero = attr.get("genero", "unisex")
    
    # Traducciones
    color_base_es = TRADUCCIONES.get(color_base, color_base)
    color_acentos_es = TRADUCCIONES.get(color_acentos, color_acentos)
    genero_es = TRADUCCIONES.get(genero, genero)
    
    # Tipo de corte
    if tipo_corte == "joggers":
        corte_desc = "jogger ajustado"
    else:
        corte_desc = "corte recto"
    
    # Tipo de tobillo
    if tipo_tobillo == "elastic":
        tobillo_desc = "tobillo elástico"
    else:
        tobillo_desc = "tobillo suelto"
    
    # Descripción de bolsillos
    if bolsillos == "lateral_zip":
        bolsillo_desc = "bolsillos laterales con zipper"
    elif bolsillos == "sides_without_zip":
        bolsillo_desc = "bolsillos laterales simples"
    else:
        bolsillo_desc = "sin bolsillos"
    
    base = (
        f"Pantalón deportivo {corte_desc} para {genero_es.lower()} "
        f"de color {color_base_es.lower()} con detalles en {color_acentos_es.lower()}, "
        f"{tobillo_desc}, {bolsillo_desc}"
    )
    
    return base + "."

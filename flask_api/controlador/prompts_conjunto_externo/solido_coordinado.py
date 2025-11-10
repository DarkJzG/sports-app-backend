# flask_api/controlador/prompts_conjunto_externo/solido_coordinado.py
from typing import Dict
from flask_api.componente.traducciones import TRADUCCIONES


def build_prompt_solido_coordinado_chaqueta(attr: Dict) -> str:
    """
    Genera prompt para la chaqueta del conjunto sólido coordinado
    """
    print("🧥 Generando prompt para chaqueta sólido coordinado")
    
    try:
        # Datos estructurales
        capucha = attr.get("capucha", "yeah")  # si/no → yes/no
        bolsillos_chaqueta = attr.get("bolsillosChaqueta", "kangaroo")
        tela = attr.get("tela", "polyester")
        genero = attr.get("genero", "unisex")
        
        # Colores coordinados
        color_base = attr.get("colorBase", "black")
        color_acentos = attr.get("colorAcentos", "neon yellow")
        
        # Construcción del tipo de prenda
        garment_type = "zip-up sports jacket"
        hood_desc = "with hood" if capucha == "yeah" else "without hood"
        
        if bolsillos_chaqueta == "kangaroo":
            pocket_desc = "with kangaroo pocket"
        elif bolsillos_chaqueta == "sides":
            pocket_desc = "with side pockets"
        else:
            pocket_desc = "without pockets"
        
        garment = (
            f"high-end photorealistic sportswear {garment_type} mockup for {genero}, "
            f"{hood_desc}, {pocket_desc}, made of {tela} fabric"
        )
        
        # Diseño sólido con acentos
        design_desc = (
            f"The entire jacket is {color_base} as the solid base color, "
            f"covering the body, sleeves, hood, and pockets uniformly. "
            f"{color_acentos} accent details on: zipper, zipper pull, drawstrings, "
            f"pocket edges, and small brand logo placement."
        )
        
        # Contexto visual
        context = (
            "displayed on an invisible mannequin, perfect studio lighting, catalog style, "
            "sharp focus, plain light gray background, no text, hyper-detailed textile texture, "
            "athletic fit, modern sportswear design."
        )
        
        prompt = f"{garment}, {design_desc}, {context}"
        
        print("✅ Prompt chaqueta generado")
        return prompt
        
    except Exception as e:
        print(f"❌ Error en build_prompt_solido_coordinado_chaqueta: {e}")
        raise


def build_prompt_solido_coordinado_pantalon(attr: Dict) -> str:
    """
    Genera prompt para el pantalón del conjunto sólido coordinado
    """
    print("👖 Generando prompt para pantalón sólido coordinado")
    
    try:
        # Datos estructurales
        tipo_corte = attr.get("tipoCortePantalon", "joggers")
        tipo_tobillo = attr.get("tipoTobillo", "elastic")
        bolsillos_pantalon = attr.get("bolsillosPantalon", "sides")
        tela = attr.get("tela", "polyester")
        genero = attr.get("genero", "unisex")
        
        # Colores coordinados (MISMOS que la chaqueta)
        color_base = attr.get("colorBase", "black")
        color_acentos = attr.get("colorAcentos", "neon yellow")
        
        # Construcción del tipo de prenda
        if tipo_corte == "joggers":
            garment_type = "athletic jogger pants"
            fit_desc = "tapered fit"
        else:
            garment_type = "straight-leg athletic pants"
            fit_desc = "regular fit"
        
        ankle_desc = "with ribbed elastic cuffs" if tipo_tobillo == "elastic" else "with loose hem"
        
        if bolsillos_pantalon == "sides":
            pocket_desc = "with side pockets"
        elif bolsillos_pantalon == "rear":
            pocket_desc = "with back pockets"
        else:
            pocket_desc = "without pockets"
        
        garment = (
            f"high-end photorealistic sportswear {garment_type} mockup for {genero}, "
            f"{fit_desc}, {ankle_desc}, {pocket_desc}, made of {tela} fabric"
        )
        
        # Diseño sólido con acentos (coordinado con la chaqueta)
        design_desc = (
            f"The entire pants are {color_base} as the solid base color, "
            f"covering the legs, waistband, and pockets uniformly. "
            f"{color_acentos} accent details on: drawstring at waistband, "
            f"pocket edges, and subtle brand logo placement on thigh."
        )
        
        # Contexto visual
        context = (
            "displayed on an invisible mannequin or flat lay, perfect studio lighting, catalog style, "
            "sharp focus, plain light gray background, no text, hyper-detailed textile texture, "
            "modern athletic design."
        )
        
        prompt = f"{garment}, {design_desc}, {context}"
        
        print("✅ Prompt pantalón generado")
        return prompt
        
    except Exception as e:
        print(f"❌ Error en build_prompt_solido_coordinado_pantalon: {e}")
        raise


def descripcion_solido_coordinado_es(attr: Dict) -> str:
    """Descripción en español del conjunto sólido coordinado"""
    color_base = attr.get("colorBase", "")
    color_acentos = attr.get("colorAcentos", "")
    genero = attr.get("genero", "unisex")
    
    color_base_es = TRADUCCIONES.get(color_base, color_base)
    color_acentos_es = TRADUCCIONES.get(color_acentos, color_acentos)
    genero_es = TRADUCCIONES.get(genero, genero)
    
    return (
        f"Conjunto deportivo externo para {genero_es.lower()} (chaqueta y pantalón) "
        f"de color {color_base_es.lower()} con detalles coordinados en {color_acentos_es.lower()}."
    )

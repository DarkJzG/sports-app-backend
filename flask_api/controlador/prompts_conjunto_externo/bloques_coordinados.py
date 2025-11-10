# flask_api/controlador/prompts_conjunto_externo/bloques_coordinados.py
from typing import Dict
from flask_api.componente.traducciones import TRADUCCIONES


def build_prompt_bloques_coordinados_chaqueta(attr: Dict) -> str:
    """
    Genera prompt para la chaqueta del conjunto con bloques coordinados
    """
    print("🧥 Generando prompt para chaqueta bloques coordinados")
    
    try:
        # Datos estructurales
        capucha = attr.get("capucha", "yes")
        bolsillos_chaqueta = attr.get("bolsillosChaqueta", "kangaroo")
        tela = attr.get("tela", "polyester")
        genero = attr.get("genero", "unisex")
        
        # Tipo de bloque y colores
        tipo_bloque = attr.get("tipoBloque", "rayas_laterales")
        color_base_bloque = attr.get("colorBaseBloque", "black")
        color_panel_bloque = attr.get("colorPanelBloque", "white")
        
        garment_type = "zip-up sports jacket"
        hood_desc = "with hood" if capucha == "si" else "without hood"
        
        if bolsillos_chaqueta == "canguro":
            pocket_desc = "with kangaroo pocket"
        elif bolsillos_chaqueta == "laterales":
            pocket_desc = "with side pockets"
        else:
            pocket_desc = "without pockets"
        
        garment = (
            f"high-end photorealistic sportswear {garment_type} mockup for {genero}, "
            f"{hood_desc}, {pocket_desc}, made of {tela} fabric"
        )
        
        # Descripción según el tipo de bloque
        if tipo_bloque == "rayas_laterales":
            # 3 rayas en las mangas
            design_desc = (
                f"Color block design with {color_base_bloque} as the main body color covering the torso, back, and sleeves. "
                f"Three thin vertical {color_panel_bloque} stripes running down each outer sleeve seam from shoulder to cuff, "
                f"evenly spaced, classic athletic stripe design."
            )
        elif tipo_bloque == "bloque_superior_chaqueta":
            # Pecho en color contraste
            design_desc = (
                f"Color block design with {color_panel_bloque} chest/shoulder panel covering the upper section, "
                f"{color_base_bloque} covering the lower body, sleeves, and back, "
                f"clean horizontal seam line defining the color transition."
            )
        elif tipo_bloque == "paneles_mixtos":
            # Hombros en color contraste
            design_desc = (
                f"Color block design with {color_panel_bloque} shoulder panels, "
                f"{color_base_bloque} covering the main body, sleeves, and back, "
                f"athletic cut with contrast stitching defining each color panel."
            )
        else:
            design_desc = f"color block design with {color_base_bloque} and {color_panel_bloque} panels"
        
        context = (
            "displayed on an invisible mannequin, perfect studio lighting, catalog style, "
            "sharp focus, plain light gray background, no logos, no text, "
            "hyper-detailed textile texture, modern athletic design."
        )
        
        prompt = f"{garment}, {design_desc}, {context}"
        
        print("✅ Prompt chaqueta bloques generado")
        return prompt
        
    except Exception as e:
        print(f"❌ Error en build_prompt_bloques_coordinados_chaqueta: {e}")
        raise


def build_prompt_bloques_coordinados_pantalon(attr: Dict) -> str:
    """
    Genera prompt para el pantalón del conjunto con bloques coordinados
    """
    print("👖 Generando prompt para pantalón bloques coordinados")
    
    try:
        # Datos estructurales
        tipo_corte = attr.get("tipoCortePantalon", "jogger")
        tipo_tobillo = attr.get("tipoTobillo", "elastic")
        bolsillos_pantalon = attr.get("bolsillosPantalon", "lateral")
        tela = attr.get("tela", "polyester")
        genero = attr.get("genero", "unisex")
        
        # Tipo de bloque y colores (COORDINADOS con la chaqueta)
        tipo_bloque = attr.get("tipoBloque", "rayas_laterales")
        color_base_bloque = attr.get("colorBaseBloque", "black")
        color_panel_bloque = attr.get("colorPanelBloque", "white")
        
        if tipo_corte == "jogger":
            garment_type = "athletic jogger pants"
            fit_desc = "tapered fit"
        else:
            garment_type = "straight-leg athletic pants"
            fit_desc = "regular fit"
        
        ankle_desc = "with ribbed elastic cuffs" if tipo_tobillo == "elastico" else "with loose hem"
        
        if bolsillos_pantalon == "laterales":
            pocket_desc = "with side pockets"
        elif bolsillos_pantalon == "traseros":
            pocket_desc = "with back pockets"
        else:
            pocket_desc = "without pockets"
        
        garment = (
            f"high-end photorealistic sportswear {garment_type} mockup for {genero}, "
            f"{fit_desc}, {ankle_desc}, {pocket_desc}, made of {tela} fabric"
        )
        
        # Descripción coordinada según el tipo de bloque
        if tipo_bloque == "rayas_laterales":
            # 3 rayas laterales coordinadas con la chaqueta
            design_desc = (
                f"Color block design with {color_base_bloque} as the main body color covering the front, back, and legs. "
                f"Three thin vertical {color_panel_bloque} stripes running down each outer leg seam from hip to ankle, "
                f"evenly spaced, matching the jacket's stripe design."
            )
        elif tipo_bloque == "bloque_superior_chaqueta":
            # Pantalón sólido para combinar con chaqueta de bloque superior
            design_desc = (
                f"Solid {color_base_bloque} covering the entire pants, "
                f"designed to coordinate with the color block jacket."
            )
        elif tipo_bloque == "paneles_mixtos":
            # Panel lateral en color contraste
            design_desc = (
                f"Color block design with {color_base_bloque} main body color on front and back, "
                f"wide vertical {color_panel_bloque} panel on each outer leg, "
                f"coordinating with the jacket's panel design."
            )
        else:
            design_desc = f"color block design with {color_base_bloque} and {color_panel_bloque}"
        
        context = (
            "displayed on an invisible mannequin or flat lay, perfect studio lighting, catalog style, "
            "sharp focus, plain light gray background, no logos, no text, "
            "hyper-detailed textile texture."
        )
        
        prompt = f"{garment}, {design_desc}, {context}"
        
        print("✅ Prompt pantalón bloques generado")
        return prompt
        
    except Exception as e:
        print(f"❌ Error en build_prompt_bloques_coordinados_pantalon: {e}")
        raise


def descripcion_bloques_coordinados_es(attr: Dict) -> str:
    """Descripción en español del conjunto con bloques coordinados"""
    tipo_bloque = attr.get("tipoBloque", "rayas_laterales")
    color_base_bloque = attr.get("colorBaseBloque", "")
    color_panel_bloque = attr.get("colorPanelBloque", "")
    genero = attr.get("genero", "unisex")
    
    color_base_es = TRADUCCIONES.get(color_base_bloque, color_base_bloque)
    color_panel_es = TRADUCCIONES.get(color_panel_bloque, color_panel_bloque)
    genero_es = TRADUCCIONES.get(genero, genero)
    
    if tipo_bloque == "rayas_laterales":
        bloque_desc = "rayas laterales coordinadas"
    elif tipo_bloque == "bloque_superior_chaqueta":
        bloque_desc = "bloque superior en chaqueta"
    elif tipo_bloque == "paneles_mixtos":
        bloque_desc = "paneles deportivos mixtos"
    else:
        bloque_desc = "bloques de color coordinados"
    
    return (
        f"Conjunto deportivo externo para {genero_es.lower()} con {bloque_desc} "
        f"en colores {color_base_es.lower()} y {color_panel_es.lower()}."
    )

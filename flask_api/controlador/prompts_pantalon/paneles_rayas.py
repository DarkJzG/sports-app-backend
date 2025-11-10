# flask_api/controlador/prompts_pantalon/paneles_rayas.py
from typing import Dict
from flask_api.componente.traducciones import TRADUCCIONES


def build_prompt_paneles_rayas(attr: Dict) -> str:
    """
    Camino 2: Pantalón con paneles y rayas laterales
    """
    print("👖 Entrando a build_prompt_paneles_rayas con:", attr)
    
    try:
        # Datos estructurales
        tipo_corte = attr.get("tipoCorte", "joggers")
        tipo_tobillo = attr.get("tipoTobillo", "elastic")
        bolsillos = attr.get("bolsillos", "side pockets")
        tela = attr.get("tela", "polyester")
        genero = attr.get("genero", "unisex")
        
        # Tipo de panel
        tipo_panel = attr.get("tipoPanelCorte", "rayas_laterales")
        colores_bloque = attr.get("coloresBloque", [])
        
        # Construcción del tipo de prenda
        if tipo_corte == "joggers":
            garment_type = "athletic jogger pants"
            fit_desc = "tapered fit"
        else:
            garment_type = "straight-leg athletic pants"
            fit_desc = "regular fit"
        
        if tipo_tobillo == "elastic":
            ankle_desc = "with ribbed elastic cuffs"
        else:
            ankle_desc = "with loose hem"
        
        if bolsillos == "lateral_zip":
            pocket_desc = "with zippered side pockets"
        elif bolsillos == "sides_without_zip":
            pocket_desc = "with side pockets"
        else:
            pocket_desc = "without pockets"
        
        garment = (
            f"high-end photorealistic sportswear {garment_type} mockup for {genero}, "
            f"{fit_desc}, {ankle_desc}, {pocket_desc}, made of {tela} fabric"
        )
        
        # Descripción según el tipo de panel
        color_base = colores_bloque[0] if len(colores_bloque) > 0 else "black"
        color_panel = colores_bloque[1] if len(colores_bloque) > 1 else "white"
        
        if tipo_panel == "side_stripes":
            # Rayas laterales estilo Adidas (3 rayas finas)
            design_desc = (
                f"Color block design with {color_base} as the main body color. "
                f"Three thin vertical {color_panel} stripes running down each outer leg seam from hip to ankle, "
                f"evenly spaced, classic athletic stripe design, clean and sharp lines."
            )
        elif tipo_panel == "side_width_panel":
            # Panel ancho lateral (1 franja ancha por lado)
            design_desc = (
                f"Color block design with {color_base} as the main body color. "
                f"Wide vertical {color_panel} panel on each outer leg extending from hip to ankle, "
                f"bold contrast panel design, modern athletic style with defined seam lines."
            )
        else:
            design_desc = f"color block design with {color_base} and {color_panel} panels"
        
        # Contexto visual
        context = (
            "displayed on an invisible mannequin or flat lay, perfect studio lighting, catalog style, "
            "sharp focus, plain light gray background, no logos, no text, "
            "hyper-detailed textile texture, professional sportswear presentation."
        )
        
        prompt = f"{garment}, {design_desc}, {context}"
        
        print("🟢 build_prompt_paneles_rayas OK")
        print("🟢 Prompt generado:", prompt)
        return prompt
        
    except Exception as e:
        print("❌ Error en build_prompt_paneles_rayas:", e)
        raise


def descripcion_paneles_rayas_es(attr: Dict) -> str:
    """Descripción en español del diseño por paneles"""
    tipo_corte = attr.get("tipoCorte", "joggers")
    tipo_panel = attr.get("tipoPanelCorte", "rayas_laterales")
    colores_bloque = attr.get("coloresBloque", [])
    genero = attr.get("genero", "unisex")
    
    # Traducciones
    colores_es = [TRADUCCIONES.get(c, c) for c in colores_bloque if c]
    genero_es = TRADUCCIONES.get(genero, genero)
    
    if tipo_corte == "joggers":
        corte_desc = "joggers"
    else:
        corte_desc = "corte recto"
    
    if tipo_panel == "side_stripes":
        panel_desc = "rayas laterales"
    elif tipo_panel == "side_width_panel":
        panel_desc = "panel ancho lateral"
    else:
        panel_desc = "diseño de paneles"
    
    base = (
        f"Pantalón deportivo {corte_desc} para {genero_es.lower()} "
        f"con {panel_desc}"
    )
    
    if colores_es and len(colores_es) >= 2:
        base += f" en colores {colores_es[0].lower()} y {colores_es[1].lower()}"
    
    return base + "."

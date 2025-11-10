# flask_api/controlador/prompts_pantaloneta/paneles_rayas.py
from typing import Dict
from flask_api.componente.traducciones import TRADUCCIONES


def build_prompt_paneles_rayas(attr: Dict) -> str:
    """
    Camino 2: Pantaloneta con paneles y rayas laterales
    """
    print("🩳 Entrando a build_prompt_paneles_rayas con:", attr)
    
    try:
        # Datos estructurales
        largo = attr.get("largo", "half")
        bolsillos = attr.get("bolsillos", "side pockets")
        cordon = attr.get("cordon", "visible")
        tela = attr.get("tela", "polyester")
        genero = attr.get("genero", "unisex")
        
        # Tipo de panel
        tipo_panel = attr.get("tipoPanelCorte", "rayas_finas")
        color_base_panel = attr.get("colorBasePanel", "black")
        color_panel = attr.get("colorPanel", "white")
        
        # Construcción del tipo de prenda según el largo
        if largo == "short":
            garment_type = "short athletic running shorts"
            length_desc = "above mid-thigh, running style"
        elif largo == "half":
            garment_type = "mid-length athletic shorts"
            length_desc = "at mid-thigh, soccer/tennis style"
        else:
            garment_type = "long athletic basketball shorts"
            length_desc = "just above knee, basketball style"
        
        if bolsillos == "lateral_zip":
            pocket_desc = "with zippered side pockets"
        elif bolsillos == "sides_without_zip":
            pocket_desc = "with side pockets"
        else:
            pocket_desc = "without pockets"
        
        if cordon == "visible":
            drawstring_desc = "visible drawstring"
        else:
            drawstring_desc = "internal drawstring"
        
        garment = (
            f"high-end photorealistic sportswear {garment_type} mockup for {genero}, "
            f"{length_desc}, {pocket_desc}, {drawstring_desc}, "
            f"made of {tela} fabric, elastic waistband"
        )
        
        # Descripción según el tipo de panel
        if tipo_panel == "thin_stripes":
            # Rayas finas laterales estilo Adidas
            design_desc = (
                f"Color block design with {color_base_panel} as the main body color covering front and back. "
                f"Two or three thin vertical {color_panel} stripes running down each outer seam from waistband to hem, "
                f"evenly spaced, classic athletic stripe design inspired by Adidas style."
            )
        elif tipo_panel == "panel_width":
            # Panel lateral ancho
            design_desc = (
                f"Color block design with {color_base_panel} as the main body color on front and back. "
                f"Wide vertical {color_panel} panel on each outer leg from waistband to hem, "
                f"bold contrast panel design, modern athletic style with defined seam lines."
            )
        elif tipo_panel == "curved_panel":
            # Panel curvo con piping (estilo fútbol/running)
            design_desc = (
                f"Color block design with {color_base_panel} main body. "
                f"Curved {color_panel} panels on outer legs with contrasting piping trim, "
                f"following the natural leg contour from hip to hem, "
                f"soccer/running style with athletic cut."
            )
        else:
            design_desc = f"color block design with {color_base_panel} and {color_panel} panels"
        
        # Contexto visual
        context = (
            "displayed flat lay or on invisible mannequin, perfect studio lighting, catalog style, "
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
    largo = attr.get("largo", "half")
    tipo_panel = attr.get("tipoPanelCorte", "thin_stripes")
    color_base_panel = attr.get("colorBasePanel", "")
    color_panel = attr.get("colorPanel", "")
    genero = attr.get("genero", "unisex")
    
    # Traducciones
    color_base_es = TRADUCCIONES.get(color_base_panel, color_base_panel)
    color_panel_es = TRADUCCIONES.get(color_panel, color_panel)
    genero_es = TRADUCCIONES.get(genero, genero)
    
    if largo == "corto":
        largo_desc = "corta"
    elif largo == "medio":
        largo_desc = "media"
    else:
        largo_desc = "larga"
    
    if tipo_panel == "thin_stripes":
        panel_desc = "rayas finas laterales"
    elif tipo_panel == "width_panel":
        panel_desc = "panel ancho lateral"
    elif tipo_panel == "curved_panel":
        panel_desc = "paneles curvos con vivos"
    else:
        panel_desc = "diseño de paneles"
    
    base = (
        f"Pantaloneta deportiva {largo_desc} para {genero_es.lower()} "
        f"con {panel_desc} "
        f"en colores {color_base_es.lower()} y {color_panel_es.lower()}"
    )
    
    return base + "."

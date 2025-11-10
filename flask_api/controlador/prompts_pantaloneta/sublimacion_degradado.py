# flask_api/controlador/prompts_pantaloneta/sublimacion_degradado.py
from typing import Dict
from flask_api.componente.traducciones import TRADUCCIONES


def build_prompt_sublimacion_degradado(attr: Dict) -> str:
    """
    Camino 3: Diseño sublimado con degradado IA
    """
    print("🩳 Entrando a build_prompt_sublimacion_degradado con:", attr)
    
    try:
        # Datos estructurales
        largo = attr.get("largo", "half")
        bolsillos = attr.get("bolsillos", "side pockets")
        cordon = attr.get("cordon", "visible")
        tela = attr.get("tela", "polyester")
        genero = attr.get("genero", "unisex")
        
        # Datos de sublimación
        area_diseno = attr.get("areaDisenoIA", "completo")
        color_base_mixto = attr.get("colorBaseMixto", "")
        
        # Datos del degradado
        colores_gradiente = attr.get("coloresGradiente", [])
        num_colores = len(colores_gradiente)
        
        # Construcción del tipo de prenda
        if largo == "short":
            garment_type = "short athletic running shorts"
            length_desc = "above mid-thigh"
        elif largo == "half":
            garment_type = "mid-length athletic shorts"
            length_desc = "at mid-thigh"
        else:
            garment_type = "long athletic basketball shorts"
            length_desc = "just above knee"
        
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
            f"made of {tela} fabric"
        )
        
        # Descripción según el área de diseño
        if area_diseno == "complete":
            # Diseño completo sublimado
            if num_colores == 2:
                gradient_desc = (
                    f"Full sublimation print covering the entire shorts. "
                    f"Smooth vertical gradient transitioning from {colores_gradiente[0]} at the waistband "
                    f"to {colores_gradiente[1]} at the hem, flowing naturally across both legs."
                )
            elif num_colores >= 3:
                gradient_desc = (
                    f"Full sublimation print covering the entire shorts. "
                    f"Multi-color gradient flowing vertically from {colores_gradiente[0]} at waistband "
                    f"through {colores_gradiente[1]} at mid-thigh to {colores_gradiente[2]} at hem, "
                    f"smooth color transitions across both legs."
                )
            else:
                gradient_desc = "full sublimation print with gradient effect across entire garment"
            
            design_desc = gradient_desc
            
        else:  # paneles_laterales
            # Solo paneles laterales sublimados
            if num_colores == 2:
                gradient_desc = (
                    f"wide vertical panels on outer legs with gradient sublimation print, "
                    f"transitioning from {colores_gradiente[0]} to {colores_gradiente[1]}"
                )
            elif num_colores >= 3:
                gradient_desc = (
                    f"wide vertical panels on outer legs with multi-color gradient sublimation, "
                    f"transitioning from {colores_gradiente[0]} through {colores_gradiente[1]} to {colores_gradiente[2]}"
                )
            else:
                gradient_desc = "wide vertical panels on outer legs with gradient sublimation"
            
            solid_desc = f"{color_base_mixto} solid color on front, back, and waistband"
            design_desc = f"Hybrid design: {solid_desc}, {gradient_desc}, clean seam separation."
        
        # Contexto visual
        context = (
            "displayed flat lay or on invisible mannequin, perfect studio lighting, catalog style, "
            "sharp focus, plain light gray background, no logos, no text, "
            "hyper-detailed sublimation print texture, modern athletic design."
        )
        
        prompt = f"{garment}, {design_desc}, {context}"
        
        print("🟢 build_prompt_sublimacion_degradado OK")
        print("🟢 Prompt generado:", prompt)
        return prompt
        
    except Exception as e:
        print("❌ Error en build_prompt_sublimacion_degradado:", e)
        raise


def descripcion_sublimacion_degradado_es(attr: Dict) -> str:
    """Descripción en español del diseño sublimado con degradado"""
    largo = attr.get("largo", "half")
    area_diseno = attr.get("areaDisenoIA", "complete")
    color_base_mixto = attr.get("colorBaseMixto", "")
    colores_gradiente = attr.get("coloresGradiente", [])
    genero = attr.get("genero", "unisex")
    
    # Traducciones
    colores_grad_es = [TRADUCCIONES.get(c, c) for c in colores_gradiente if c]
    genero_es = TRADUCCIONES.get(genero, genero)
    
    if largo == "short":
        largo_desc = "corta"
    elif largo == "half":
        largo_desc = "media"
    else:
        largo_desc = "larga"
    
    if area_diseno == "complete":
        area_desc = "sublimación completa con degradado"
    else:
        color_base_es = TRADUCCIONES.get(color_base_mixto, color_base_mixto)
        area_desc = f"base {color_base_es.lower()} con paneles laterales sublimados con degradado"
    
    base = (
        f"Pantaloneta deportiva {largo_desc} para {genero_es.lower()} "
        f"con {area_desc}"
    )
    
    if colores_grad_es:
        if len(colores_grad_es) == 2:
            base += f" en tonos {colores_grad_es[0].lower()} y {colores_grad_es[1].lower()}"
        elif len(colores_grad_es) >= 3:
            base += f" en tonos {', '.join([c.lower() for c in colores_grad_es])}"
    
    return base + "."

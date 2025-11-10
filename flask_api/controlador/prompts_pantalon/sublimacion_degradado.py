# flask_api/controlador/prompts_pantalon/sublimacion_degradado.py
from typing import Dict
from flask_api.componente.traducciones import TRADUCCIONES


def build_prompt_sublimacion_degradado(attr: Dict) -> str:
    """
    Camino 3: Diseño sublimado con degradado IA
    """
    print("👖 Entrando a build_prompt_sublimacion_degradado con:", attr)
    
    try:
        # Datos estructurales
        tipo_corte = attr.get("tipoCorte", "jogger")
        tipo_tobillo = attr.get("tipoTobillo", "elastic")
        bolsillos = attr.get("bolsillos", "side pockets")
        tela = attr.get("tela", "polyester")
        genero = attr.get("genero", "unisex")
        
        # Datos de sublimación
        area_diseno = attr.get("areaDisenoIA", "completo")
        color_base_mixto = attr.get("colorBaseMixto", "")
        
        # Datos del degradado
        colores_gradiente = attr.get("coloresGradiente", [])
        num_colores = len(colores_gradiente)
        
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
        
        # Descripción según el área de diseño
        if area_diseno == "complete":
            # Diseño completo sublimado
            if num_colores == 2:
                gradient_desc = (
                    f"Full sublimation print covering the entire pants. "
                    f"Smooth gradient transitioning vertically from {colores_gradiente[0]} at the waistband "
                    f"to {colores_gradiente[1]} at the ankles, flowing naturally across both legs. "
                )
            elif num_colores >= 3:
                gradient_desc = (
                    f"Full sublimation print covering the entire pants. "
                    f"Multi-color gradient flowing vertically from {colores_gradiente[0]} at the waistband "
                    f"through {colores_gradiente[1]} at mid-thigh to {colores_gradiente[2]} at the ankles, "
                    f"smooth color transitions across both legs. "
                )
            else:
                gradient_desc = "full sublimation print with gradient effect across entire garment"
            
            design_desc = gradient_desc
            
        else:  # paneles_laterales
            # Solo paneles laterales sublimados
            if num_colores == 2:
                gradient_desc = (
                    f"wide vertical panels on outer legs with gradient sublimation print, "
                    f"transitioning from {colores_gradiente[0]} to {colores_gradiente[1]} "
                )
            elif num_colores >= 3:
                gradient_desc = (
                    f"wide vertical panels on outer legs with multi-color gradient sublimation, "
                    f"transitioning from {colores_gradiente[0]} through {colores_gradiente[1]} to {colores_gradiente[2]} "
                )
            else:
                gradient_desc = "wide vertical panels on outer legs with gradient sublimation"
            
            solid_desc = f"{color_base_mixto} solid color on front, back, inner legs, and waistband"
            design_desc = f"Mixed design: {solid_desc}, {gradient_desc}, clean seam separation."
        
        # Contexto visual
        context = (
            "displayed on an invisible mannequin or flat lay, perfect studio lighting, catalog style, "
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
    tipo_corte = attr.get("tipoCorte", "joggers")
    area_diseno = attr.get("areaDisenoIA", "complete")
    color_base_mixto = attr.get("colorBaseMixto", "")
    colores_gradiente = attr.get("coloresGradiente", [])
    genero = attr.get("genero", "unisex")
    
    # Traducciones
    colores_grad_es = [TRADUCCIONES.get(c, c) for c in colores_gradiente if c]
    genero_es = TRADUCCIONES.get(genero, genero)
    
    if tipo_corte == "joggers":
        corte_desc = "joggers"
    else:
        corte_desc = "corte recto"
    
    if area_diseno == "complete":
        area_desc = "sublimación completa con degradado"
    else:
        color_base_es = TRADUCCIONES.get(color_base_mixto, color_base_mixto)
        area_desc = f"base {color_base_es.lower()} con paneles laterales sublimados con degradado"
    
    base = (
        f"Pantalón deportivo {corte_desc} para {genero_es.lower()} "
        f"con {area_desc}"
    )
    
    if colores_grad_es:
        if len(colores_grad_es) == 2:
            base += f" en tonos {colores_grad_es[0].lower()} y {colores_grad_es[1].lower()}"
        elif len(colores_grad_es) >= 3:
            base += f" en tonos {', '.join([c.lower() for c in colores_grad_es])}"
    
    return base + "."

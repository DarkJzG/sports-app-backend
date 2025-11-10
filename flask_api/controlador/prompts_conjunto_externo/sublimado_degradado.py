# flask_api/controlador/prompts_conjunto_externo/sublimado_degradado.py
from typing import Dict
from flask_api.componente.traducciones import TRADUCCIONES


def build_prompt_sublimado_degradado_chaqueta(attr: Dict) -> str:
    """
    Genera prompt para la chaqueta con sublimación degradado
    """
    print("🧥 Generando prompt para chaqueta sublimado degradado")
    
    try:
        # Datos estructurales
        capucha = attr.get("capucha", "yes")
        bolsillos_chaqueta = attr.get("bolsillosChaqueta", "kangaroo")
        tela = attr.get("tela", "polyester")
        genero = attr.get("genero", "unisex")
        
        # Datos de sublimación
        area_sublimacion = attr.get("areaSublimacion", "completo_ambas")
        color_base_sublimado = attr.get("colorBaseSublimado", "")
        colores_gradiente = attr.get("coloresGradiente", [])
        num_colores = len(colores_gradiente)
        
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
        
        # Descripción según el área de sublimación
        if area_sublimacion == "completo_ambas":
            # Sublimación completa
            if num_colores == 2:
                gradient_desc = (
                    f"Full sublimation print covering the entire jacket. "
                    f"Smooth vertical gradient transitioning from {colores_gradiente[0]} at the shoulders "
                    f"to {colores_gradiente[1]} at the waist, flowing across body, sleeves, and hood."
                )
            elif num_colores >= 3:
                gradient_desc = (
                    f"Full sublimation print covering the entire jacket. "
                    f"Multi-color gradient flowing from {colores_gradiente[0]} at shoulders "
                    f"through {colores_gradiente[1]} at chest to {colores_gradiente[2]} at waist, "
                    f"smooth transitions across entire garment."
                )
            else:
                gradient_desc = "full sublimation print with gradient effect"
            
            design_desc = gradient_desc
        else:  # hibrido
            # Solo paneles sublimados
            if num_colores == 2:
                gradient_desc = (
                    f"gradient sublimation on chest, shoulders, and hood panels, "
                    f"transitioning from {colores_gradiente[0]} to {colores_gradiente[1]}"
                )
            elif num_colores >= 3:
                gradient_desc = (
                    f"gradient sublimation on chest, shoulders, and hood panels, "
                    f"transitioning from {colores_gradiente[0]} through {colores_gradiente[1]} to {colores_gradiente[2]}"
                )
            else:
                gradient_desc = "gradient sublimation on upper panels"
            
            solid_desc = f"{color_base_sublimado} solid color on lower body, sleeves, and back"
            design_desc = f"Hybrid design: {solid_desc}, {gradient_desc}, seamless integration."
        
        context = (
            "displayed on an invisible mannequin, perfect studio lighting, catalog style, "
            "sharp focus, plain light gray background, no logos, no text, "
            "hyper-detailed sublimation texture, modern Windrunner style."
        )
        
        prompt = f"{garment}, {design_desc}, {context}"
        
        print("✅ Prompt chaqueta sublimado generado")
        return prompt
        
    except Exception as e:
        print(f"❌ Error en build_prompt_sublimado_degradado_chaqueta: {e}")
        raise


def build_prompt_sublimado_degradado_pantalon(attr: Dict) -> str:
    """
    Genera prompt para el pantalón con sublimación degradado (COORDINADO con la chaqueta)
    """
    print("👖 Generando prompt para pantalón sublimado degradado")
    
    try:
        # Datos estructurales
        tipo_corte = attr.get("tipoCortePantalon", "jogger")
        tipo_tobillo = attr.get("tipoTobillo", "elastic")
        bolsillos_pantalon = attr.get("bolsillosPantalon", "lateral")
        tela = attr.get("tela", "polyester")
        genero = attr.get("genero", "unisex")
        
        # Datos de sublimación (COORDINADOS con la chaqueta)
        area_sublimacion = attr.get("areaSublimacion", "completo_ambas")
        color_base_sublimado = attr.get("colorBaseSublimado", "")
        colores_gradiente = attr.get("coloresGradiente", [])
        num_colores = len(colores_gradiente)
        
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
        
        # Descripción coordinada con la chaqueta
        if area_sublimacion == "completo_ambas":
            # Sublimación completa (mismo degradado que la chaqueta)
            if num_colores == 2:
                gradient_desc = (
                    f"Full sublimation print matching the jacket. "
                    f"Smooth vertical gradient from {colores_gradiente[0]} at waistband "
                    f"to {colores_gradiente[1]} at ankles, coordinated design."
                )
            elif num_colores >= 3:
                gradient_desc = (
                    f"Full sublimation print matching the jacket. "
                    f"Multi-color gradient from {colores_gradiente[0]} at waistband "
                    f"through {colores_gradiente[1]} at mid-thigh to {colores_gradiente[2]} at ankles, coordinated."
                )
            else:
                gradient_desc = "full sublimation print with coordinated gradient"
            
            design_desc = gradient_desc
        else:  # hibrido
            # Paneles laterales sublimados
            if num_colores == 2:
                gradient_desc = (
                    f"gradient sublimation on outer leg panels, "
                    f"transitioning from {colores_gradiente[0]} to {colores_gradiente[1]}, matching jacket design"
                )
            elif num_colores >= 3:
                gradient_desc = (
                    f"gradient sublimation on outer leg panels, "
                    f"transitioning from {colores_gradiente[0]} through {colores_gradiente[1]} to {colores_gradiente[2]}, matching jacket"
                )
            else:
                gradient_desc = "gradient sublimation on outer leg panels"
            
            solid_desc = f"{color_base_sublimado} solid color on front, back, and inner legs"
            design_desc = f"Hybrid design: {solid_desc}, {gradient_desc}, coordinated with jacket."
        
        context = (
            "displayed on an invisible mannequin or flat lay, perfect studio lighting, catalog style, "
            "sharp focus, plain light gray background, no logos, no text, "
            "hyper-detailed sublimation texture."
        )
        
        prompt = f"{garment}, {design_desc}, {context}"
        
        print("✅ Prompt pantalón sublimado generado")
        return prompt
        
    except Exception as e:
        print(f"❌ Error en build_prompt_sublimado_degradado_pantalon: {e}")
        raise


def descripcion_sublimado_degradado_es(attr: Dict) -> str:
    """Descripción en español del conjunto sublimado con degradado"""
    area_sublimacion = attr.get("areaSublimacion", "completo_ambas")
    color_base_sublimado = attr.get("colorBaseSublimado", "")
    colores_gradiente = attr.get("coloresGradiente", [])
    genero = attr.get("genero", "unisex")
    
    colores_grad_es = [TRADUCCIONES.get(c, c) for c in colores_gradiente if c]
    genero_es = TRADUCCIONES.get(genero, genero)
    
    if area_sublimacion == "completo_ambas":
        area_desc = "sublimación completa con degradado coordinado"
    else:
        color_base_es = TRADUCCIONES.get(color_base_sublimado, color_base_sublimado)
        area_desc = f"diseño híbrido con base {color_base_es.lower()} y paneles sublimados con degradado coordinado"
    
    base = (
        f"Conjunto deportivo externo para {genero_es.lower()} con {area_desc}"
    )
    
    if colores_grad_es:
        if len(colores_grad_es) == 2:
            base += f" en tonos {colores_grad_es[0].lower()} y {colores_grad_es[1].lower()}"
        elif len(colores_grad_es) >= 3:
            base += f" en tonos {', '.join([c.lower() for c in colores_grad_es])}"
    
    return base + "."

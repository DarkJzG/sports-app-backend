# flask_api/controlador/prompts_pantalon/sublimacion_artistico.py
from typing import Dict
from flask_api.componente.traducciones import TRADUCCIONES


def build_prompt_sublimacion_artistico(attr: Dict) -> str:
    """Camino 3: Diseño sublimado con estilo artístico IA"""
    print("👖 Entrando a build_prompt_sublimacion_artistico con:", attr)
    
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
        
        # Datos del estilo artístico
        estilo_artistico = attr.get("estiloArtistico", "brush strokes")
        colores_artistico = attr.get("coloresArtistico", [])
        
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
        
        # Descripción del estilo artístico
        if estilo_artistico == "brush strokes":
            style_desc = "artistic brush strokes with expressive paint textures"
        elif estilo_artistico == "fluent":
            style_desc = "fluid art effect with smooth watercolor-like transitions"
        elif estilo_artistico == "smoke":
            style_desc = "ethereal smoke-like effect with soft diffusion"
        else:
            style_desc = "artistic abstract texture"
        
        # Descripción de colores
        num_colores = len(colores_artistico)
        if num_colores == 2:
            color_desc = f"in {colores_artistico[0]} and {colores_artistico[1]} tones"
        elif num_colores >= 3:
            color_desc = f"in {', '.join(colores_artistico)} tones"
        else:
            color_desc = "with mixed artistic tones"
        
        # Descripción según el área de diseño
        if area_diseno == "complete":
            artistic_desc = (
                f"Full sublimation print with {style_desc} covering the entire pants, "
                f"{color_desc}, creating dynamic artistic expression across both legs."
            )
            design_desc = artistic_desc
        else:  # paneles_laterales
            artistic_desc = (
                f"wide vertical panels on outer legs with {style_desc}, "
                f"{color_desc}, bold artistic sublimation design"
            )
            solid_desc = f"{color_base_mixto} solid color on front, back, and inner legs"
            design_desc = f"Mixed design: {solid_desc}, {artistic_desc}, modern streetwear aesthetic."
        
        # Contexto visual
        context = (
            "displayed on an invisible mannequin or flat lay, perfect studio lighting, catalog style, "
            "sharp focus, plain light gray background, no logos, no text, "
            "hyper-detailed sublimation print texture."
        )
        
        prompt = f"{garment}, {design_desc}, {context}"
        
        print("🟢 build_prompt_sublimacion_artistico OK")
        print("🟢 Prompt generado:", prompt)
        return prompt
        
    except Exception as e:
        print("❌ Error en build_prompt_sublimacion_artistico:", e)
        raise


def descripcion_sublimacion_artistico_es(attr: Dict) -> str:
    """Descripción en español del diseño sublimado artístico"""
    tipo_corte = attr.get("tipoCorte", "jogger")
    area_diseno = attr.get("areaDisenoIA", "completo")
    color_base_mixto = attr.get("colorBaseMixto", "")
    estilo_artistico = attr.get("estiloArtistico", "")
    colores_artistico = attr.get("coloresArtistico", [])
    genero = attr.get("genero", "unisex")
    
    # Traducciones
    estilo_es = TRADUCCIONES.get(estilo_artistico, estilo_artistico)
    colores_art_es = [TRADUCCIONES.get(c, c) for c in colores_artistico if c]
    genero_es = TRADUCCIONES.get(genero, genero)
    
    if tipo_corte == "joggers":
        corte_desc = "joggers"
    else:
        corte_desc = "corte recto"
    
    if area_diseno == "complete":
        area_desc = f"sublimación completa con diseño artístico tipo {estilo_es}"
    else:
        color_base_es = TRADUCCIONES.get(color_base_mixto, color_base_mixto)
        area_desc = f"base {color_base_es.lower()} con paneles laterales sublimados con diseño artístico tipo {estilo_es}"
    
    base = (
        f"Pantalón deportivo {corte_desc} para {genero_es.lower()} "
        f"con {area_desc}"
    )
    
    if colores_art_es:
        base += f" en tonos {', '.join([c.lower() for c in colores_art_es])}"
    
    return base + "."

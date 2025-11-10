# flask_api/controlador/prompts_conjunto_externo/sublimado_artistico.py
from typing import Dict
from flask_api.componente.traducciones import TRADUCCIONES


def build_prompt_sublimado_artistico_chaqueta(attr: Dict) -> str:
    """
    Genera prompt para la chaqueta con sublimación artística
    """
    print("🧥 Generando prompt para chaqueta sublimado artístico")
    
    try:
        # Datos estructurales
        capucha = attr.get("capucha", "yes")
        bolsillos_chaqueta = attr.get("bolsillosChaqueta", "kangaroo")
        tela = attr.get("tela", "polyester")
        genero = attr.get("genero", "unisex")
        
        # Datos de sublimación
        area_sublimacion = attr.get("areaSublimacion", "completo_ambas")
        color_base_sublimado = attr.get("colorBaseSublimado", "")
        estilo_artistico = attr.get("estiloArtistico", "brush strokes")
        colores_artistico = attr.get("coloresArtistico", [])
        num_colores = len(colores_artistico)
        
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
        
        # Descripción del estilo artístico
        if estilo_artistico == "pinceladas":
            style_desc = "artistic brush strokes with expressive paint textures"
        elif estilo_artistico == "humo":
            style_desc = "ethereal smoke-like effect with soft diffusion"
        else:
            style_desc = "artistic abstract texture"
        
        # Descripción de colores
        if num_colores == 2:
            color_desc = f"in {colores_artistico[0]} and {colores_artistico[1]} tones"
        elif num_colores >= 3:
            color_desc = f"in {', '.join(colores_artistico)} tones"
        else:
            color_desc = "with mixed artistic tones"
        
        # Descripción según el área
        if area_sublimacion == "completo_ambas":
            artistic_desc = (
                f"Full sublimation print with {style_desc} covering entire jacket, "
                f"{color_desc}, dynamic artistic expression across body, sleeves, and hood."
            )
            design_desc = artistic_desc
        else:  # hibrido
            artistic_desc = (
                f"{style_desc} on chest, shoulders, and hood panels, "
                f"{color_desc}, bold artistic sublimation"
            )
            solid_desc = f"{color_base_sublimado} solid color on lower body, sleeves, and back"
            design_desc = f"Hybrid design: {solid_desc}, {artistic_desc}, modern streetwear aesthetic."
        
        context = (
            "displayed on an invisible mannequin, perfect studio lighting, catalog style, "
            "sharp focus, plain light gray background, no logos, no text, "
            "hyper-detailed sublimation texture."
        )
        
        prompt = f"{garment}, {design_desc}, {context}"
        
        print("✅ Prompt chaqueta artístico generado")
        return prompt
        
    except Exception as e:
        print(f"❌ Error en build_prompt_sublimado_artistico_chaqueta: {e}")
        raise


def build_prompt_sublimado_artistico_pantalon(attr: Dict) -> str:
    """
    Genera prompt para el pantalón con sublimación artística (COORDINADO)
    """
    print("👖 Generando prompt para pantalón sublimado artístico")
    
    try:
        # Datos estructurales
        tipo_corte = attr.get("tipoCortePantalon", "jogger")
        tipo_tobillo = attr.get("tipoTobillo", "elastic")
        bolsillos_pantalon = attr.get("bolsillosPantalon", "lateral")
        tela = attr.get("tela", "polyester")
        genero = attr.get("genero", "unisex")
        
        # Datos de sublimación (COORDINADOS)
        area_sublimacion = attr.get("areaSublimacion", "completo_ambas")
        color_base_sublimado = attr.get("colorBaseSublimado", "")
        estilo_artistico = attr.get("estiloArtistico", "brush strokes")
        colores_artistico = attr.get("coloresArtistico", [])
        num_colores = len(colores_artistico)
        
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
        
        # Descripción del estilo artístico
        if estilo_artistico == "pinceladas":
            style_desc = "artistic brush strokes with expressive paint textures"
        elif estilo_artistico == "humo":
            style_desc = "ethereal smoke-like effect with soft diffusion"
        else:
            style_desc = "artistic abstract texture"
        
        # Descripción de colores
        if num_colores == 2:
            color_desc = f"in {colores_artistico[0]} and {colores_artistico[1]} tones"
        elif num_colores >= 3:
            color_desc = f"in {', '.join(colores_artistico)} tones"
        else:
            color_desc = "with mixed artistic tones"
        
        # Descripción coordinada
        if area_sublimacion == "completo_ambas":
            artistic_desc = (
                f"Full sublimation print matching the jacket with {style_desc}, "
                f"{color_desc}, coordinated artistic expression across entire pants."
            )
            design_desc = artistic_desc
        else:  # hibrido
            artistic_desc = (
                f"{style_desc} on outer leg panels, "
                f"{color_desc}, matching jacket's artistic design"
            )
            solid_desc = f"{color_base_sublimado} solid color on front, back, and inner legs"
            design_desc = f"Hybrid design: {solid_desc}, {artistic_desc}, coordinated with jacket."
        
        context = (
            "displayed on an invisible mannequin or flat lay, perfect studio lighting, catalog style, "
            "sharp focus, plain light gray background, no logos, no text, "
            "hyper-detailed sublimation texture."
        )
        
        prompt = f"{garment}, {design_desc}, {context}"
        
        print("✅ Prompt pantalón artístico generado")
        return prompt
        
    except Exception as e:
        print(f"❌ Error en build_prompt_sublimado_artistico_pantalon: {e}")
        raise


def descripcion_sublimado_artistico_es(attr: Dict) -> str:
    """Descripción en español del conjunto sublimado artístico"""
    area_sublimacion = attr.get("areaSublimacion", "completo_ambas")
    color_base_sublimado = attr.get("colorBaseSublimado", "")
    estilo_artistico = attr.get("estiloArtistico", "")
    colores_artistico = attr.get("coloresArtistico", [])
    genero = attr.get("genero", "unisex")
    
    estilo_es = TRADUCCIONES.get(estilo_artistico, estilo_artistico)
    colores_art_es = [TRADUCCIONES.get(c, c) for c in colores_artistico if c]
    genero_es = TRADUCCIONES.get(genero, genero)
    
    if area_sublimacion == "completo_ambas":
        area_desc = f"sublimación completa con diseño artístico tipo {estilo_es} coordinado"
    else:
        color_base_es = TRADUCCIONES.get(color_base_sublimado, color_base_sublimado)
        area_desc = f"diseño híbrido con base {color_base_es.lower()} y paneles artísticos tipo {estilo_es} coordinados"
    
    base = (
        f"Conjunto deportivo externo para {genero_es.lower()} con {area_desc}"
    )
    
    if colores_art_es:
        base += f" en tonos {', '.join([c.lower() for c in colores_art_es])}"
    
    return base + "."

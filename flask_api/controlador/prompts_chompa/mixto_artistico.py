# flask_api/controlador/prompts_chompa/mixto_artistico.py
from typing import Dict
from flask_api.componente.traducciones import TRADUCCIONES


def build_prompt_mixto_artistico(attr: Dict) -> str:
    """Camino 3: Diseño mixto con estilo artístico IA"""
    print("🧥 Entrando a build_prompt_mixto_artistico con:", attr)
    
    try:
        # Datos estructurales
        tipo_chompa = attr.get("tipoChompa", "hoodie")
        capucha = attr.get("capucha", "yes")
        bolsillos = attr.get("bolsillos", "kangaroo")
        tela = attr.get("tela", "polyester")
        genero = attr.get("genero", "unisex")
        
        # Datos del diseño mixto
        area_diseno = attr.get("areaDisenoIA", "pecho_hombros")
        color_base_mixto = attr.get("colorBaseMixto", "black")
        
        # Datos del estilo artístico
        estilo_artistico = attr.get("estiloArtistico", "brush strokes")
        colores_artistico = attr.get("coloresArtistico", [])
        
        # Construcción del tipo de prenda
        if tipo_chompa == "jacket":
            garment_type = "zip-up sports jacket"
        else:
            garment_type = "pullover hoodie" if capucha == "Yeah" else "pullover sweatshirt"
        
        hood_desc = "with hood" if capucha == "Yeah" else "without hood"
        
        if bolsillos == "kangaroo":
            pocket_desc = "with kangaroo pocket"
        elif bolsillos == "sides":
            pocket_desc = "with side pockets"
        else:
            pocket_desc = "without pockets"
        
        garment = (
            f"high-end photorealistic sportswear {garment_type} mockup for {genero}, "
            f"{hood_desc}, {pocket_desc}, made of {tela} fabric"
        )
        
        # Descripción del área
        if area_diseno == "chest_shoulders":
            area_desc = "chest, shoulders, and hood area"
            solid_desc = f"{color_base_mixto} solid color on lower body and sleeves"
        else:
            area_desc = "main body and lower panels"
            solid_desc = f"{color_base_mixto} solid color on shoulders and upper chest"
        
        # Descripción del estilo artístico
        if estilo_artistico == "brush strokes":
            style_desc = "artistic brush strokes with expressive paint textures"
        elif estilo_artistico == "splashes":
            style_desc = "dynamic paint splatter effect, conveying energy and motion"
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
        
        artistic_desc = f"{style_desc} on {area_desc}, {color_desc}"
        
        design_desc = f"Mixed design: {solid_desc}, {artistic_desc}, bold artistic expression."
        
        context = (
            "displayed on an invisible mannequin, perfect studio lighting, catalog style, "
            "sharp focus, plain light gray background, no logos, no text, "
            "hyper-detailed textile texture."
        )
        
        prompt = f"{garment}, {design_desc}, {context}"
        
        print("🟢 build_prompt_mixto_artistico OK")
        print("🟢 Prompt generado:", prompt)
        return prompt
        
    except Exception as e:
        print("❌ Error en build_prompt_mixto_artistico:", e)
        raise


def descripcion_mixto_artistico_es(attr: Dict) -> str:
    """Descripción en español del diseño mixto artístico"""
    tipo_chompa = attr.get("tipoChompa", "sudadera")
    capucha = attr.get("capucha", "si")
    area_diseno = attr.get("areaDisenoIA", "pecho_hombros")
    color_base_mixto = attr.get("colorBaseMixto", "")
    estilo_artistico = attr.get("estiloArtistico", "")
    colores_artistico = attr.get("coloresArtistico", [])
    genero = attr.get("genero", "unisex")
    
    # Traducciones
    color_base_es = TRADUCCIONES.get(color_base_mixto, color_base_mixto)
    estilo_es = TRADUCCIONES.get(estilo_artistico, estilo_artistico)
    colores_art_es = [TRADUCCIONES.get(c, c) for c in colores_artistico if c]
    genero_es = TRADUCCIONES.get(genero, genero)
    
    if tipo_chompa == "sudadera":
        tipo_desc = "sudadera" if capucha == "si" else "buzo"
    else:
        tipo_desc = "chaqueta deportiva"
    
    if area_diseno == "pecho_hombros":
        area_desc = "pecho y hombros"
    else:
        area_desc = "cuerpo inferior"
    
    base = (
        f"{tipo_desc.capitalize()} deportiva para {genero_es.lower()} "
        f"estilo mixto con base {color_base_es.lower()} y diseño artístico tipo {estilo_es} en {area_desc}"
    )
    
    if colores_art_es:
        base += f" en tonos {', '.join([c.lower() for c in colores_art_es])}"
    
    return base + "."

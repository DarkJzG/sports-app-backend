# flask_api/controlador/prompts_chompa/mixto_personalizado.py
from typing import Dict
from flask_api.componente.traducciones import TRADUCCIONES


def build_prompt_mixto_personalizado(attr: Dict) -> str:
    """Camino 3: Diseño mixto con objetos personalizados IA"""
    print("🧥 Entrando a build_prompt_mixto_personalizado con:", attr)
    
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
        
        # Datos de objetos personalizados
        motifs = attr.get("motifs", "abstract shapes")
        colores_objetos = attr.get("coloresObjetos", [])
        estilo_objetos = attr.get("estiloObjetos", "realistic")
        distribucion_objetos = attr.get("distribucionObjetos", "random")
        
        # Construcción del tipo de prenda
        if tipo_chompa == "chaqueta":
            garment_type = "zip-up sports jacket"
        else:
            garment_type = "pullover hoodie" if capucha == "yes" else "pullover sweatshirt"
        
        hood_desc = "with hood" if capucha == "yes" else "without hood"
        
        if bolsillos == "kangaroo":
            pocket_desc = "with kangaroo pocket"
        elif bolsillos == "laterales":
            pocket_desc = "with side pockets"
        else:
            pocket_desc = "without pockets"
        
        garment = (
            f"high-end photorealistic sportswear {garment_type} mockup for {genero}, "
            f"{hood_desc}, {pocket_desc}, made of {tela} fabric"
        )
        
        # Descripción del área
        if area_diseno == "pecho_hombros":
            area_desc = "chest, shoulders, and hood area"
            solid_desc = f"{color_base_mixto} solid color on lower body and sleeves"
        else:
            area_desc = "main body and lower panels"
            solid_desc = f"{color_base_mixto} solid color on shoulders and upper chest"
        
        # Traducción de estilo
        if estilo_objetos == "animado":
            style = "animated cartoon style"
        elif estilo_objetos == "realista":
            style = "realistic photographic style"
        elif estilo_objetos == "futurista":
            style = "futuristic digital style"
        else:
            style = "modern graphic style"
        
        # Traducción de distribución
        if distribucion_objetos == "sin_repeticion":
            dist_desc = f"a single large {motifs} element centered on {area_desc}, prominent and detailed"
        elif distribucion_objetos == "aleatorio":
            dist_desc = f"multiple {motifs} motifs randomly scattered across {area_desc}, dynamic layout"
        elif distribucion_objetos == "disperso":
            dist_desc = f"repeated {motifs} motifs evenly spaced over {area_desc}, balanced composition"
        else:
            dist_desc = f"{motifs} motifs distributed across {area_desc}"
        
        # Descripción de colores
        num_colores = len(colores_objetos)
        if num_colores >= 2:
            if num_colores == 2:
                color_desc = f"with {colores_objetos[1]} {motifs}"
            else:
                color_desc = f"featuring {motifs} in {', '.join(colores_objetos[1:])} tones"
        else:
            color_desc = f"with vivid {motifs} elements"
        
        objects_desc = f"{dist_desc}, {color_desc}, rendered in {style}"
        
        design_desc = f"Mixed design: {solid_desc}, {objects_desc}, modern streetwear aesthetic."
        
        context = (
            "displayed on an invisible mannequin, perfect studio lighting, catalog style, "
            "sharp focus, plain light gray background, no logos, no text, "
            "hyper-detailed textile texture."
        )
        
        prompt = f"{garment}, {design_desc}, {context}"
        
        print("🟢 build_prompt_mixto_personalizado OK")
        print("🟢 Prompt generado:", prompt)
        return prompt
        
    except Exception as e:
        print("❌ Error en build_prompt_mixto_personalizado:", e)
        raise


def descripcion_mixto_personalizado_es(attr: Dict) -> str:
    """Descripción en español del diseño mixto personalizado"""
    tipo_chompa = attr.get("tipoChompa", "sudadera")
    capucha = attr.get("capucha", "si")
    area_diseno = attr.get("areaDisenoIA", "pecho_hombros")
    color_base_mixto = attr.get("colorBaseMixto", "")
    motifs = attr.get("motifs", "")
    colores_objetos = attr.get("coloresObjetos", [])
    estilo_objetos = attr.get("estiloObjetos", "")
    distribucion_objetos = attr.get("distribucionObjetos", "")
    genero = attr.get("genero", "unisex")
    
    # Traducciones
    color_base_es = TRADUCCIONES.get(color_base_mixto, color_base_mixto)
    motifs_es = TRADUCCIONES.get(motifs, motifs)
    estilo_es = TRADUCCIONES.get(estilo_objetos, estilo_objetos)
    dist_es = TRADUCCIONES.get(distribucion_objetos, distribucion_objetos)
    colores_obj_es = [TRADUCCIONES.get(c, c) for c in colores_objetos if c]
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
        f"estilo mixto con base {color_base_es.lower()} y diseño personalizado de {motifs_es} en {area_desc}"
    )
    
    if colores_obj_es:
        base += f" en tonos {', '.join([c.lower() for c in colores_obj_es])}"
    
    if estilo_es:
        base += f", estilo {estilo_es}"
    
    if dist_es:
        base += f" con distribución {dist_es}"
    
    return base + "."

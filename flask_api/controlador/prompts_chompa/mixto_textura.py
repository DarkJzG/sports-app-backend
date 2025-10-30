# flask_api/controlador/prompts_chompa/mixto_textura.py
from typing import Dict
from flask_api.componente.traducciones import TRADUCCIONES


def build_prompt_mixto_textura(attr: Dict) -> str:
    """Camino 3: Diseño mixto con textura personalizada IA"""
    print("🧥 Entrando a build_prompt_mixto_textura con:", attr)
    
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
        
        # Datos de la textura
        tipo_textura = attr.get("tipoTextura", "moteado")
        textura_personalizada = attr.get("texturaPersonalizada", "")
        colores_textura = attr.get("coloresTextura", [])
        
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
        
        # Descripción de la textura
        if tipo_textura == "personalizado" and textura_personalizada:
            texture_desc = textura_personalizada
        elif tipo_textura == "moteado":
            texture_desc = "speckled texture with subtle dots"
        elif tipo_textura == "lineas":
            texture_desc = "fine parallel lines pattern"
        elif tipo_textura == "circuitos":
            texture_desc = "circuit board inspired pattern"
        elif tipo_textura == "olas":
            texture_desc = "wave flow pattern with organic curves"
        elif tipo_textura == "flores":
            texture_desc = "floral pattern with botanical elements"
        else:
            texture_desc = "abstract texture pattern"
        
        # Descripción de colores
        num_colores = len(colores_textura)
        if num_colores == 2:
            color_desc = f"{colores_textura[0]} base with {colores_textura[1]} texture"
        elif num_colores >= 3:
            color_desc = f"{colores_textura[0]} base with texture in {', '.join(colores_textura[1:])} tones"
        else:
            color_desc = "multi-tone texture"
        
        texture_full_desc = f"{texture_desc} on {area_desc}, {color_desc}"
        
        design_desc = f"Mixed design: {solid_desc}, {texture_full_desc}, seamless integration."
        
        context = (
            "displayed on an invisible mannequin, perfect studio lighting, catalog style, "
            "sharp focus, plain light gray background, no logos, no text, "
            "hyper-detailed textile texture."
        )
        
        prompt = f"{garment}, {design_desc}, {context}"
        
        print("🟢 build_prompt_mixto_textura OK")
        print("🟢 Prompt generado:", prompt)
        return prompt
        
    except Exception as e:
        print("❌ Error en build_prompt_mixto_textura:", e)
        raise


def descripcion_mixto_textura_es(attr: Dict) -> str:
    """Descripción en español del diseño mixto con textura"""
    tipo_chompa = attr.get("tipoChompa", "sudadera")
    capucha = attr.get("capucha", "si")
    area_diseno = attr.get("areaDisenoIA", "pecho_hombros")
    color_base_mixto = attr.get("colorBaseMixto", "")
    tipo_textura = attr.get("tipoTextura", "")
    textura_personalizada = attr.get("texturaPersonalizada", "")
    colores_textura = attr.get("coloresTextura", [])
    genero = attr.get("genero", "unisex")
    
    # Traducciones
    color_base_es = TRADUCCIONES.get(color_base_mixto, color_base_mixto)
    tipo_tex_es = TRADUCCIONES.get(tipo_textura, tipo_textura)
    tex_pers_es = TRADUCCIONES.get(textura_personalizada, textura_personalizada)
    colores_tex_es = [TRADUCCIONES.get(c, c) for c in colores_textura if c]
    genero_es = TRADUCCIONES.get(genero, genero)
    
    if tipo_chompa == "sudadera":
        tipo_desc = "sudadera" if capucha == "si" else "buzo"
    else:
        tipo_desc = "chaqueta deportiva"
    
    if area_diseno == "pecho_hombros":
        area_desc = "pecho y hombros"
    else:
        area_desc = "cuerpo inferior"
    
    textura_desc = tex_pers_es if tipo_textura == "personalizado" and tex_pers_es else tipo_tex_es
    
    base = (
        f"{tipo_desc.capitalize()} deportiva para {genero_es.lower()} "
        f"estilo mixto con base {color_base_es.lower()} y textura {textura_desc} en {area_desc}"
    )
    
    if colores_tex_es:
        base += f" en tonos {', '.join([c.lower() for c in colores_tex_es])}"
    
    return base + "."

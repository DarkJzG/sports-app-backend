# flask_api/controlador/prompts_chompa/mixto_geometrico.py
from typing import Dict
from flask_api.componente.traducciones import TRADUCCIONES


def build_prompt_mixto_geometrico(attr: Dict) -> str:
    """Camino 3: Diseño mixto con patrón geométrico IA"""
    print("🧥 Entrando a build_prompt_mixto_geometrico con:", attr)
    
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
        
        # Datos del patrón geométrico
        figura_geometrica = attr.get("figuraGeometrica", "triangles")
        colores_geometrico = attr.get("coloresGeometrico", [])
        
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
        
        # Traducción de figura geométrica
        if figura_geometrica == "triangulos":
            shape = "triangles"
        elif figura_geometrica == "cuadrados":
            shape = "squares"
        elif figura_geometrica == "hexagonos":
            shape = "hexagons"
        else:
            shape = "geometric shapes"
        
        # Descripción de colores
        num_colores = len(colores_geometrico)
        if num_colores >= 3:
            color_desc = (
                f"base color {colores_geometrico[0]}, "
                f"primary {shape} in {colores_geometrico[1]}, "
                f"secondary accents in {colores_geometrico[2]}"
            )
            if num_colores >= 4:
                color_desc += f" and {colores_geometrico[3]}"
        else:
            color_desc = f"multi-color {shape} pattern"
        
        geometric_desc = (
            f"geometric pattern of {shape} on {area_desc}, "
            f"{color_desc}, tessellated design with sharp edges"
        )
        
        design_desc = f"Mixed design: {solid_desc}, {geometric_desc}, modern athletic style."
        
        context = (
            "displayed on an invisible mannequin, perfect studio lighting, catalog style, "
            "sharp focus, plain light gray background, no logos, no text, "
            "hyper-detailed textile texture."
        )
        
        prompt = f"{garment}, {design_desc}, {context}"
        
        print("🟢 build_prompt_mixto_geometrico OK")
        print("🟢 Prompt generado:", prompt)
        return prompt
        
    except Exception as e:
        print("❌ Error en build_prompt_mixto_geometrico:", e)
        raise


def descripcion_mixto_geometrico_es(attr: Dict) -> str:
    """Descripción en español del diseño mixto geométrico"""
    tipo_chompa = attr.get("tipoChompa", "sudadera")
    capucha = attr.get("capucha", "si")
    area_diseno = attr.get("areaDisenoIA", "pecho_hombros")
    color_base_mixto = attr.get("colorBaseMixto", "")
    figura_geometrica = attr.get("figuraGeometrica", "")
    colores_geometrico = attr.get("coloresGeometrico", [])
    genero = attr.get("genero", "unisex")
    
    # Traducciones
    color_base_es = TRADUCCIONES.get(color_base_mixto, color_base_mixto)
    figura_es = TRADUCCIONES.get(figura_geometrica, figura_geometrica)
    colores_geom_es = [TRADUCCIONES.get(c, c) for c in colores_geometrico if c]
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
        f"estilo mixto con base {color_base_es.lower()} y patrón geométrico de {figura_es} en {area_desc}"
    )
    
    if colores_geom_es:
        base += f" en tonos {', '.join([c.lower() for c in colores_geom_es[:3]])}"
    
    return base + "."

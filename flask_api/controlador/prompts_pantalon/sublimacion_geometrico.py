# flask_api/controlador/prompts_pantalon/sublimacion_geometrico.py
from typing import Dict
from flask_api.componente.traducciones import TRADUCCIONES


def build_prompt_sublimacion_geometrico(attr: Dict) -> str:
    """Camino 3: Diseño sublimado con patrón geométrico IA"""
    print("👖 Entrando a build_prompt_sublimacion_geometrico con:", attr)
    
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
        
        # Datos del patrón geométrico
        figura_geometrica = attr.get("figuraGeometrica", "triangles")
        colores_geometrico = attr.get("coloresGeometrico", [])
        
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
        
        # Traducción de figura geométrica
        if figura_geometrica == "triangles":
            shape = "triangles"
        elif figura_geometrica == "squares":
            shape = "squares"
        elif figura_geometrica == "diagonal_lines":
            shape = "diagonal lines"
        else:
            shape = "geometric shapes"
        
        # Descripción de colores
        num_colores = len(colores_geometrico)
        if num_colores >= 3:
            color_desc = (
                f"base color {colores_geometrico[0]}, "
                f"primary {shape} in {colores_geometrico[1]}, "
                f"with fragments in {colores_geometrico[2]}"
            )
            if num_colores >= 4:
                color_desc += f" and {colores_geometrico[3]}"
        else:
            color_desc = f"multi-color {shape} pattern"
        
        # Descripción según el área de diseño
        if area_diseno == "complete":
            geometric_desc = (
                f"Full sublimation print with geometric pattern of {shape} covering the entire pants, "
                f"{color_desc}, tessellated design creating dynamic visual effect across both legs."
            )
            design_desc = geometric_desc
        else:  # paneles_laterales
            geometric_desc = (
                f"wide vertical panels on outer legs with geometric pattern of {shape}, "
                f"{color_desc}, tessellated sublimation design"
            )
            solid_desc = f"{color_base_mixto} solid color on front, back, and inner legs"
            design_desc = f"Mixed design: {solid_desc}, {geometric_desc}, modern athletic style."
        
        # Contexto visual
        context = (
            "displayed on an invisible mannequin or flat lay, perfect studio lighting, catalog style, "
            "sharp focus, plain light gray background, no logos, no text, "
            "hyper-detailed sublimation print texture."
        )
        
        prompt = f"{garment}, {design_desc}, {context}"
        
        print("🟢 build_prompt_sublimacion_geometrico OK")
        print("🟢 Prompt generado:", prompt)
        return prompt
        
    except Exception as e:
        print("❌ Error en build_prompt_sublimacion_geometrico:", e)
        raise


def descripcion_sublimacion_geometrico_es(attr: Dict) -> str:
    """Descripción en español del diseño sublimado geométrico"""
    tipo_corte = attr.get("tipoCorte", "jogger")
    area_diseno = attr.get("areaDisenoIA", "completo")
    color_base_mixto = attr.get("colorBaseMixto", "")
    figura_geometrica = attr.get("figuraGeometrica", "")
    colores_geometrico = attr.get("coloresGeometrico", [])
    genero = attr.get("genero", "unisex")
    
    # Traducciones
    figura_es = TRADUCCIONES.get(figura_geometrica, figura_geometrica)
    colores_geom_es = [TRADUCCIONES.get(c, c) for c in colores_geometrico if c]
    genero_es = TRADUCCIONES.get(genero, genero)
    
    if tipo_corte == "joggers":
        corte_desc = "joggers"
    else:
        corte_desc = "corte recto"
    
    if area_diseno == "complete":
        area_desc = f"sublimación completa con patrón geométrico de {figura_es}"
    else:
        color_base_es = TRADUCCIONES.get(color_base_mixto, color_base_mixto)
        area_desc = f"base {color_base_es.lower()} con paneles laterales sublimados con patrón geométrico de {figura_es}"
    
    base = (
        f"Pantalón deportivo {corte_desc} para {genero_es.lower()} "
        f"con {area_desc}"
    )
    
    if colores_geom_es:
        base += f" en tonos {', '.join([c.lower() for c in colores_geom_es[:3]])}"
    
    return base + "."

# flask_api/controlador/prompts_chompa/mixto_degradado.py
from typing import Dict
from flask_api.componente.traducciones import TRADUCCIONES


def build_prompt_mixto_degradado(attr: Dict) -> str:
    """
    Camino 3: Diseño mixto con degradado IA
    """
    print("🧥 Entrando a build_prompt_mixto_degradado con:", attr)
    
    try:
        # Datos estructurales
        tipo_chompa = attr.get("tipoChompa", "hoodie")
        capucha = attr.get("capucha", "Yeah")               # "Yeah" | "No"
        bolsillos = attr.get("bolsillos", "kangaroo")
        tela = attr.get("tela", "polyester")
        genero = attr.get("genero", "unisex")
        
        # Datos del diseño mixto
        area_diseno = attr.get("areaDisenoIA", "pecho_hombros")
        color_base_mixto = attr.get("colorBaseMixto", "black")
        
        # Datos del degradado
        colores_gradiente = attr.get("coloresGradiente", [])
        tipo_gradiente = attr.get("tipoGradiente", "linear")
        num_colores = len(colores_gradiente)
        
        # === Tipo de prenda y capucha/cuello ===
        if tipo_chompa == "jacket":
            if capucha == "Yeah":
                garment_type = "zip-up sports jacket with hood"
                hood_desc = "with hood"
                has_hood = True
            else:
                garment_type = "zip-up sports jacket with high collar, no hood"
                hood_desc = "with high collar, without hood"
                has_hood = False
        else:
            if capucha == "Yeah":
                garment_type = "pullover hoodie"
                hood_desc = "with hood"
                has_hood = True
            else:
                garment_type = "pullover sweatshirt with high collar"
                hood_desc = "with high collar, without hood"
                has_hood = False
        
        # === Bolsillos ===
        if bolsillos == "kangaroo":
            pocket_desc = "with kangaroo pocket"
        elif bolsillos in ["laterales", "sides"]:
            pocket_desc = "with side pockets"
        else:
            pocket_desc = "without pockets"
        
        garment = (
            f"high-end photorealistic sportswear {garment_type} mockup for {genero}, "
            f"{hood_desc}, {pocket_desc}, made of {tela} fabric"
        )
        
        # === Descripción del área de diseño ===
        if area_diseno == "pecho_hombros" or area_diseno == "chest_shoulders":
            if has_hood:
                area_desc = "chest, shoulders and hood area"
            else:
                area_desc = "chest and shoulders area, no hood"
            solid_desc = f"{color_base_mixto} solid color on lower body, sleeves and back"
        else:  # cuerpo_inferior / lower_body
            area_desc = "lower body"
            solid_desc = f"{color_base_mixto} solid color on shoulders, upper chest and sleeves"
        
        # === Descripción del degradado según número de colores ===
        if num_colores == 2:
            gradient_desc = (
                f"{tipo_gradiente} gradient pattern on {area_desc}, "
                f"smoothly transitioning from {colores_gradiente[0]} to {colores_gradiente[1]}"
            )
        elif num_colores == 3:
            gradient_desc = (
                f"{tipo_gradiente} gradient pattern on {area_desc}, "
                f"flowing from {colores_gradiente[0]} through {colores_gradiente[1]} "
                f"to {colores_gradiente[2]}"
            )
        elif num_colores >= 4:
            gradient_desc = (
                f"multi-step {tipo_gradiente} gradient on {area_desc}, "
                f"blending {', '.join(colores_gradiente[:4])}"
            )
        else:
            gradient_desc = f"multi-color {tipo_gradiente} gradient on {area_desc}"
        
        design_desc = (
            f"Mixed design: {solid_desc}, {gradient_desc}, "
            "seamless transition between solid and gradient areas."
        )
        
        # Refuerzo si no hay capucha
        if not has_hood:
            design_desc += " This design must NOT include any hood or hood shapes, only a high collar. "
        
        # Contexto visual
        context = (
            "displayed on an invisible mannequin, perfect studio lighting, catalog style, "
            "sharp focus, plain light gray background, no logos, no text, "
            "hyper-detailed textile texture, modern Windrunner style."
        )
        
        prompt = f"{garment}, {design_desc}, {context}"
        
        print("🟢 build_prompt_mixto_degradado OK")
        print("🟢 Prompt generado:", prompt)
        return prompt
        
    except Exception as e:
        print("❌ Error en build_prompt_mixto_degradado:", e)
        raise



def descripcion_mixto_degradado_es(attr: Dict) -> str:
    """Descripción en español del diseño mixto con degradado"""
    tipo_chompa = attr.get("tipoChompa", "sudadera")
    capucha = attr.get("capucha", "si")
    area_diseno = attr.get("areaDisenoIA", "pecho_hombros")
    color_base_mixto = attr.get("colorBaseMixto", "")
    colores_gradiente = attr.get("coloresGradiente", [])
    tipo_gradiente = attr.get("tipoGradiente", "linear")
    genero = attr.get("genero", "unisex")
    
    # Traducciones
    color_base_es = TRADUCCIONES.get(color_base_mixto, color_base_mixto)
    colores_grad_es = [TRADUCCIONES.get(c, c) for c in colores_gradiente if c]
    tipo_grad_es = TRADUCCIONES.get(tipo_gradiente, tipo_gradiente)
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
        f"estilo mixto con base {color_base_es.lower()} y degradado {tipo_grad_es} en {area_desc}"
    )
    
    if colores_grad_es:
        if len(colores_grad_es) == 2:
            base += f" en tonos {colores_grad_es[0].lower()} y {colores_grad_es[1].lower()}"
        elif len(colores_grad_es) >= 3:
            base += f" en tonos {', '.join([c.lower() for c in colores_grad_es])}"
    
    return base + "."

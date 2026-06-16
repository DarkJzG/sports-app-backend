# flask_api/controlador/prompts_chompa/bloques_color.py
from typing import Dict
from flask_api.componente.traducciones import TRADUCCIONES


def build_prompt_bloques_color(attr: Dict) -> str:
    """
    Camino 2: Chompa con bloques de color (corte y costura)
    """
    print("🧥 Entrando a build_prompt_bloques_color con:", attr)
    
    try:
        # Datos estructurales
        tipo_chompa = attr.get("tipoChompa", "jacket")
        capucha = attr.get("capucha", "Yeah")               # "Yeah" | "No"
        bolsillos = attr.get("bolsillos", "kangaroo")
        tela = attr.get("tela", "polyester")
        genero = attr.get("genero", "unisex")
        
        # Tipo de bloque
        tipo_bloque = attr.get("tipoBloque", "horizontal")
        colores_bloque = attr.get("coloresBloque", [])
        
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
        
        # Bolsillos
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
        
        # === Descripción según el tipo de bloque ===
        if tipo_bloque == "horizontal":
            color1 = colores_bloque[0] if len(colores_bloque) > 0 else "white"
            color2 = colores_bloque[1] if len(colores_bloque) > 1 else "black"
            
            design_desc = (
                "Color block design with horizontal split: "
                f"upper section (chest, shoulders, upper sleeves) in {color1}, "
                f"lower section (abdomen, lower sleeves, waist) in {color2}, "
                "clean seam line dividing the two color blocks horizontally across the torso."
            )
        
        elif tipo_bloque == "chevron":
            color1 = colores_bloque[0] if len(colores_bloque) > 0 else "navy blue"
            color2 = colores_bloque[1] if len(colores_bloque) > 1 else "white"
            
            design_desc = (
                "Chevron V-shaped color block design: "
                f"{color1} V-panel on chest extending from shoulders to center chest, "
                f"{color2} covering the rest of the body, sleeves and back, "
                "bold diagonal seams creating dynamic V-shape across front."
            )
        
        elif tipo_bloque == "panels":
            color1 = colores_bloque[0] if len(colores_bloque) > 0 else "black"
            color2 = colores_bloque[1] if len(colores_bloque) > 1 else "white"
            color3 = colores_bloque[2] if len(colores_bloque) > 2 else "gray"
            
            design_desc = (
                "Multi-panel color block design: "
                f"{color1} shoulder and upper chest panels, "
                f"{color2} main body panel (center torso and back), "
                f"{color3} sleeve panels, "
                "visible stitching lines emphasizing the panel construction."
            )
        else:
            design_desc = "color block design with multiple fabric panels"
        
        # Refuerzo si no hay capucha
        if not has_hood:
            design_desc += " This design must NOT include any hood or hood shapes, only a high collar. "
        
        # Contexto visual
        context = (
            "displayed on an invisible mannequin, perfect studio lighting, catalog style, "
            "sharp focus, plain light gray background, no logos, no text, "
            "hyper-detailed textile texture, modern athletic design."
        )
        
        prompt = f"{garment}, {design_desc}, {context}"
        
        print("🟢 build_prompt_bloques_color OK")
        print("🟢 Prompt generado:", prompt)
        return prompt
        
    except Exception as e:
        print("❌ Error en build_prompt_bloques_color:", e)
        raise



def descripcion_bloques_color_es(attr: Dict) -> str:
    """Descripción en español del diseño por bloques"""
    tipo_chompa = attr.get("tipoChompa", "sudadera")
    capucha = attr.get("capucha", "Yeah")
    tipo_bloque = attr.get("tipoBloque", "horizontal")
    colores_bloque = attr.get("coloresBloque", [])
    genero = attr.get("genero", "unisex")
    
    print("🟢 Entrando a descripcion_bloques_color_es con:", attr)
    # Traducciones
    colores_es = [TRADUCCIONES.get(c, c) for c in colores_bloque if c]
    genero_es = TRADUCCIONES.get(genero, genero)
    
    if tipo_chompa == "sudadera":
        tipo_desc = "sudadera" if capucha == "si" else "buzo"
    else:
        tipo_desc = "chaqueta deportiva"
    
    if tipo_bloque == "horizontal":
        bloque_desc = "diseño de bloques horizontales"
    elif tipo_bloque == "chevron":
        bloque_desc = "diseño chevron en V"
    elif tipo_bloque == "paneles":
        bloque_desc = "diseño de paneles deportivos"
    else:
        bloque_desc = "diseño de bloques de color"
    
    if capucha == "Sí":
        capucha_desc = "con capucha"
    elif capucha == "No":
        capucha_desc = "sin capucha"
    
    base = (
        f"{tipo_desc.capitalize()} {capucha_desc} para {genero_es.lower()} "
        f"con {bloque_desc}"
    )
    
    if colores_es:
        if len(colores_es) == 2:
            base += f" en colores {colores_es[0].lower()} y {colores_es[1].lower()}"
        elif len(colores_es) >= 3:
            base += f" en colores {colores_es[0].lower()}, {colores_es[1].lower()} y {colores_es[2].lower()}"

    print("🟢 Descripción generada exitosamente")
    return base + "."

    


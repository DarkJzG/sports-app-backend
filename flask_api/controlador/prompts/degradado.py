# flask_api/controlador/prompts/degradado.py
from typing import Dict
from flask_api.componente.traducciones import TRADUCCIONES

def build_prompt_degradado(attr: Dict) -> str:
    print("🧩 Entrando a build_prompt_degradado con:", attr)
    
    try:
        tipo = attr.get("tipoGradiente", "linear").lower()
        colores = attr.get("colores", [])
        num_colores = len(colores)

        # ===============================
        # 🧩 1) Base descriptiva de prenda
        # ===============================
        genero = attr.get("genero", "")
        cuello = attr.get("cuello", "")
        manga = attr.get("manga", "")
        tela = attr.get("tela", "")
        garment = f"high-end photorealistic sportswear t-shirt mockup for {genero}, with {cuello} neck and {manga} sleeves, made of {tela} fabric"

        # ===============================
        # 🧩 2) Construcción por número de colores
        # ===============================
        if num_colores == 2:
            grad_desc = f" The main body features a full gradient pattern. The gradient is a smooth {tipo} transition from {colores[0]} to {colores[1]}"
        elif num_colores == 3:
            grad_desc = f" The main body features a full gradient pattern. The gradient is a multi-stop {tipo} type, smoothly blending: {colores[0]} (base) → {colores[1]} → {colores[2]} (accent)"
        elif num_colores >= 4:
            grad_desc = f" The gradient is a multi-stop {tipo} type, smoothly blending: {colores[0]} (base) → {colores[1]} → {colores[2]} → {colores[3]} (accent)"
        else:
            grad_desc = f" The gradient is a multi-stop {tipo} type, smoothly blending: {colores[0]} (base) → {colores[1]} → {colores[2]} → {colores[3]} → {colores[4]} (accent)"

        # ===============================
    # 🧩 3) Contexto visual base
        # ===============================
        context = (
            "displayed on an invisible mannequin,"
            "perfect studio lighting, catalog style,"
            "sharp focus, plain light gray background,"
            "no logos, no text, hyper-detailed textile texture."
        )

        # ===============================
        # 🧩 4) Prompt final
        # ===============================
        prompt = f"{garment}, {grad_desc}, {context}"

        print("🟣 build_prompt_degradado: OK")
        print("🟣 Prompt generado:", prompt)
        return prompt
    except Exception as e:
        print("❌ Error dentro de build_prompt_degradado:", e)
        raise

def descripcion_degradado_es(attr: Dict) -> str:
    num_colores = len(attr.get("colores", []))
    colores = [c for c in attr.get("colores", []) if isinstance(c, str) and c.strip()]

    tipo = attr.get("tipoGradiente", "linear")
    genero = attr.get("genero", "unisex")

    
    colores_es = [TRADUCCIONES.get(c, c) for c in colores]
    tipo_es = TRADUCCIONES.get(tipo, tipo)
    genero_es = TRADUCCIONES.get(genero, genero)
    base = f"Camiseta deportiva para {genero_es} con patron degradado {tipo_es} "

    if num_colores == 2:
        base += f" con colores {colores_es[0]} y {colores_es[1]}"
    elif num_colores == 3:
        base += f" con colores {colores_es[0]}, {colores_es[1]} y {colores_es[2]}"
    elif num_colores >= 4:
        base += f" con colores {colores_es[0]}, {colores_es[1]}, {colores_es[2]} y {colores_es[3]}"
    else:
        base += f" con colores {colores_es[0]}, {colores_es[1]}, {colores_es[2]}, {colores_es[3]} y {colores_es[4]}"

    return base + "."
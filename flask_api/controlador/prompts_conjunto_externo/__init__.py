# flask_api/controlador/prompts_conjunto_externo/__init__.py
from .solido_coordinado import build_prompt_solido_coordinado_chaqueta, build_prompt_solido_coordinado_pantalon, descripcion_solido_coordinado_es
from .bloques_coordinados import build_prompt_bloques_coordinados_chaqueta, build_prompt_bloques_coordinados_pantalon, descripcion_bloques_coordinados_es
from .sublimado_degradado import build_prompt_sublimado_degradado_chaqueta, build_prompt_sublimado_degradado_pantalon, descripcion_sublimado_degradado_es
from .sublimado_artistico import build_prompt_sublimado_artistico_chaqueta, build_prompt_sublimado_artistico_pantalon, descripcion_sublimado_artistico_es


def build_prompts_conjunto_externo_v1(attr: dict) -> tuple:
    """
    Genera AMBOS prompts (chaqueta y pantalón) según el camino seleccionado.
    Retorna: (prompt_chaqueta, prompt_pantalon)
    """
    camino = attr.get("caminoSeleccionado", "solid_coordinated")
    
    if camino == "solid_coordinated":
        prompt_chaqueta = build_prompt_solido_coordinado_chaqueta(attr)
        prompt_pantalon = build_prompt_solido_coordinado_pantalon(attr)
        return (prompt_chaqueta, prompt_pantalon)
    
    elif camino == "bloques_coordinated":
        prompt_chaqueta = build_prompt_bloques_coordinados_chaqueta(attr)
        prompt_pantalon = build_prompt_bloques_coordinados_pantalon(attr)
        return (prompt_chaqueta, prompt_pantalon)
    
    elif camino == "sublimado_ia":
        tipo_diseno = attr.get("tipoDisenoIA", "degradado")
        
        if tipo_diseno == "degradado":
            prompt_chaqueta = build_prompt_sublimado_degradado_chaqueta(attr)
            prompt_pantalon = build_prompt_sublimado_degradado_pantalon(attr)
        elif tipo_diseno == "artistico":
            prompt_chaqueta = build_prompt_sublimado_artistico_chaqueta(attr)
            prompt_pantalon = build_prompt_sublimado_artistico_pantalon(attr)
        else:
            # Fallback
            prompt_chaqueta = build_prompt_solido_coordinado_chaqueta(attr)
            prompt_pantalon = build_prompt_solido_coordinado_pantalon(attr)
        
        return (prompt_chaqueta, prompt_pantalon)
    
    else:
        # Fallback default
        prompt_chaqueta = build_prompt_solido_coordinado_chaqueta(attr)
        prompt_pantalon = build_prompt_solido_coordinado_pantalon(attr)
        return (prompt_chaqueta, prompt_pantalon)


def descripcion_conjunto_externo_es_v1(attr: dict) -> str:
    """
    Genera la descripción en español del conjunto completo
    """
    camino = attr.get("caminoSeleccionado", "solid_coordinated")
    
    if camino == "solid_coordinated":
        return descripcion_solido_coordinado_es(attr)
    elif camino == "bloques_coordinated":
        return descripcion_bloques_coordinados_es(attr)
    elif camino == "sublimado_ia":
        tipo_diseno = attr.get("tipoDisenoIA", "degradado")
        if tipo_diseno == "degradado":
            return descripcion_sublimado_degradado_es(attr)
        elif tipo_diseno == "artistico":
            return descripcion_sublimado_artistico_es(attr)
    
    return "Conjunto deportivo externo coordinado."

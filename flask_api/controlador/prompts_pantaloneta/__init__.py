# flask_api/controlador/prompts_pantaloneta/__init__.py
from .solido_acentos import build_prompt_solido_acentos, descripcion_solido_acentos_es
from .paneles_rayas import build_prompt_paneles_rayas, descripcion_paneles_rayas_es
from .sublimacion_degradado import build_prompt_sublimacion_degradado, descripcion_sublimacion_degradado_es
from .sublimacion_artistico import build_prompt_sublimacion_artistico, descripcion_sublimacion_artistico_es


def build_prompt_pantaloneta_v1(attr: dict) -> str:
    """
    Genera el prompt según el camino seleccionado:
    - solido: Sólido con acentos
    - paneles: Paneles y rayas
    - sublimacion: Diseño sublimado IA (degradado o artístico)
    """
    camino = attr.get("caminoSeleccionado", "solid")
    
    if camino == "solid":
        return build_prompt_solido_acentos(attr)
    elif camino == "panels":
        return build_prompt_paneles_rayas(attr)
    elif camino == "sublimation":
        tipo_diseno = attr.get("tipoDisenoIA", "degrade")
        mapping = {
            "degraded": build_prompt_sublimacion_degradado,
            "artistic": build_prompt_sublimacion_artistico,
        }
        builder = mapping.get(tipo_diseno, build_prompt_sublimacion_degradado)
        return builder(attr)
    else:
        return build_prompt_solido_acentos(attr)


def descripcion_pantaloneta_es_v1(attr: dict) -> str:
    """
    Genera la descripción en español según el camino seleccionado
    """
    camino = attr.get("caminoSeleccionado", "solid")
    
    if camino == "solid":
        return descripcion_solido_acentos_es(attr)
    elif camino == "panels":
        return descripcion_paneles_rayas_es(attr)
    elif camino == "sublimation":
        tipo_diseno = attr.get("tipoDisenoIA", "degraded")
        mapping = {
            "degraded": descripcion_sublimacion_degradado_es,
            "artistic": descripcion_sublimacion_artistico_es,
        }
        builder = mapping.get(tipo_diseno, descripcion_sublimacion_degradado_es)
        return builder(attr)
    else:
        return descripcion_solido_acentos_es(attr)
